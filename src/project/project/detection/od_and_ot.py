from ultralytics import YOLO
from ament_index_python.packages import get_package_share_directory
import os, torch, cv2
from collections import defaultdict

# yolo_dir = get_package_share_directory('project') + '/yolo'
yolo_dir = '/home/jaewon/rokey_week8_ws/src/project/yolo'
ROBOT_CLASS_DICT = {
    0: 'car',
    1: 'dummy'
    }

WORLD_CLASS_DICT = {
    0: 'car',
    }

def yolo_loading(cam_type):
    if cam_type == 'robot':
        class_dict = ROBOT_CLASS_DICT
        path =os.path.join(yolo_dir, 'robot_best.pt')
    elif cam_type == 'world':
        class_dict = WORLD_CLASS_DICT
        path = os.path.join(yolo_dir, 'world_best.pt')
    else:
        raise ValueError('cam_type must be either robot or world')
    yolo = YOLO(path)
    return yolo, class_dict


class Detection:
    def __init__(self, cam_type):
        self.yolo, self.class_dict = yolo_loading(cam_type)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def detect(self, frame):
        result = self.yolo.predict(frame, device=self.device,conf = 0.5,iou = 0.2)
        boxes, classes = self.convert_to_string(result)
        return boxes, classes

    def convert_to_string(self,outputs):
        '''
        YOLO를 이용하여 인식한 결과를 string으로 변환하는 함수
        outputs: YOLO를 이용하여 인식한 결과 (list 형태)
        반환: string으로 변환된 결과 (class_list, [x, y, w, h])
        '''
        if outputs is None or len(outputs) == 0:
            return "None" , "None"

        # YOLO 결과 처리
        result = outputs[0]  # 단일 이미지 결과 사용
        if not hasattr(result, "boxes") or result.boxes is None:
            return "None", "None"

        boxes = result.boxes.xywh  # 바운딩 박스 정보
        classes = result.boxes.cls  # 클래스 정보import warnings
        # 리스트로 변환
        boxes_list = boxes.tolist()
        boxes_list = [[round(coord, 2) for coord in box] for box in boxes_list] 

        classes_list = [int(cls) for cls in classes.tolist()]

        # 문자열로 변환
        boxes_str = str(boxes_list)
        classes_str = str(classes_list)
        return boxes_str, classes_str
    
from collections import Counter
class Tracking:
    def __init__(self, cam_type):
        # YOLO 모델 로드 및 클래스 맵 설정
        self.yolo, self.class_dict = yolo_loading(cam_type)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.history = defaultdict(lambda: [])


    def track(self, frame):
        """
        실시간 객체 탐지 및 추적 수행
        :param frame: 단일 프레임 이미지 (numpy array)
        :return: 추적된 객체가 포함된 프레임
        """
        # YOLO 탐지 수행
        results = self.yolo.track(frame, device=self.device, conf=0.5, iou=0.2,persist=True)

        # 탐지 결과를 문자열로 변환
        boxes, classes = self.convert_to_string(results)
        # 객체 이력 업데이트
        # self.update_history(track_ids, boxes)
        #그리기
        # frame = self.drawing(frame,results)
        print(f"boxes: {boxes}, classes: {classes}", type(boxes), type(classes))
        return boxes, classes, frame

    def convert_to_string(self,outputs):
        '''
        YOLO를 이용하여 인식한 결과를 string으로 변환하는 함수
        outputs: YOLO를 이용하여 인식한 결과 (list 형태)
        반환: string으로 변환된 결과 (class_list, [x, y, w, h])
        '''
        if outputs is None or len(outputs) == 0:
            return "None" , "None"

        # YOLO 결과 처리
        result = outputs[0]  # 단일 이미지 결과 사용
        if not hasattr(result, "boxes"):
            return "None", "None"

        boxes = result.boxes.xywh  # 바운딩 박스 정보
        classes = result.boxes.cls  # 클래스 정보
        ids = result.boxes.track_id  # 객체 ID 정보 

        # 리스트로 변환
        boxes_list = boxes.tolist()
        boxes_list = [[round(coord, 2) for coord in box] for box in boxes_list] 
        classes_list = [int(cls) for cls in classes.tolist()]
        track_ids = [int(track_id) for track_id in ids.tolist()]

        # 문자열로 변환
        boxes_str = str(boxes_list)
        classes_str = str(classes_list)
        track_ids_str = str(track_ids)

        return classes_str, boxes_str, track_ids_str
    
    def update_history(self, track_ids, boxes):
        """
        객체 이력 정보 업데이트
        :param track_ids: 객체 ID 리스트
        :param boxes: 객체 바운딩 박스 리스트
        """
        for track_id, box in zip(track_ids, boxes):
            self.history[track_id].append(box)
    def get_history(self):
        """
        객체 이력 정보 반환
        :return: 객체 이력 정보 (dict)
        """
        return self.history
    
    def drawing(self,frame,result):
        for box in result.xyxy:
            x1, y1, x2, y2 = [int(coord) for coord in box]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        return frame

# if __name__ == '__main__':
#     from function import get_index_of_cam
#     index = get_index_of_cam()
#     cap = cv2.VideoCapture(index)
#     detect = Detection('robot')
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             continue    
#         boxes, classes = detect.detect(frame)
#         boxes = eval(boxes)
#         classes = eval(classes)if __name__ == '__main__':
#     from function import get_index_of_cam
#     index = get_index_of_cam()
#     cap = cv2.VideoCapture(index)
#     detect = Detection('robot')
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             continue    
#         boxes, classes = detect.detect(frame)
#         boxes = eval(boxes)
#         classes = eval(classes)
#         if boxes == 'None' or classes == 'None':
#             pass
#         else:
#             for box, cls in zip(boxes, classes):
#                 x, y, w, h = box
#                 x, y, w, h = map(int, [x, y, w, h])
#                 class_name = detect.class_dict[cls]
#                 cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#                 cv2.putText(frame, class_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv2.destroyAllWindows()
#                 cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#                 cv2.putText(frame, class_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv2.destroyAllWindows()

if __name__ == '__main__':
    from function import get_index_of_cam
    index = get_index_of_cam()
    cap = cv2.VideoCapture(index)
    track = Tracking('robot')
    while True:
        ret, frame = cap.read()
        if not ret:
            continue    
        classes, boxes, frame = track.track(frame)
        boxes = eval(boxes)
        classes = eval(classes)
        if boxes == 'None' or classes == 'None':
            pass
        else:
            for box, cls in zip(boxes, classes):
                x, y, w, h = box
                x, y, w, h = map(int, [x, y, w, h])
                class_name = track.class_dict[cls]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()