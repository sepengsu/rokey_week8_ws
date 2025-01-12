from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    # 설치된 경로에서 월드 파일 참조
    world_file = PathJoinSubstitution([
        FindPackageShare('week8_gazebo'),
        'worlds',
        'week8_world.world'
    ])
    
    return LaunchDescription([
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file],
            output='screen'
        ),

        Node(
            package='week8_gazebo',
            executable='compressed_node',  # 실행할 노드 파일
            name='compressed_node',  # 노드 이름
            output='screen',  # 로그 출력
        )
    ])
