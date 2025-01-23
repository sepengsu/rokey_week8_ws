from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Gazebo 환경 변수 설정
    pkg_path = get_package_share_directory('week8_gazebo')
    gazebo_model_path = os.path.join(pkg_path, 'models')
    gazebo_plugin_path = '/opt/ros/humble/lib'

    # Gazebo 월드 파일 경로 설정
    world_file = os.path.join(pkg_path, 'worlds', 'week8_world.world')

    # Gazebo 실행 프로세스
    gazebo_process = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so', world_file],
        output='screen'
    )

    # 스폰할 모델의 SDF 파일 경로 설정
    # sdf_file = os.path.join(pkg_path, 'models', 'rc_car', 'car_model.sdf')
    sdf_file = os.path.join(gazebo_model_path, 'turtlebot3_burger', 'model.sdf')
    if not os.path.exists(sdf_file):
        print(f"[ERROR] SDF file not found at {sdf_file}")
        raise FileNotFoundError(f"SDF file not found at {sdf_file}")

    # Gazebo에 모델 스폰 노드 설정
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'rc_car',    # 스폰할 모델 이름
            '-file', sdf_file,       # 모델 파일 경로
            '-x', '3.0',             # 초기 x 위치
            '-y', '3.0',             # 초기 y 위치
            '-z', '0.1',             # 초기 z 위치
        ],
        output='screen'
    )

    # Joint State Publisher 노드 추가
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # LaunchDescription에 설정 추가
    return LaunchDescription([
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', gazebo_plugin_path),
        gazebo_process,
        spawn_entity_node,
        joint_state_publisher_node,
    ])
