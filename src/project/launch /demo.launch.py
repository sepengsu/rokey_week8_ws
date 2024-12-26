from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Node 1: Minimal Publisher
    node1 = Node(
        package='project', 
        executable='minimal_publisher', # 실행 파일 또는 Python 모듈 이름
        name='minimal_publisher',     # 노드 이름
        output='screen'               # 출력 옵션
    )

    # Node 2: Minimal Subscriber
    node2 = Node(
        package='my_python_pkg',      # 패키지 이름
        executable='minimal_subscriber', # 실행 파일 또는 Python 모듈 이름
        name='minimal_subscriber',   # 노드 이름
        output='screen'
    )

    return LaunchDescription([
        node1,
        node2,
    ])
