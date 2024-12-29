import cv2

class NodeFunction:
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
    def control(self):
        pass

    def db_open(self):
        pass
