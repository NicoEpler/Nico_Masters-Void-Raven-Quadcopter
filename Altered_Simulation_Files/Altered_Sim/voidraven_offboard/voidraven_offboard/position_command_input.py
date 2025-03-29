#!/usr/bin/env python3
import sys
import threading
import time
import io
import os

import geometry_msgs.msg
import rclpy
from rclpy.node import Node
import std_msgs.msg
from px4_msgs.msg import VehicleStatus, VehicleOdometry

from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSHistoryPolicy,
    QoSDurabilityPolicy
)

# Platform-specific imports for capturing keypresses
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty


msg = """
This node takes keypresses from the keyboard and publishes them
as position setpoints.

Using the arrow keys and WASD, you can increment the position setpoint in X, Y, Z, and yaw:

  W: Increase Z
  S: Decrease Z
  A: Decrease Yaw
  D: Increase Yaw
  Up Arrow:    Increase Y
  Down Arrow:  Decrease Y
  Left Arrow:  Decrease X
  Right Arrow: Increase X

Press SPACE to arm/disarm the drone.
Press CTRL-C to exit.
"""

# Keys mapped to increments in (x, y, z, yaw)
moveBindings = {
    'w': (0, 0, 1, 0),
    's': (0, 0, -1, 0),
    'a': (0, 0, 0, -1),
    'd': (0, 0, 0, 1),
    '\x1b[A': (0, 1, 0, 0),  # Up Arrow
    '\x1b[B': (0, -1, 0, 0),  # Down Arrow
    '\x1b[C': (-1, 0, 0, 0),  # Right Arrow
    '\x1b[D': (1, 0, 0, 0),  # Left Arrow
}


def saveTerminalSettings():
    """Save terminal settings so we can restore them after capture."""
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    """Restore the saved terminal settings."""
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def getKey(old_settings):
    """Capture a single keypress from stdin."""
    if sys.platform == 'win32':
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        # Check for escape sequence (arrow keys)
        if key == '\x1b':
            key += sys.stdin.read(2)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    return key


