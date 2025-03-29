#!/usr/bin/env python3

import sys
import rclpy
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSHistoryPolicy,
    QoSDurabilityPolicy,
)
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool

# OS-specific imports for keyboard handling
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

init_msg = """
This node converts keypresses to updated setpoint positions
published to the /offboard_position_cmd topic in geometry_msgs/Twist format.
Following buttons have functions:

W:              Increase Z by 0.1m
S:              Decrease Z by 0.1m
Up Arrow:       Increase Y by 0.1m
Down Arrow:     Decrease Y by 0.1m
Left Arrow:     Increase X by 0.1m
Right Arrow :   Decrease X by 0.1m
A:              Decrease Yaw by 0.1 rad
D:              Increase Yaw by 0.1 rad

Space:          Arm and Takeoff or Disarm the drone
Ctrl-C:         Exit the node

"""

# Key mappings: (x_increment, y_increment, z_increment, yaw_increment)
moveBindings = {
    'w': (0.0,  0.0,  0.1,  0.0),  # Increase Z
    's': (0.0,  0.0, -0.1,  0.0),  # Decrease Z
    'a': (0.0,  0.0,  0.0, -0.1),  # Decrease Yaw
    'd': (0.0,  0.0,  0.0,  0.1),  # Increase Yaw

    '\x1b[A': (0.0,  0.1,  0.0,  0.0),   # Up Arrow -> Increase Y
    '\x1b[B': (0.0, -0.1,  0.0,  0.0),   # Down Arrow -> Decrease Y
    '\x1b[C': (-0.1, 0.0,  0.0,  0.0),   # Right Arrow -> Decrease X
    '\x1b[D': (0.1,  0.0,  0.0,  0.0),   # Left Arrow -> Increase X
}

# We'll store the latest Twist received from /offboard_position_cmd here
current_position = Twist()

def getKey(old_settings):
    """Read a single keypress from stdin (with arrow key support on Linux)."""
    if sys.platform == 'win32':
        return msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        # If the first character is ESC, we may be dealing with an arrow key
        if key == '\x1b':
            additional_chars = sys.stdin.read(2)
            key += additional_chars
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return key

def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)

def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def offboard_position_cmd_callback(msg):
    """
    Callback for the /offboard_position_cmd subscription.
    Stores the latest position command into current_position.
    """
    global current_position
    current_position = msg


def main():
    old_settings = saveTerminalSettings()
    rclpy.init()

    node = rclpy.create_node('teleop_position_keyboard')

    # Set up QoS (can be adjusted as needed)
    qos_profile = QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=10
    )

    # Publisher for updated position commands
    pub = node.create_publisher(Twist, '/offboard_position_cmd', qos_profile)

    # Subscription to read the latest position commands (in case anything else updates them)
    sub = node.create_subscription(
        Twist,
        '/offboard_position_cmd',
        offboard_position_cmd_callback,
        qos_profile
    )

    # Arm/Disarm publisher
    arm_pub = node.create_publisher(Bool, '/arm_message', qos_profile)
    arm_toggle = False

    # Print usage instructions
    print(__doc__)

    # Print the initial setpoint
    print(init_msg)
    print(
        f"X: {current_position.linear.x:.2f}    "
        f"Y: {current_position.linear.y:.2f}    "
        f"Z: {current_position.linear.z:.2f}    "
        f"Yaw: {current_position.angular.z:.2f} "
    )

    try:
        while True:
            # Let ROS process subscription callbacks to update current_position
            rclpy.spin_once(node, timeout_sec=0.05)

            key = getKey(old_settings)
            if key in moveBindings:
                x_inc, y_inc, z_inc, yaw_inc = moveBindings[key]

                # Update the local stored current_position immediately
                current_position.linear.x  += x_inc
                current_position.linear.y  += y_inc
                current_position.linear.z  += z_inc
                current_position.angular.z += yaw_inc

                # Publish updated position
                pub.publish(current_position)

                # Print the updated position
                print(
                    f"X: {current_position.linear.x:.2f}    "
                    f"Y: {current_position.linear.y:.2f}    "
                    f"Z: {current_position.linear.z:.2f}    "
                    f"Yaw: {current_position.angular.z:.2f} "
                )

            elif key == ' ':
                # Space: Toggle arm
                arm_toggle = not arm_toggle
                arm_msg = Bool()
                arm_msg.data = arm_toggle
                arm_pub.publish(arm_msg)
                print(f"Arm toggle is now: {arm_toggle}")

            else:
                # If it's Ctrl-C, exit the loop
                if key == '\x03':
                    break

    except Exception as e:
        print(e)

    finally:
        # On exit, publish a final "neutral" message if desired
        current_position.linear.x = 0.0
        current_position.linear.y = 0.0
        current_position.linear.z = 0.0
        current_position.angular.x = 0.0
        current_position.angular.y = 0.0
        current_position.angular.z = 0.0
        pub.publish(current_position)
        print("Shutting down... Published final neutral setpoint.")

        restoreTerminalSettings(old_settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
