import os
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
import cv2

class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__('yolo_detector_node')
        self.get_logger().info('YOLO Detector Node has been started.')

        self.bridge = CvBridge()

        self.camera_subscription = self.create_subscription(
            CompressedImage,
            '/camera/image/compressed',
            self.image_callback,
            10)
        
        self.detection_publisher = self.create_publisher(
            Detections,
            '/detections',
            10)

        self.model = self.load_model()
    
    def load_model(self):
        pkg_share = get_package_share_directory('package_that_uses_the_camera')

        model_path = os.path.join(pkg_share, 'models', 'yolov8.onnx')
        self.yolo_model = cv2.dnn.readNetFromONNX(model_path)
        self.yolo_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.yolo_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    def image_callback(self, msg):
        # Convert ROS CompressedImage to OpenCV image
        cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Perform YOLO detection
        blob = cv2.dnn.blobFromImage(cv_image, 1/255.0, (640, 640), swapRB=True, crop=False)
        self.yolo_model.setInput(blob)
        outputs = self.yolo_model.forward()

        # Process outputs and publish detections
        detections_msg = Detections()
        # Fill detections_msg based on outputs
        self.detection_publisher.publish(detections_msg)

# OLD CODE FROM camera_streamer.py FILE BELOW    
class CameraStreamerPublisherNode(Node):
    def __init__(self):
        super().__init__('camera_streamer_publisher_node')
        # Initialize your publisher here
        self.get_logger().info('Camera Streamer Publisher Node has been started.')
        # self.publisher_raw = self.create_publisher(Image, 'image_raw', 10)
        self.publisher_compressed = self.create_publisher(CompressedImage, '/camera/image/compressed', 10)
        self.publisher_compressed_yolo = self.create_publisher(CompressedImage, '/camera/image_yolo/compressed', 10)

        # Load YOLO model
        pkg_share = get_package_share_directory('package_that_uses_the_camera')
        # config_path = os.path.join(pkg_share, 'configs', 'yolov3.cfg')
        # model_path = os.path.join(pkg_share, 'models', 'yolov3.weights')
        # self.yolo_model = cv2.dnn.readNetFromDarknet(config_path, model_path)

        model_path = os.path.join(pkg_share, 'models', 'yolov8.onnx')
        self.yolo_model = cv2.dnn.readNetFromONNX(model_path)
        self.yolo_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.yolo_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        timer_period = 0.033  # seconds
        self.timer = self.create_timer(timer_period, self.publish_image)
        self.capture = cv2.VideoCapture(0)

    def publish_image(self):
        # Capture image from camera and publish
        # image_msg = Image()

        ret, frame = self.capture.read()
        if not ret:
            self.get_logger().error('Failed to capture image from camera.')
            return
        
        # Old code to detect circles using Hough Transform
        # frame_with_rectangle = frame.copy()
        # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame_gray = cv2.medianBlur(frame_gray, 9)
        # rows = frame_gray.shape[0]
        # circles = cv2.HoughCircles(frame_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=rows/4, param1=100, param2=30, minRadius=5, maxRadius=60)
        # if circles is not None:
        #     circles = np.uint16(np.around(circles))
        #     for i in circles[0, :]:
        #         # draw the outer circle
        #         cv2.circle(frame_with_rectangle, (i[0], i[1]), i[2], (0, 255, 0), 2)
        #         # draw the center of the circle
        #         cv2.circle(frame_with_rectangle, (i[0], i[1]), 2, (0, 0, 255), 3)
        # cv2.rectangle(frame_with_rectangle, (50, 50), (200, 200), (0, 255, 0), 2)
        # if ret:
        #     # Convert the frame to a ROS Image message
        #     image_msg.data = frame.tobytes()
        #     image_msg.height = frame.shape[0]
        #     image_msg.width = frame.shape[1]
        #     image_msg.encoding = 'bgr8'
        #     image_msg.step = frame.shape[1] * 3

        # New code to detect objects using YOLO
        frame_with_rectangle = frame.copy()
        height, width = frame.shape[:2]
        # blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
        print("Blob shape:", blob.shape)
        self.yolo_model.setInput(blob)
        # layer_names = self.yolo_model.getLayerNames()
        # layer_names = [layer_names[i - 1] for i in self.yolo_model.getUnconnectedOutLayers()]
        # outputs = self.yolo_model.forward(layer_names)
        outputs = self.yolo_model.forward().transpose((0, 2, 1))
        print("YOLO outputs shape:", outputs.shape)
        height, width = frame.shape[:2]
        boxes = []
        confidences = []
        for output in outputs: # 3 different detection heads
            for detection in output: # detections for each head
                scores = detection[4:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    print(f"Detection: class_name={class_id}, confidence={confidence}")
                    center_x = int(detection[0] * width / 640)
                    center_y = int(detection[1] * height / 640)
                    w = int(detection[2] * width / 640)
                    h = int(detection[3] * height / 640)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        print("Detected boxes:", len(indices))
        for i in indices:
            box = boxes[i]
            x, y, w, h = box
            print(f"Drawing box: x={x}, y={y}, w={w}, h={h}")
            cv2.rectangle(frame_with_rectangle, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # For compressed image, we can use JPEG encoding
        ret, buffer = cv2.imencode('.jpg', frame)
        ret, buffer_yolo = cv2.imencode('.jpg', frame_with_rectangle)
        image_msg_compressed = CompressedImage()
        image_msg_compressed_yolo = CompressedImage()
        if ret:
            image_msg_compressed.header.stamp = self.get_clock().now().to_msg()
            image_msg_compressed.header.frame_id = 'camera_frame'
            image_msg_compressed.data = buffer.tobytes()
            image_msg_compressed.format = 'jpeg'
            image_msg_compressed_yolo.header.stamp = self.get_clock().now().to_msg()
            image_msg_compressed_yolo.header.frame_id = 'camera_frame'
            image_msg_compressed_yolo.data = buffer_yolo.tobytes()
            image_msg_compressed_yolo.format = 'jpeg'

        # self.publisher_raw.publish(image_msg)
        self.publisher_compressed.publish(image_msg_compressed)
        self.publisher_compressed_yolo.publish(image_msg_compressed_yolo)

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