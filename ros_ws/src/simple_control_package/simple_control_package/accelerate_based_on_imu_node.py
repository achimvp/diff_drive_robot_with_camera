import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from boxbot_interfaces.msg import BoxbotObservation

class AccelerateBasedOnIMUNode(Node):
    def __init__(self):
        super().__init__('accelerate_based_on_imu_node')
        self.get_logger().info('Accelerate Based On IMU Node has been started.')

        self.observation_subscriber = self.create_subscription(
            BoxbotObservation,
            'boxbot_observation',
            self.observation_callback,
            10
        )

    def observation_callback(self, msg):
        self.imu_data = msg.imu
        self.get_logger().info(f"Received IMU data: {self.imu_data}")