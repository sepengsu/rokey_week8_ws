import cv2
import numpy as np
import warnings
from collections import Counter
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

def max_color(crop_img):
    """
    이미지에서 가장 많은 색상을 찾아 반환
    """
    colors = crop_img.reshape(-1, crop_img.shape[-1])
    colors = [tuple(color) for color in colors] # (B, G, R) 형태로 변환
    color_counter = Counter(colors) # 색상 개수 세기
    most_common_color = color_counter.most_common(1)[0][0] # 가장 많은 색상(숫자)을 찾아 반환
    most_common_color = tuple(reversed(most_common_color)) # (R, G, B) 형태로 변환
    match_color = None
    for color, name in COLOR_MAP.items():
        if color == most_common_color:
            match_color = name
            break
    return most_common_color

COLOR_MAP = {
    (0, 0, 255): 'red',
    (0, 255, 0): 'green',
    (255, 0, 0): 'blue',
    (255, 255, 0): 'yellow',
    (255, 0, 255): 'magenta',
    (0, 255, 255): 'cyan',
    (255, 255, 255): 'white',
    (0, 0, 0): 'black'
}