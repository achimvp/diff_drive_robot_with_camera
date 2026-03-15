import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MoveCirclePublisherNode(Node):
    def __init__(self):
        super().__init__('move_circle_publisher_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5  # Move forward at 0.5 m/s
        msg.angular.z = 0.5  # No rotation
        self.publisher_.publish(msg)
    

def main(args=None):
    try:
        rclpy.init(args=args)
        move_circle_publisher_node = MoveCirclePublisherNode()
        rclpy.spin(move_circle_publisher_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")