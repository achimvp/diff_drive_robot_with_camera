import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class RosControlNode(Node):
    def __init__(self):
        super().__init__("ros_control_node")
        self.get_logger().info("ROS Control Node has been initialized.")

        self.create_timer(0.1, self.timer_callback) 
        self.ctrl_pub = self.create_publisher(Float64MultiArray, "/boxbot/action", 10)
        self._init_time = self.get_clock().now()
    
    def timer_callback(self):
        self.get_logger().info("Timer callback executed.")
        self.ctrl_pub.publish(Float64MultiArray(data=[1.0, 0.0, 0.0, 0.0]))  # Example command to move forward
        if (self.get_clock().now() - self._init_time).nanoseconds > 1e10:  # Run for 10 seconds
            self.get_logger().info("Shutting down ROS Control Node after 10 seconds.")
            raise SystemExit


def main(args=None):
    rclpy.init(args=args)
    try:
        node = RosControlNode()
        rclpy.spin(node)
    except SystemExit:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()