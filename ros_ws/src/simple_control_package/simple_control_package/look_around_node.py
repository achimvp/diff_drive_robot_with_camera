import rclpy
from rclpy.node import Node
from boxbot_interfaces.msg import CameraTurretPosition
from std_msgs.msg import Float64MultiArray

class LookAroundNode(Node):
    def __init__(self):
        super().__init__('look_around_node')
        self.get_logger().info('Look Around Node has been started.')

        self.camera_position_publisher = self.create_publisher(
            # CameraTurretPosition,
            Float64MultiArray,
            'camera_body_controller/commands',
            10
        )

        self.timer = self.create_timer(0.1, self.publish_camera_position_callback)
        self.pitch = 0.0
        self.yaw = 0.0
        self.increment = 0.1  # Increment for yaw angle
    
    def publish_camera_position_callback(self):
        # msg = CameraTurretPosition()
        # msg.pitch = self.pitch
        # msg.yaw = self.yaw
        msg = Float64MultiArray()
        msg.data = [self.yaw, self.pitch]
        self.camera_position_publisher.publish(msg)

        # Update the angles for the next position
        self.yaw += self.increment  # Increment yaw to rotate horizontally
        if self.yaw < - 1.57:  # Reset yaw after a full rotation
            self.yaw = -1.57
            self.increment *= -1 # Reverse direction to look back
        if self.yaw > 1.57:  # Reset yaw after a full rotation
            self.yaw = 1.57
            self.increment *= -1 # Reverse direction to look back

def main(args=None):
    try:
        rclpy.init(args=args)
        look_around_node = LookAroundNode()
        rclpy.spin(look_around_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")