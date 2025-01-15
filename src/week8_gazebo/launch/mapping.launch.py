from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import SetEnvironmentVariable
import os
from launch_ros.actions import Node
pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
pkg_cartographer_ros = get_package_share_directory('turtlebot3_cartographer')
pkg_dir = get_package_share_directory('week8_gazebo')
world = os.path.join(pkg_dir, 'worlds', 'week8_world.world')
robots = [
{'name': 'robot', 'x_pose': '1.8', 'y_pose': '1.2', 'z_pose': '0.01'},]
TURTLEBOT3_MODEL = 'burger'
x_pose =robots[0]['x_pose']
y_pose =robots[0]['y_pose']
z_pose =robots[0]['z_pose']
urdf = os.path.join(pkg_dir, 'urdf', 'turtlebot3_burger.urdf')
sdf = os.path.join(pkg_dir, 'models', 'turtlebot3_burger', 'model.sdf')

def generate_launch_description():

    ld = LaunchDescription()
    # Gazebo 환경 설정
    gazebo_model_path = PathJoinSubstitution([FindPackageShare('week8_gazebo'),'models'])
    gazebo_plugin_path = PathJoinSubstitution(['/opt/ros/humble/lib'])
    ld.add_action(SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path))
    ld.add_action(SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', gazebo_plugin_path))

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    # 로봇 상태 게시 노드 만들기
    robot_state_publisher_cmd = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, {'robot_description': robot_desc}],
        )
    
    # 터틀봇 스폰 노드 만들기
    spawn_turtlebot_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', TURTLEBOT3_MODEL,
            '-file', sdf,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.01'
        ],
        output='screen',
    )

    # cartographer_node 만들기 위한 
    # Add the commands to the launch description
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_turtlebot_cmd)
    # cartographer launch 파일 추가
    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_cartographer_ros, 'launch', 'cartographer.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )
    ld.add_action(cartographer_launch)

    
    # 맵 저장 노드 추가
    map_saver_node = Node(
        package='nav2_map_server',
        executable='map_saver_cli',
        name='map_saver',
        output='screen',
        arguments=['-f', os.path.join(pkg_dir, 'maps', 'saved_map')]
    )
    ld.add_action(map_saver_node)

    return ld