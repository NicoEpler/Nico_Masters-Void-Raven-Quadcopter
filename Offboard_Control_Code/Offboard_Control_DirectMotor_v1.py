# motor_control.py
import rclpy
from rclpy.node import Node
from px4_msgs.msg import ActuatorControl

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')

        # Publisher to actuator controls
        self.control_publisher = self.create_publisher(ActuatorControl, "/fmu/actuator_controls", 10)

        # Timer to regularly send control commands
        self.timer = self.create_timer(0.1, self.publish_motor_commands)

        # Initialize actuator control message
        self.control_msg = ActuatorControl()
        self.control_msg.control = [0.0] * 8  # Assuming an 8-channel setup, all set to 0 initially

        # Set motor control values (example values for motors)
        self.set_motor_values(0.5, 0.5, 0.5, 0.5)  # Adjust as needed

    def set_motor_values(self, motor_1, motor_2, motor_3, motor_4):
        """ Set the values for the motors (normalized from -1.0 to 1.0) """
        self.control_msg.control[0] = motor_1
        self.control_msg.control[1] = motor_2
        self.control_msg.control[2] = motor_3
        self.control_msg.control[3] = motor_4

    def publish_motor_commands(self):
        # Publish the motor control commands
        self.control_publisher.publish(self.control_msg)
        self.get_logger().info('Motor commands sent!')

def main(args=None):
    rclpy.init(args=args)
    motor_control_node = MotorControlNode()
    rclpy.spin(motor_control_node)

    motor_control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
