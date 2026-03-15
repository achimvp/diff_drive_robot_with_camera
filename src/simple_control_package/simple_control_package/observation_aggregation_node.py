import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, Image
from control_msgs.msg import JointTrajectoryControllerState
from boxbot_interfaces.msg import CameraTurretPosition, BoxbotObservation

class ObservationAggregationNode(Node):
    def __init__(self):
        super().__init__('observation_aggregation_node')
        self.get_logger().info('Observation Aggregation Node has been started.')

        self.odom_subscriber = self.create_subscription(
            Odometry,
            'diff_drive_controller/odom',
            self.odom_callback,
            10
        )
        self.imu_subscriber = self.create_subscription(
            Imu,
            'imu_sensor_broadcaster/imu',
            self.imu_callback,
            10
        )
        self.camera_turret_position_subscriber = self.create_subscription(
            JointTrajectoryControllerState, # actual position of the camera turret, not the command position
            'camera_body_controller/controller_state',
            self.camera_turret_position_callback,
            10
        )

        self.image_subscriber = self.create_subscription(
            Image,
            'camera/image_raw',
            self.image_callback,
            10
        )

        # Publishers for processed data can be added here
        ## Maybe we can publish the controls in a single message that contains both the camera turret position and the diff drive command
        # self.camera_turret_position_command_publisher = self.create_publisher(
        #     CameraTurretPosition, # desired position of the camera turret, which will be published to the camera turret position controller plugin that we will write for Gazebo
        #     'camera_body_controller/cmd_pos',
        #     10
        # )
        # self.diff_drive_command_publisher = self.create_publisher(
        #     Odometry,
        #     'diff_drive_controller/cmd_vel',
        #     10
        # )

        self.boxbot_observation_publisher = self.create_publisher(
            BoxbotObservation,
            'boxbot_observation',
            10
        )

        self.publish_state_timer = self.create_timer(0.034, self.publish_state_callback)  # Run inference at 30 Hz
        self.last_odom = Odometry()
        self.last_imu = Imu()
        self.last_camera_turret_position = CameraTurretPosition()
        self.last_camera_image = Image()
    
    def odom_callback(self, msg):
        # We could process the odometry data here if needed, but for now we will just store it for inference
        # One way to process the odometry data would be to use a small GRU to aggregate the velocity measurements over time and use that as input to the inference model
        # This way we do not lose the information about velocity measurements that we between the inference steps, which could be important for generating accurate control commands
        # The same holds for the IMU data
        self.last_odom = msg

    def imu_callback(self, msg):
        self.last_imu = msg

    def camera_turret_position_callback(self, msg):
        self.last_camera_turret_position.yaw = msg.feedback.positions[0]  # Assuming the first joint in the trajectory is the camera body joint
        self.last_camera_turret_position.pitch = msg.feedback.positions[1]  # Assuming the second joint in the trajectory is the camera head joint

    def image_callback(self, msg):
        self.last_camera_image = msg
    
    def publish_state_callback(self):
        """Here we will publish the aggregated state data."""
        boxbot_observation = BoxbotObservation()
        boxbot_observation.odom = self.last_odom
        boxbot_observation.imu = self.last_imu
        boxbot_observation.camera_turret_position = self.last_camera_turret_position
        boxbot_observation.camera_image = self.last_camera_image
        self.boxbot_observation_publisher.publish(boxbot_observation)

            # # Publish the aggregated state data
            # # This is where you would publish the aggregated sensor data to a topic that can be consumed by an inference node
            # # For demonstration, we will just log the aggregated state data
            # self.get_logger().info(f"Publishing aggregated state: Odom={self.last_odom}, IMU={self.last_imu}, Camera Turret Position={self.last_camera_turret_position}, Image={self.last_camera_image}")

            # # Create a dummy camera turret position command
            # camera_command = CameraTurretPosition()
            # camera_command.pan = self.current_camera_turret_position.pan + 0.1  # Example modification
            # camera_command.tilt = self.current_camera_turret_position.tilt + 0.1  # Example modification

            # # Create a dummy diff drive command
            # diff_drive_command = Odometry()
            # diff_drive_command.twist.twist.linear.x = self.current_velocity_measurement.twist.twist.linear.x + 0.1  # Example modification
            # diff_drive_command.twist.twist.angular.z = self.current_velocity_measurement.twist.twist.angular.z + 0.1  # Example modification

            # # Publish the commands
            # self.camera_turret_position_command_publisher.publish(camera_command)
            # self.diff_drive_command_publisher.publish(diff_drive_command)

def main(args=None):
    try:
        rclpy.init(args=args)
        observation_aggregation_node = ObservationAggregationNode()
        rclpy.spin(observation_aggregation_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")