class TeleopPositionKeyboard(Node):
    def __init__(self):
        super().__init__('teleop_position_keyboard')

        # Create a print lock to synchronize print statements
        self.print_lock = threading.Lock()

        self.qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Publisher for position commands (still using Twist, but treated as position setpoints)
        self.position_pub = self.create_publisher(
            geometry_msgs.msg.Twist, '/offboard_position_cmd', self.qos_profile)

        # Publisher for arming toggle
        self.arm_pub = self.create_publisher(
            std_msgs.msg.Bool, '/arm_message', self.qos_profile)

        # Increment steps for position and yaw
        self.position_step = 0.1
        self.yaw_step = 0.2

        # Current position setpoints
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.z_pos = 0.0
        self.yaw_pos = 0.0

        self.arm_toggle = False
        
        # Status monitoring variables
        self.monitoring_active = False
        self.monitoring_thread = None
        self.nav_state = 0
        
        # Current vehicle position from odometry
        self.vehicle_x = 0.0
        self.vehicle_y = 0.0
        self.vehicle_z = 0.0
        
        # Subscription objects (will be created when needed)
        self.status_sub = None
        self.odometry_sub = None
        
        # Counter for status updates (to reduce print frequency)
        self.status_update_count = 0

    def safe_print(self, message):
        """Thread-safe print function"""
        with self.print_lock:
            # Clear the current line
            print('\r' + ' ' * 80, end='\r')
            print(message, flush=True)

    def start_monitoring(self):
        """Start monitoring vehicle status and odometry"""
        self.safe_print("Starting vehicle status and odometry monitoring...")
        
        # Create subscriptions
        self.status_sub = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.vehicle_status_callback,
            self.qos_profile)
        
        self.odometry_sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odometry_callback,
            self.qos_profile)
            
        self.monitoring_active = True
        self.status_update_count = 0
        
        # Start a thread to process callbacks
        self.monitoring_thread = threading.Thread(target=self.monitoring_spin)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    # def stop_monitoring(self):
    #     """Stop monitoring vehicle status and odometry"""
    #     if not self.monitoring_active:
    #         return
            
    #     self.safe_print("Stopping vehicle status and odometry monitoring")
        
    #     # Destroy subscriptions
    #     self.destroy_subscription(self.status_sub)
    #     self.destroy_subscription(self.odometry_sub)
        
    #     self.status_sub = None
    #     self.odometry_sub = None
    #     self.monitoring_active = False
        
    #     # Wait for monitoring thread to finish
    #     if self.monitoring_thread:
    #         self.monitoring_thread.join(timeout=1.0)
    #         self.monitoring_thread = None
            
    def stop_monitoring(self):
        """Stop monitoring vehicle status and odometry"""
        if not self.monitoring_active:
            return
            
        self.safe_print("Stopping vehicle status and odometry monitoring")
        
        # Destroy subscriptions
        self.destroy_subscription(self.status_sub)
        self.destroy_subscription(self.odometry_sub)
        
        self.status_sub = None
        self.odometry_sub = None
        self.monitoring_active = False
        
        # Only attempt to join the thread if we're not IN that thread
        current_thread = threading.current_thread()
        if self.monitoring_thread and self.monitoring_thread is not current_thread:
            self.monitoring_thread.join(timeout=1.0)
            self.monitoring_thread = None

    def monitoring_spin(self):
        """Process callbacks in a separate thread"""
        while self.monitoring_active and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
            
            # Check if we've reached the target nav_state (14)
            if self.nav_state == 14:
                # self.safe_print("Vehicle entered OFFBOARD mode (nav_state=14)")
                # self.safe_print(f"Setting position to current vehicle position: X={self.vehicle_x:.2f}, Y={self.vehicle_y:.2f}, Z={self.vehicle_z:.2f}")
                
                # Update setpoints to current position
                self.x_pos = float(-self.vehicle_x)
                self.y_pos = float(self.vehicle_y)
                self.z_pos = float(-self.vehicle_z)
                
                # Publish the updated setpoint
                self.publish_position()
                self.stop_monitoring()
                
                # Stop monitoring
                # self.monitoring_active = False
                break

    def vehicle_status_callback(self, msg):
        """Callback for vehicle status messages"""
        self.nav_state = msg.nav_state
        
        # Only print status updates occasionally to avoid flooding
        self.status_update_count += 1
        if self.status_update_count % 10 == 0:
            self.safe_print(f"Current nav_state: {self.nav_state}")

    def odometry_callback(self, msg):
        """Callback for vehicle odometry messages"""
        # Store the current vehicle position
        self.vehicle_y = float(msg.position[0])
        self.vehicle_x = float(msg.position[1])
        self.vehicle_z = float(msg.position[2])

    def publish_position(self):
        """Publish the current position setpoint"""
        position_msg = geometry_msgs.msg.Twist()
        position_msg.linear.x = float(self.x_pos)
        position_msg.linear.y = float(self.y_pos)
        position_msg.linear.z = float(self.z_pos)
        position_msg.angular.z = float(self.yaw_pos)
        self.position_pub.publish(position_msg)
        
        self.safe_print(
            f"X: {position_msg.linear.x:.2f}, "
            f"Y: {position_msg.linear.y:.2f}, "
            f"Z: {position_msg.linear.z:.2f}, "
            f"Yaw: {position_msg.angular.z:.2f}"
        )

    def run(self):
        """Main run loop for keyboard control"""
        settings = saveTerminalSettings()
        self.safe_print(msg)
        
        try:
            while rclpy.ok():
                key = getKey(settings)

                if key in moveBindings:
                    x_inc, y_inc, z_inc, yaw_inc = moveBindings[key]
                    self.x_pos += x_inc * self.position_step
                    self.y_pos += y_inc * self.position_step
                    self.z_pos += z_inc * self.position_step
                    self.yaw_pos += yaw_inc * self.yaw_step
                else:
                    # If it's not a recognized key, stop only if it's CTRL-C
                    if key == '\x03':  # CTRL-C
                        break

                if key == ' ':  # Space bar toggles arming
                    self.arm_toggle = not self.arm_toggle
                    arm_msg = std_msgs.msg.Bool()
                    arm_msg.data = self.arm_toggle
                    self.arm_pub.publish(arm_msg)
                    self.safe_print(f"Arm toggle is now: {self.arm_toggle}")
                    self.start_monitoring()
                    # Start monitoring when armed
                    # if self.arm_toggle:
                    #     self.start_monitoring()
                    # else:
                    #     self.stop_monitoring()

                # Publish the position setpoint
                self.publish_position()

        except Exception as e:
            self.safe_print(f"Error: {e}")

        finally:
            # Stop monitoring on exit
            self.stop_monitoring()
            restoreTerminalSettings(settings)


def main():
    rclpy.init()
    node = TeleopPositionKeyboard()
    
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    
    # Clean up
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()