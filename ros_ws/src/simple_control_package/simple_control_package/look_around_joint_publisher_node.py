import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformListener, Buffer

class LookAroundJointStatePublisherNode(Node):
    def __init__(self):
        super().__init__('look_around_joint_publisher_node')
        self.get_logger().info('Look Around Joint Publisher Node has been started.')

        self.joint_state_publisher = self.create_publisher(
            JointState,
            'joint_states',
            10
        )

        self.joint_state = JointState()
        self.joint_state.name = ['camera_head_joint', 'camera_body_joint']
        self.joint_state.position = [0.0, 0.0]
        self.joint_state.velocity = [0.0, 0.0]
        self.joint_state.effort = [0.0, 0.0]

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.timer = self.create_timer(0.1, self.publish_joint_state_callback)
        self.pitch = 0.0
        self.yaw = 0.0
        self.increment = 0.1  # Increment for yaw angle
    
    def publish_joint_state_callback(self):
        now = self.get_clock().now()
        self.joint_state.header.stamp = now.to_msg()
        self.joint_state.position = [self.pitch, self.yaw]
        self.joint_state_publisher.publish(self.joint_state)

        # Update the angles for the next position
        self.yaw += self.increment  # Increment yaw to rotate horizontally
        if self.yaw < - 1.57:  # Reset yaw after a full rotation
            self.yaw = -1.57
            self.increment *= -1 # Reverse direction to look back
        if self.yaw > 1.57:  # Reset yaw after a full rotation
            self.yaw = 1.57
            self.increment *= -1 # Reverse direction to look back
        
        try:
            transform1 = self.tf_buffer.lookup_transform('camera_base_link', 'camera_body_link', rclpy.time.Time())
            self.get_logger().info(f"Transform from base_link to camera_link: {transform1}")
            transform2 = self.tf_buffer.lookup_transform('camera_body_link', 'camera_head_link', rclpy.time.Time())
            self.get_logger().info(f"Transform from camera_link to base_link: {transform2}")
        except Exception as e:
            self.get_logger().error(f"Error looking up transform: {e}")

def main(args=None):
    try:
        rclpy.init(args=args)
        look_around_joint_publisher_node = LookAroundJointStatePublisherNode()
        rclpy.spin(look_around_joint_publisher_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")