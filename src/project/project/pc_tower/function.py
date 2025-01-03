import cv2

ROBOT_CLASS_DICT = {
    0: 'car',
    1: 'dummy'
    }

class WorldFindCar:
    '''
    '''
class AmrFunction:
    '''
    pc_tower의 tower_node.py에서 사용되는 함수들을 모아놓은 클래스
    Node의 attribute들은 아래와 같다.
    - robot_image: 로봇 카메라 이미지
    - robot_class: 로봇 카메라 클래스
    - robot_box: 로봇 카메라 박스
    - world_image: 월드 카메라 이미지
    - world_class: 월드 카메라 클래스
    - world_box: 월드 카메라 박스
    - world_db: 월드 데이터베이스 핸들러
    '''

    def find_car(self):
        '''
        robot camera에서 차량을 찾는 함수
        box: x, y, w, h
        '''
        boxes = self.robot_box # 로봇 카메라 박스 
        classes = self.robot_class # 로봇 카메라 클래스
        for box, class_id in zip(boxes, classes):
            if ROBOT_CLASS_DICT[class_id] == 'car':
                x,y = box[0], box[1]
                return box
        return None
            
    def calculate_distance(self, box):
        '''
        차량과의 거리를 계산하는 함수
        '''
        x, y, w, h = box
        return h**2  # 임시로 h^2로 설정 --> w는 무시
    
    def calculate_error(self, box):
        '''
        차량과의 각도, 거리를 계산하여 각각 반환하는 함수
        '''
        x, y, w, h = box
        z = self.calculate_distance(box) # 거리
        x_range = self.robot_image.shape[1] # 로봇 카메라 이미지의 너비
        return (x - x_range/2), z
    
    def get_velocity(self, error):
        '''
        error를 받아서 x,y,w 값을 반환하는 함수
        '''
        x, z = error
        p_angle = 0.1
        p_velocity = 0.1

        angle = p_angle * x
        velocity = p_velocity * z
        return angle, velocity
    
    def amr_function(self):
        '''
        전체 함수를 실행하는 함수
        '''
        box = self.find_car()
        if box is None:
            return 0, 0
        error = self.calculate_error(box)
        return self.get_velocity(error)
    


class MakeCmd:
    '''
    control_node에 command를 보내는 클래스
    '''



    

