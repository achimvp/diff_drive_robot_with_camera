# this node is responsible for collecting all the observations and publishing them as a single message
# The format of the message is defined in the boxbot_interfaces package as BoxbotObservation
import rclpy
import numpy as np
from rclpy.node import Node
from boxbot_interfaces.msg import BoxbotObservation, CameraTurretPosition
from sensor_msgs.msg import CameraInfo, Imu, Image, JointState
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion

class BoxbotAdapterNode(Node):

    PUBLISH_RATE_HZ = 20.0

    def __init__(self):
        super().__init__("boxbot_adapter_node")

        # initialize instance variables to store the latest observations
        self._latest_odometry_position = None # this will store the latest position data from the odometry topic (x, y, yaw)
        self._latest_odometry_velocity = None # this will store the latest velocity data from the odometry topic
        self._latest_image = None # this will store the latest image data from the camera
        self._latest_camera_info = None # this will store the latest camera info data from the camera_info topic
        self._latest_imu_linear_acceleration = None # this will store the linear acceleration data from the IMU
        self._latest_imu_angular_velocity = None # this will store the angular velocity data from the IMU
        self._latest_camera_turret_position = None # this will store the latest camera turret position data (yaw and pitch) from the camera turret controller

        self._latest_odometry_ts = self.get_clock().now() # this will store the timestamp of the latest odometry data, which is used to determine if the odometry data is stale or not
        self._latest_imu_ts = self.get_clock().now() # this will store the timestamp of the latest IMU data, which is used to determine if the IMU data is stale or not
        self._latest_image_ts = self.get_clock().now() # this will store the timestamp of the latest image data, which is used to determine if the image data is stale or not
        self._latest_camera_info_ts = self.get_clock().now() # this will store the timestamp of the latest camera info data, which is used to determine if the data is stale or not
        self._latest_camera_turret_position_ts = self.get_clock().now() # this will store the timestamp of the latest camera turret position data, which is used to determine if the data is stale or not

        # create the subscriber nodes
        ## subscribe to the odometry topic
        self.odom_subscriber = self.create_subscription(
            Odometry,
            'diff_drive_controller/odom',
            self.odometry_callback,
            10
        )

        ## subscribe to the camera topic
        self.camera_subscriber = self.create_subscription(
            Image,
            'camera/image_raw',
            self.image_callback,
            10
        )

        ## subscribe to the camera info topic
        self.camera_info_subscriber = self.create_subscription(
            CameraInfo,
            'camera/camera_info',
            self.camera_info_callback,
            10
        )

        ## subscribe to the imu topic
        self.imu_subscriber = self.create_subscription(
            Imu,
            'imu_sensor_broadcaster/imu',
            self.imu_callback,
            10
        )

        ## subscribe to the camera turret position topic
        self.camera_turret_position_subscriber = self.create_subscription(
            JointState,
            'joint_states',
            self.camera_turret_position_callback,
            10
        )

        # create the publisher node
        self.observation_publisher = self.create_publisher(
            BoxbotObservation,
            'boxbot_observation',
            10
        )

        self.create_timer(1.0/self.PUBLISH_RATE_HZ, self._publish_observation)
        self.get_logger().info('Boxbot Adapter Node has been started.')
    
    def odometry_callback(self, msg):
        _, _, yaw = euler_from_quaternion([msg.pose.pose.orientation.w, msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z])
        
        self._latest_odometry_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            yaw,
        ])
        self._latest_odometry_velocity = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.angular.z
        ])
        self._latest_odometry_ts = self.get_clock().now()

    def image_callback(self, msg: Image):
        self._latest_image = msg
        self._latest_image_ts = self.get_clock().now()

    def imu_callback(self, msg: Imu):
        self._latest_imu_linear_acceleration = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
        ])
        self._latest_imu_angular_velocity = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])
        self._latest_imu_ts = self.get_clock().now()

    def camera_info_callback(self, msg: CameraInfo):
        self._latest_camera_info = msg
        self._latest_camera_info_ts = self.get_clock().now()

    def camera_turret_position_callback(self, msg: JointState):
        camera_turret_position = CameraTurretPosition()
        camera_turret_position.yaw = msg.position[0] # assuming the first joint is the yaw of the camera turret
        camera_turret_position.pitch = msg.position[1] # assuming the second joint is
        self._latest_camera_turret_position = camera_turret_position
        self._latest_camera_turret_position_ts = self.get_clock().now()
    
    def _publish_observation(self):
        if not self._all_data_ready():
            self.get_logger().warn('Not all data is ready, skipping observation publish.')
            return
        observation_msg = BoxbotObservation()
        observation_msg.header.stamp = self.get_clock().now().to_msg()
        observation_msg.linear_acceleration = self._latest_imu_linear_acceleration.tolist() # convert the numpy array to a list before publishing
        observation_msg.angular_velocity = self._latest_imu_angular_velocity.tolist() # convert the numpy array to a list before publishing
        observation_msg.position = self._latest_odometry_position.tolist() # convert the numpy array to a list before publishing
        observation_msg.velocity = self._latest_odometry_velocity.tolist() # convert the numpy array to a list before publishing
        observation_msg.camera_turret_position = self._latest_camera_turret_position # this is already a custom message type, so we can assign it directly
        observation_msg.camera_image = self._latest_image
        observation_msg.camera_info = self._latest_camera_info # this is already a custom message type, so we can assign it directly
        self.observation_publisher.publish(observation_msg)
        
    

    def _all_data_ready(self):
        now = self.get_clock().now()

        def fresh(latest_ts):
            return (now - latest_ts).nanoseconds < 1e9 # data is considered fresh if it is less than 0.1 second old
        
        return all([
            self._latest_odometry_position is not None and self._latest_odometry_velocity is not None and fresh(self._latest_odometry_ts),
            self._latest_image is not None and fresh(self._latest_image_ts),
            self._latest_imu_linear_acceleration is not None and self._latest_imu_angular_velocity is not None and fresh(self._latest_imu_ts),
            self._latest_camera_turret_position is not None and fresh(self._latest_camera_turret_position_ts),
            self._latest_camera_info is not None and fresh(self._latest_camera_info_ts)
        ])


def main(args=None):
    try:
        rclpy.init(args=args)
        boxbot_adapter_node = BoxbotAdapterNode()
        rclpy.spin(boxbot_adapter_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")