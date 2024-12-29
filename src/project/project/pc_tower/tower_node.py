import rclpy, time, cv2, numpy as np
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from project.pc_tower.callback import NodeCallbacks
from project.database import DetectDBHandler


def add_methods_from(source_class):
    """
    source_class의 메서드를 대상 클래스에 추가하는 데코레이터
    """
    def decorator(target_class):
        for attr_name in dir(source_class):
            if callable(getattr(source_class, attr_name)) and not attr_name.startswith("__"):
                # source_class의 메서드를 target_class에 추가
                setattr(target_class, attr_name, getattr(source_class, attr_name))
        return target_class
    return decorator


@add_methods_from(NodeCallbacks)
class TowerNode(Node):

    def __init__(self):
        super().__init__('tower_node')
        self.get_logger().info('Tower node started')
        self.init_subscribers()

    def init_subscribers(self):
        self.robot_sub()
        self.world_sub()
        self.robot_image = None
        self.robot_class = None
        self.robot_box = None
        self.world_image = None
        self.world_class = None
        self.world_box = None
        
    def robot_sub(self):    
        self.robot_image_sub = self.create_subscription(
            CompressedImage,
            'robot/image',
            self.robot_image_callback,
            5
        )
        self.robot_class_sub = self.create_subscription(
            String,
            'robot/classes',
            self.robot_class_callback,
            5
        )
        self.robot_box_sub = self.create_subscription(
            String,
            'robot/boxes',
            self.robot_box_callback,
            5
        )

    def world_sub(self):
        self.world_image_sub = self.create_subscription(
            CompressedImage,
            'world/image',
            self.world_image_callback,
            5
        )
        self.world_class_sub = self.create_subscription(
            String,
            'world/classes',
            self.world_class_callback,
            5
        )
        self.world_box_sub = self.create_subscription(
            String,
            'world/boxes',
            self.world_box_callback,
            5
        )

    def db_open(self):
        self.world_db = DetectDBHandler('world') # world 데이터베이스 핸들러
        