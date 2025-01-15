from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Gazebo 환경 설정
    gazebo_model_path = PathJoinSubstitution([FindPackageShare('week8_gazebo'),'models'])
    gazebo_plugin_path = PathJoinSubstitution(['/opt/ros/humble/lib'])

    # 월드 파일 경로 설정
    world_file = PathJoinSubstitution([
        FindPackageShare('week8_gazebo'),
        'worlds','week8_world.world'])

    # Gazebo 실행 프로세스
    gazebo_process = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_file],
        output='screen'
    )

    # 압축 노드 실행 (5초 딜레이)
    compressed_node = TimerAction(
        period=5.0,  # 5초 대기 후 실행
        actions=[
            Node(
                package='week8_gazebo',
                executable='compressed_node',
                name='compressed_node',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        # Gazebo 환경 변수 설정
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', gazebo_plugin_path),

        # Gazebo 실행
        gazebo_process,

        # 딜레이 후 노드 실행
        compressed_node,
    ])
