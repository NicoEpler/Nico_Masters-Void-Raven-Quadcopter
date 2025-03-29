#!/usr/bin/env python3
import sys

import geometry_msgs.msg
import rclpy
import std_msgs.msg

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
    '\x1b[B': (0, -1, 0, 0), # Down Arrow
    '\x1b[C': (-1, 0, 0, 0), # Right Arrow
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


def main():
    settings = saveTerminalSettings()
    rclpy.init()

    node = rclpy.create_node('teleop_position_keyboard')

    qos_profile = QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=10
    )

    # Publisher for position commands (still using Twist, but treated as position setpoints)
    position_pub = node.create_publisher(geometry_msgs.msg.Twist, '/offboard_position_cmd', qos_profile)

    # Publisher for arming toggle
    arm_pub = node.create_publisher(std_msgs.msg.Bool, '/arm_message', qos_profile)

    # Increment steps for position and yaw
    position_step = 0.1
    yaw_step = 0.2

    # Current position setpoints
    x_pos = 0.0
    y_pos = 0.0
    z_pos = 0.0
    yaw_pos = 0.0

    arm_toggle = False

    try:
        print(msg)
        while True:
            key = getKey(settings)

            if key in moveBindings:
                x_inc, y_inc, z_inc, yaw_inc = moveBindings[key]
                x_pos += x_inc * position_step
                y_pos += y_inc * position_step
                z_pos += z_inc * position_step
                yaw_pos += yaw_inc * yaw_step
            else:
                # If it's not a recognized key, stop only if it's CTRL-C
                if key == '\x03':  # CTRL-C
                    break

            if key == ' ':  # Space bar toggles arming
                arm_toggle = not arm_toggle
                arm_msg = std_msgs.msg.Bool()
                arm_msg.data = arm_toggle
                arm_pub.publish(arm_msg)
                print(f"Arm toggle is now: {arm_toggle}")

            # Create and publish the position setpoint
            position_msg = geometry_msgs.msg.Twist()
            position_msg.linear.x = x_pos
            position_msg.linear.y = y_pos
            position_msg.linear.z = z_pos
            position_msg.angular.z = yaw_pos
            position_pub.publish(position_msg)

            print(
                f"X: {position_msg.linear.x:.2f}, "
                f"Y: {position_msg.linear.y:.2f}, "
                f"Z: {position_msg.linear.z:.2f}, "
                f"Yaw: {position_msg.angular.z:.2f}"
            )

    except Exception as e:
        print(e)

    finally:
        # On exit, publish a final zeroed command (if desired)
        stop_msg = geometry_msgs.msg.Twist()
        position_pub.publish(stop_msg)

        restoreTerminalSettings(settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
