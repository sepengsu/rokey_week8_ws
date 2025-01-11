from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 설치된 경로에서 월드 파일 참조
    world_file = PathJoinSubstitution([
        FindPackageShare('turtlebot3_multi_robot'),
        'worlds',
        'week8_world.world'
    ])

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file],
            output='screen'
        )
    ])
