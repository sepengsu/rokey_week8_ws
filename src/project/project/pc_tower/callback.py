import cv2, numpy as np, rclpy, time, os

class NodeCallbacks:
    '''
    NodeMethods 클래스
    node의 주요 메서드를 정의하는 클래스
    '''
    def world_camera_image_callback(self, msg):
        """월드 카메라 이미지 콜백"""
        if msg is None:
            return
        np_arr = np.frombuffer(msg.data, np.uint8)
        # np_arr를 이미지로 변환 (np_arr -> np.ndarray)
        self.world_camera_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

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
        self.world_camera_boxes = boxes
    def world_camera_classes_callback(self, msg):
        """월드 카메라 클래스 콜백"""
        if msg.data == 'None':
            return
        classes = eval(msg.data) # 문자열을 리스트로 변환
        self.world_camera_classes = classes

    def robot_camera_image_callback(self, msg):
        """로봇 카메라 이미지 콜백"""
        if msg is None:
            return
        np_arr = np.frombuffer(msg.data, np.uint8)
        # np_arr를 이미지로 변환 (np_arr -> np.ndarray)
        self.robot_camera_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    def robot_camera_boxes_callback(self, msg):
        """
        로봇 카메라 박스 콜백
        데이터 타입: [[x,y,w,h], [x,y,w,h], ...]
        """
        if self.robot_camera_frame is None:
            self.get_logger().warning("Robot camera frame is not ready. Skipping boxes callback.")
            return
        
        if msg.data == 'None':
            return

        boxes = eval(msg.data)
        self.robot_camera_boxes = boxes
    
    def robot_camera_classes_callback(self, msg):
        """로봇 카메라 클래스 콜백"""
        if msg.data == 'None':
            return
        classes = eval(msg.data)
        self.robot_camera_classes = classes
        