import rclpy, cv2
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from project.detection import Detection
from std_msgs.msg import String
from project.database import DetectDBHandler
import time
from project.detection.function import max_color, get_index_of_cam
 

class WorldCam(Node):
    def __init__(self):
        super().__init__('world_cam')
        self.image_pub = self.create_publisher(CompressedImage, '/world_cam/image_raw/compressed', 5)
        self.boxes_pub = self.create_publisher(String, '/world_cam/boxes', 5)
        self.classes_pub = self.create_publisher(String, '/world_cam/classes', 5)
        self.description_pub = self.create_publisher(String, '/world_cam/description', 5) # 탐지된 물체 설명 (color, size, refind) 발행
        self.yolo = Detection('world')
        self.db = DetectDBHandler()
        self.db.create_table() # 테이블 생성 or 이미 존재하면 열기만 함
        self.frame = None
        self.cam_index = get_index_of_cam()
        self.create_timer(0.02,self.process) # 0.02초마다 process 함수 실행
    
    def process(self):
        cur_time = time.localtime() # 현재 시간 구하기
        cur_time = f'{cur_time.tm_year}-{cur_time.tm_mon}-{cur_time.tm_mday} {cur_time.tm_hour}:{cur_time.tm_min}:{cur_time.tm_sec}'
        self.get_frame()
        boxes, classes = self.yolo.detect(self.frame)
        boxes_list = eval(boxes) if boxes != "None" else []
        classes_list = eval(classes) if classes != "None" else []
        if len(boxes_list) > 0 and len(classes_list) > 0:

            self.db_save(boxes_list, classes_list, self.frame, cur_time)
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

    def db_save(self,cur_time, boxes, classes, frame):
        for box, class_ in zip(boxes, classes):
            self.db.insert(cur_time, box, class_, max_color(frame), frame.shape[:2], self.db.img_id, frame)
        
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
    world_cam = WorldCam()
    rclpy.spin(world_cam)
    rclpy.shutdown()