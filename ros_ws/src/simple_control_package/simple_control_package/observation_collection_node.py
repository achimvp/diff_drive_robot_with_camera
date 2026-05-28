# this node is responsible for collecting all the observations and publishing them as a single message
# The format of the message is defined in the boxbot_interfaces package as BoxbotObservation
import rclpy
import numpy as np
from rclpy.node import Node
from boxbot_interfaces.msg import BoxbotObservation
from sensor_msgs.msg import Imu, Image, JointState
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray

class ObservationCollectionNode(Node):

    PUBLISH_RATE_HZ = 10.0

    def __init__(self):
        super().__init__("observation_collection_node")

        # initialize instance variables to store the latest observations
        self._latest_odometry = None # this will store the latest odometry data from the odometry topic
        self._latest_image = None # this will store the latest image data from the camera
        self._latest_imu = None # this will store the linear acceleration and angular velocity data from the IMU
        self._latest_camera_turret_position = None # this will store the latest camera turret position data (yaw and pitch) from the camera turret controller

        self._latest_odometry_ts = self.get_clock().now() # this will store the timestamp of the latest odometry data, which is used to determine if the odometry data is stale or not
        self._latest_imu_ts = self.get_clock().now() # this will store the timestamp of the latest IMU data, which is used to determine if the IMU data is stale or not
        self._latest_image_ts = self.get_clock().now() # this will store the timestamp of the latest image data, which is used to determine if the image data is stale or not
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
        self.get_logger().info('Observation Collection Node has been started.')
    
    def odometry_callback(self, msg):
        self._latest_odometry = msg
        self._latest_odometry_ts = self.get_clock().now()

    def image_callback(self, msg: Image):
        self._latest_image = msg.data
        self._latest_image_ts = self.get_clock().now()

    def imu_callback(self, msg: Imu):
        self._latest_imu = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z,
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])
        self._latest_imu_ts = self.get_clock().now()

    def camera_turret_position_callback(self, msg: JointState):
        self._latest_camera_turret_position = msg.position[:2] # we only care about the first two joints, which are the yaw and pitch of the camera turret
        self._latest_camera_turret_position_ts = self.get_clock().now()
    
    def _publish_observation(self):
        if not self._all_data_ready():
            self.get_logger().warn('Not all data is ready, skipping observation publish.')
            return
        observation_msg = BoxbotObservation()
        observation_msg.odom = self._latest_odometry
        observation_msg.camera_image.data = self._latest_image
        observation_msg.imu.data = self._latest_imu.tolist() # convert the numpy array to a list before publishing
        observation_msg.camera_turret_position.data = self._latest_camera_turret_position
        self.observation_publisher.publish(observation_msg)
        
    

    def _all_data_ready(self):
        now = self.get_clock().now()

        def fresh(latest_ts):
            return (now - latest_ts).nanoseconds < 1e9 # data is considered fresh if it is less than 0.1 second old
        
        print(self._latest_odometry_ts, self._latest_image_ts, self._latest_imu_ts, self._latest_camera_turret_position_ts)
        print(self._latest_odometry is not None, self._latest_image is not None, self._latest_imu is not None, self._latest_camera_turret_position is not None)
        
        return all([
            self._latest_odometry is not None and fresh(self._latest_odometry_ts),
            self._latest_image is not None and fresh(self._latest_image_ts),
            self._latest_imu is not None and fresh(self._latest_imu_ts),
            self._latest_camera_turret_position is not None and fresh(self._latest_camera_turret_position_ts)
        ])


def main(args=None):
    try:
        rclpy.init(args=args)
        observation_collection_node = ObservationCollectionNode()
        rclpy.spin(observation_collection_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")