import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np

class GuiNode(Node):
    def __init__(self):
        super().__init__('gui_node')
        self.get_logger().info('GUI node started')
        self.world_camera_frame = None
        self.robot_camera_frame = None

        # ROS 2 이미지 토픽 구독
        self.create_subscription(
            CompressedImage,
            '/world/camera',
            self.world_camera_callback,
            QoSProfile(depth=10)
        )
        self.create_subscription(
            CompressedImage,
            '/robot/camera',
            self.robot_camera_callback,
            QoSProfile(depth=10)
        )

    def world_camera_callback(self, msg):
        """월드 카메라 이미지 콜백"""
        np_arr = np.frombuffer(msg.data, np.uint8)
        if np_arr.size == 0:
            self.get_logger().info('Empty image')
            return
        self.world_camera_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def robot_camera_callback(self, msg):
        """로봇 카메라 이미지 콜백"""
        np_arr = np.frombuffer(msg.data, np.uint8)
        self.robot_camera_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)