from ultralytics import YOLO
import os
import torch

def main():
    # 작업 디렉토리 설정
    if 'yolo' in os.listdir():
        os.chdir('yolo')

    # COCO 기반 사전 학습된 모델 사용 (YOLO11N)
    weights_path = './yolo11n.pt'  # Ultralytics 제공 사전 학습 가중치

    # 모델 로드
    yolo = YOLO(weights_path)

    # 데이터 경로 및 설정
    pwd = os.getcwd() 
    yaml = os.path.join(pwd, 'data_for_world/data.yaml')
    print(yaml)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # 학습 실행
    yolo.train(
        data=yaml,               # 데이터셋 정의 YAML 파일 경로
        imgsz=640,               # 입력 이미지 크기
        batch = 16,          # 배치 크기
        epochs=300,              # 학습 에포크 수
        weight_decay=0.0005,    # 가중치 감쇠
        device=device,           # 학습에 사용할 디바이스
        project='yolo_for_world', # 결과 저장 프로젝트 경로c
        name='v1',                # 학습 실행 이름
        lr0=0.01,                # 초기 학습률
        workers=8,              # 데이터 로드에 사용할 CPU 워커 수
        exist_ok=True,           # 프로젝트 폴더가 이미 존재할 경우 덮어쓰기
    )

if __name__ == '__main__':
    main()
