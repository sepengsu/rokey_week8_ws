import rclpy, cv2
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from project.detection import Detection
from std_msgs.msg import String
from project.database import DetectDBHandler
import time
import warnings

def get_index_of_cam():
    warnings.filterwarnings('ignore')
    index = 0
    cap = cv2.VideoCapture(index) # 0번 카메라부터 시작
    while not cap.isOpened():
        index += 1 # 카메라 인덱스 증가
        cap = cv2.VideoCapture(index)
    cap.release()
    print(f'Camera index: {index}')
    return index

class RobotCam(Node):
    def __init__(self):
        super().__init__('robot_cam')
        self.image_pub = self.create_publisher(CompressedImage, '/robot_cam/image', 5)
        self.boxes_pub = self.create_publisher(String, '/robot_cam/boxes', 5)
        self.classes_pub = self.create_publisher(String, '/robot_cam/classes', 5)
        self.yolo = Detection('robot')
        self.frame = None
        self.cam_index = get_index_of_cam()
        self.create_timer(0.06,self.process) # 0.02초마다 process 함수 실행
    
    def process(self):
        cur_time = time.localtime() # 현재 시간 구하기
        cur_time = f'{cur_time.tm_year}-{cur_time.tm_mon}-{cur_time.tm_mday} {cur_time.tm_hour}:{cur_time.tm_min}:{cur_time.tm_sec}'
        self.get_frame()
        boxes, classes = self.yolo.detect(self.frame)

        if self.frame is None:
            return
        self.publish_image()
        self.publish_boxes(boxes)
        self.publish_classes(classes)

    def get_frame(self):
        index = self.cam_index
        cap = cv2.VideoCapture(index)
        ret, frame = cap.read()
        if not ret:
            self.get_logger().error('Failed to get frame')
            self.frame = None
            return
        self.frame = frame
    
    def publish_image(self):
        msg = CompressedImage()
        msg.format = 'jpeg'
        msg.data = cv2.imencode('.jpg', self.frame)[1].tobytes()
        self.image_pub.publish(msg)
    
    def publish_boxes(self, boxes):
        msg = String()
        msg.data = str(boxes)
        self.boxes_pub.publish(msg)
    
    def publish_classes(self, classes):
        msg = String()
        msg.data = str(classes)
        self.classes_pub.publish(msg)
    

def main(args=None):
    rclpy.init(args=args)
    world_cam = RobotCam()
    rclpy.spin(world_cam)
    rclpy.shutdown()