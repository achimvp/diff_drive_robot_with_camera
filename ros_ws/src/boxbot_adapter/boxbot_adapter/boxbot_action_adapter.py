# this node is responsible for collecting all the observations and publishing them as a single message
# The format of the message is defined in the boxbot_interfaces package as BoxbotObservation
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import TwistStamped

class BoxbotActionAdapterNode(Node):

    def __init__(self):
        super().__init__("boxbot_action_adapter_node")

        # create the subscriber nodes    
        ## subscribe to the rl action topic
        self.action_subscriber = self.create_subscription(
            Float64MultiArray,
            'rl/boxbot_action',
            self.action_callback,
            10
        )

        # create the publisher nodes
        ## publish to the odometry topic
        self.odom_publisher = self.create_publisher(
            TwistStamped,
            'diff_drive_controller/cmd_vel',
            10
        )

        ## publish to the camera turret controller topic
        self.camera_turret_position_publisher = self.create_publisher(
            Float64MultiArray,
            'camera_body_controller/commands',
            10
        )

        self.get_logger().info('Boxbot Action Adapter Node has been started.')

    def action_callback(self, msg: Float64MultiArray):
        self.get_logger().info(f"Received action: {msg}")
        # publish the action to the appropriate topics
        twist_msg = TwistStamped()
        twist_msg.header.stamp = self.get_clock().now().to_msg()
        twist_msg.twist.linear.x = msg.data[0] # assuming msg.data is a list or array of [linear_vel_x, linear_vel_y]
        twist_msg.twist.angular.z = msg.data[1] # assuming msg.data[2] is the angular velocity around the z-axis
        self.odom_publisher.publish(twist_msg)

        camera_turret_position_msg = Float64MultiArray()
        camera_turret_position_msg.data = [msg.data[2], msg.data[3]] # assuming msg.data[3] and msg.data[4] are the yaw and pitch values
        self.camera_turret_position_publisher.publish(camera_turret_position_msg)
    
    
def main(args=None):
    try:
        rclpy.init(args=args)
        boxbot_action_adapter_node = BoxbotActionAdapterNode()
        rclpy.spin(boxbot_action_adapter_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")