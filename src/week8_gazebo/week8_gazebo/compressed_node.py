import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
import cv2
import numpy as np
from cv_bridge import CvBridge

class ImageToCompressed(Node):
    def __init__(self):
        super().__init__('compressed_node')

        # Create a CvBridge instance
        self.bridge = CvBridge()

        # Subscriptions
        self.world_cam_sub = self.create_subscription(
            Image,
            '/world_cam/image',
            self.world_cam_callback,
            10
        )
        self.robot_cam_sub = self.create_subscription(
            Image,
            '/robot_cam/image',
            self.robot_cam_callback,
            10
        )

        # Publishers
        self.world_cam_pub = self.create_publisher(
            CompressedImage,
            '/world_cam/image/compressed',
            10
        )
        self.robot_cam_pub = self.create_publisher(
            CompressedImage,
            '/robot_cam/image/compressed',
            10
        )

    def world_cam_callback(self, data):
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')

            # Encode image to JPEG format
            _, encoded_image = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

            # Create a CompressedImage message
            compressed_msg = CompressedImage()
            compressed_msg.header = data.header
            compressed_msg.format = "jpeg"
            compressed_msg.data = np.array(encoded_image).tobytes()

            # Publish the compressed image
            self.world_cam_pub.publish(compressed_msg)

        except Exception as e:
            self.get_logger().error(f"Error in world_cam_callback: {str(e)}")
    
    def robot_cam_callback(self, data):
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')

            # Encode image to JPEG format
            _, encoded_image = cv2.imencode('.jpg', cv_image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

            # Create a CompressedImage message
            compressed_msg = CompressedImage()
            compressed_msg.header = data.header
            compressed_msg.format = "jpeg"
            compressed_msg.data = np.array(encoded_image).tobytes()

            # Publish the compressed image
            self.robot_cam_pub.publish(compressed_msg)

        except Exception as e:
            self.get_logger().error(f"Error in robot_cam_callback: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    node = ImageToCompressed()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
