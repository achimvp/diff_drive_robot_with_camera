#!/usr/bin/env python3
import os
import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
import cv2
import numpy as np

class CameraStreamerPublisherNode(Node):
    def __init__(self):
        super().__init__('camera_streamer_publisher_node')
        # Initialize your publisher here
        self.get_logger().info('Camera Streamer Publisher Node has been started.')
        self.publisher_raw = self.create_publisher(Image, '/camera/rgb/image_raw', 10)
        # self.publisher_compressed = self.create_publisher(CompressedImage, '/camera/image/compressed', 10)


        timer_period = 0.033  # seconds
        self.timer = self.create_timer(timer_period, self.publish_image)
        self.capture = cv2.VideoCapture(0)

    def publish_image(self):
        ret, frame = self.capture.read()
        if not ret:
            self.get_logger().error('Failed to capture image from camera.')
            return
        
        image_msg = Image()
        # Convert OpenCV image to ROS Image message
        image_msg.header.stamp = self.get_clock().now().to_msg()
        image_msg.header.frame_id = 'camera_frame'
        image_msg.height = frame.shape[0]
        image_msg.width = frame.shape[1]
        image_msg.encoding = 'bgr8'
        image_msg.is_bigendian = False
        image_msg.step = frame.shape[1] * 3
        image_msg.data = frame.tobytes()
        
        # ret, buffer = cv2.imencode('.jpg', frame)
        # image_msg_compressed = CompressedImage()
        # if ret:
        #     image_msg_compressed.header.stamp = self.get_clock().now().to_msg()
        #     image_msg_compressed.header.frame_id = 'camera_frame'
        #     image_msg_compressed.data = buffer.tobytes()
        #     image_msg_compressed.format = 'jpeg'

        self.publisher_raw.publish(image_msg)
        # self.publisher_compressed.publish(image_msg_compressed)

        # Logic to publish image
        self.get_logger().info('Published an image.')
    
    def destroy_node(self):
        self.capture.release()
        super().destroy_node()

def main():
    print('Hi from package_that_uses_the_camera.')
    try:
        rclpy.init()
        node = CameraStreamerPublisherNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
