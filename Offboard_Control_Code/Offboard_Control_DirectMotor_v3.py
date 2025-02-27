import rclpy
from rclpy.node import Node
from rclpy.clock import Clock
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

from px4_msgs.msg import ActuatorMotors
from px4_msgs.msg import VehicleStatus
from px4_msgs.msg import OffboardControlMode
import numpy as np

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')

        # Define QoS settings for reliability and delivery of messages
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT,
            durability=QoSDurabilityPolicy.RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.RMW_QOS_POLICY_HISTORY_KEEP_LAST,
            depth=1
        )

        # Subscription to the vehicle status for monitoring arm and navigation states
        self.status_sub = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.vehicle_status_callback,
            qos_profile)

        # Publisher to actuator controls
        self.control_publisher = self.create_publisher(ActuatorMotors, "/fmu/in/actuator_controls", qos_profile)

        # Publisher to offboard control mode to maintain offboard mode
        self.offboard_mode_publisher = self.create_publisher(OffboardControlMode, "/fmu/in/offboard_control_mode", qos_profile)

        # Timer to regularly send control commands (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop_callback)

        # Initialize actuator control message
        self.control_msg = ActuatorMotors()
        self.control_msg.control = np.zeros(12,dtype=np.float32)
        #self.control_msg.control = [0.0] * 8  # Assuming an 8-channel setup, all set to 0 initially

        # Set motor control values (example values for motors)
        self.set_motor_values(0.05, 0.05, 0.05, 0.05)  # Adjust as needed

        # Initialize vehicle state variables
        self.nav_state = VehicleStatus.NAVIGATION_STATE_MAX
        self.arming_state = VehicleStatus.ARMING_STATE_DISARMED

    def vehicle_status_callback(self, msg):
        """ Callback function to update vehicle arming and navigation state """
        self.nav_state = msg.nav_state
        self.arming_state = msg.arming_state
        self.get_logger().info(f'Vehicle Status - NAV: {self.nav_state}, ARM: {self.arming_state}')

    def set_motor_values(self, motor_1, motor_2, motor_3, motor_4):
        """ Set the values for the motors (normalized from -1.0 to 1.0) """
        self.control_msg.control[0] = motor_1
        self.control_msg.control[1] = motor_2
        self.control_msg.control[2] = motor_3
        self.control_msg.control[3] = motor_4

    def control_loop_callback(self):
        """ Publish offboard control mode and motor control commands """

        # Publish offboard control mode (heartbeat signal)
        offboard_mode_msg = OffboardControlMode()
        offboard_mode_msg.timestamp = int(Clock().now().nanoseconds / 1000)
        offboard_mode_msg.position = False  # No position control
        offboard_mode_msg.velocity = False  # No velocity control
        offboard_mode_msg.acceleration = False  # No acceleration control
        offboard_mode_msg.attitude = False  # No attitude control
        offboard_mode_msg.body_rate = False  # No body rate control
        offboard_mode_msg.thrust_and_torque = True  # No thrust and torque control
        offboard_mode_msg.direct_actuator = False  # Enable direct actuator control

        self.offboard_mode_publisher.publish(offboard_mode_msg)

        # Only publish motor control commands if armed and in offboard mode
        #if (self.nav_state == VehicleStatus.NAVIGATION_STATE_OFFBOARD and 
        #    self.arming_state == VehicleStatus.ARMING_STATE_ARMED):
            
            # Add timestamp to the actuator control message
        #    self.control_msg.timestamp = int(Clock().now().nanoseconds / 1000)
            
            # Publish the motor control commands
        #    self.control_publisher.publish(self.control_msg)
        #    self.get_logger().info('Motor commands sent!')

        #else:
        #    self.get_logger().warn('Vehicle not armed or not in offboard mode; commands not sent.')
            
            
        # Add timestamp to the actuator control message
        self.control_msg.timestamp = int(Clock().now().nanoseconds / 1000)
        
        # Publish the motor control commands
        self.control_publisher.publish(self.control_msg)
        self.get_logger().info('Motor commands sent!')
            
            
def main(args=None):
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create an instance of the MotorControlNode
    motor_control_node = MotorControlNode()

    # Keep the node running
    rclpy.spin(motor_control_node)

    # Shutdown the node when done
    motor_control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
