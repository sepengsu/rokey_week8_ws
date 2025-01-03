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
        self.init_world_cam()

    
    def init_world_cam(self):
        """월드 카메라 관련 노드 초기화"""
        self.create_subscription(
            CompressedImage,
            '/world_cam/image',
            self.world_camera_image_callback,
            5
        )
        self.create_subscription(
            String,
            '/world_cam/boxes',
            self.world_camera_boxes_callback,
            5
        )
        self.create_subscription(
            String,
            '/world_cam/classes',
            self.world_camera_classes_callback,
            5
        )

    def init_robot_cam(self):
        """로봇 카메라 관련 노드 초기화"""
        self.create_subscription(
            CompressedImage,
            '/robot_cam/image',
            self.robot_camera_image_callback,
            5
        )
        self.create_subscription(
            String,
            '/robot_cam/boxes',
            self.robot_camera_boxes_callback,
            5
        )
        self.create_subscription(
            String,
            '/robot_cam/classes',
            self.robot_camera_classes_callback,
            5
        )

    def world_camera_image_callback(self, msg):
        """월드 카메라 이미지 콜백"""
        np_arr = np.frombuffer(msg.data, np.uint8)
        # np_arr를 이미지로 변환 (np_arr -> np.ndarray)
        self.world_camera_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # 이미지를 np.ndarray로 변환
        # self.world_camera_frame = cv2.cvtColor(self.world_camera_frame, cv2.COLOR_BGR2RGB)

    def world_camera_boxes_callback(self, msg):
        """
        월드 카메라 박스 콜백
        데이터 타입: [[x,y,w,h], [x,y,w,h], ...]
        """
        if self.world_camera_frame is None:
            self.get_logger().warning("World camera frame is not ready. Skipping boxes callback.")
            return
        
        if msg.data == 'None':
            return

        boxes = eval(msg.data) # 문자열을 리스트로 변환
        for box in boxes:
            x, y, w, h = box
            cv2.rectangle(self.world_camera_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    def world_camera_classes_callback(self, msg):
        """월드 카메라 클래스 콜백"""
        if msg.data == 'None':
            return
        
        classes = eval(msg.data)
        for class_ in classes:
            cv2.putText(self.world_camera_frame, class_, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    
    def robot_camera_image_callback(self, msg):
        """로봇 카메라 이미지 콜백"""
        pass

    def robot_camera_boxes_callback(self, msg):
        """로봇 카메라 박스 콜백"""
        pass

    def robot_camera_classes_callback(self, msg):
        """로봇 카메라 클래스 콜백"""
        pass