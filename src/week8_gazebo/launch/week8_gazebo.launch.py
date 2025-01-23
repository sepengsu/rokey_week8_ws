import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition
import launch.logging
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
nav2_bt_navigator_dir = get_package_share_directory('nav2_bt_navigator')
package_dir = get_package_share_directory('week8_gazebo')
gazebo_model_path = PathJoinSubstitution([FindPackageShare('week8_gazebo'),'models'])
gazebo_plugin_path = PathJoinSubstitution(['/opt/ros/humble/lib'])

robots = [
# {'name': 'robot', 'x_pose': '1.8', 'y_pose': '1.2', 'z_pose': '0.01'},
{'name': 'rc_car', 'x_pose': '1.8', 'y_pose': '1.2', 'z_pose': '0.01'},
]
TURTLEBOT3_MODEL = 'burger'
world = os.path.join(package_dir,'worlds', 'week8_world.world')

urdf_list = [os.path.join(package_dir, 'urdf', 'turtlebot3_' + TURTLEBOT3_MODEL + '.urdf')] # turtlebot3_burger.urdf
urdf_list = [os.path.join(package_dir, 'urdf', 'rc_car.urdf')] 

sdf_list = [os.path.join(package_dir, 'models', 'turtlebot3_'+ TURTLEBOT3_MODEL, 'model.sdf')] # turtlebot3_burger.sdf
sdf_list = [os.path.join(package_dir, 'models', 'rc_car', 'car_model.sdf')] # rc_car.sdf

def generate_launch_description():
    ld = LaunchDescription()

    # 환경 변수 설정
    ld.add_action(SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path))
    ld.add_action(SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', gazebo_plugin_path))
    # Names and poses of the robots

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time', default_value=use_sim_time, description='Use simulator time'
    )

    enable_drive = LaunchConfiguration('enable_drive', default='false')
    declare_enable_drive = DeclareLaunchArgument(
        name='enable_drive', default_value=enable_drive, description='Enable robot drive node'
    )

    enable_rviz = LaunchConfiguration('enable_rviz', default='true')
    declare_enable_rviz = DeclareLaunchArgument(
        name='enable_rviz', default_value=enable_rviz, description='Enable rviz launch'
    )

    nav_launch_dir = os.path.join(package_dir, 'launch', 'nav2_bringup')

    rviz_config_file = LaunchConfiguration('rviz_config_file')
    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(
            package_dir, 'rviz', 'multi_nav2_default_view.rviz'))


    # 가제보 서버와 클라이언트 노드 추가
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world,'verbose': 'true',
                          '-s': 'libgazebo_ros_factory.so',}.items(),
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gzclient.launch.py')
        ),
    )

    params_file = LaunchConfiguration('nav_params_file')
    declare_params_file_cmd = DeclareLaunchArgument(
        'nav_params_file',
        default_value=os.path.join(package_dir, 'params', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes')
    
    # 가제보 서버와 클라이언트 노드 추가 
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_enable_drive)
    ld.add_action(declare_enable_rviz)
    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
 
    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]
    map_server=Node(package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': os.path.join(package_dir, 'map', 'map.yaml')},],
        remappings=remappings)

    map_server_lifecyle=Node(package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_map_server',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},{'autostart': True},
                        {'node_names': ['map_server']}])
    
    # 맵 서버 노드 추가
    ld.add_action(map_server)
    ld.add_action(map_server_lifecyle)

    ######################

    # Remapping is required for state publisher otherwise /tf and /tf_static 
    # will get be published on root '/' namespace
    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    last_action = None
    # Spawn turtlebot3 instances in gazebo
    for robot, urdf, sdf in zip(robots, urdf_list, sdf_list):
        namespace = [ '/' + robot['name'] ]

        # Create state publisher node for that instance
        turtlebot_state_publisher = Node(
            package='robot_state_publisher',
            namespace=namespace,
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,'publish_frequency': 10.0}],
            remappings=remappings,
            arguments=[urdf],
        )

        # 각 로봇의 sdf 파일을 이용하여 gazebo에 로봇을 생성
        spawn_turtlebot3_burger = Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-file', sdf,
                '-entity', robot['name'],
                '-robot_namespace', namespace,
                '-x', robot['x_pose'], '-y', robot['y_pose'],
                '-z', '0.01', '-Y', '0.0','-unpause',
            ],
            output='screen',
        )

        bringup_cmd = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav_launch_dir, 'bringup_launch.py')),
                    launch_arguments={  
                                    'slam': 'False',
                                    'namespace': namespace,
                                    'use_namespace': 'True',
                                    'map': '','map_server': 'False',
                                    'params_file': params_file,
                                    'default_bt_xml_filename': os.path.join(
                                        nav2_bt_navigator_dir,
                                        'behavior_trees', 'navigate_w_replanning_and_recovery.xml'),
                                    'autostart': 'true','use_sim_time': use_sim_time, 'log_level': 'warn'}.items()
        )

        if last_action is None:
            # First robot에 대한 처리
            ld.add_action(turtlebot_state_publisher)
            ld.add_action(spawn_turtlebot3_burger)
            ld.add_action(bringup_cmd)

        else:
            # RegisterEventHandler를 사용하여 이전 로봇 생성이 완료된 후에만 다음 로봇 생성을 수행합니다.
            # spawn_entity를 단순히 ld.add_action으로 호출하면 병렬 실행으로 인해 문제가 발생합니다.
            spawn_turtlebot3_event = RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=last_action,
                    on_exit=[spawn_turtlebot3_burger,
                            turtlebot_state_publisher,
                            bringup_cmd],
                )
            )

            ld.add_action(spawn_turtlebot3_event)

        # 다음 RegisterEventHandler를 위해 마지막 인스턴스를 저장
        last_action = spawn_turtlebot3_burger
    ######################

    ######################
    
    # 마지막 로봇이 생성된 후 rviz 노드와 drive 노드를 시작합니다.
    for robot in robots:

        namespace = [ '/' + robot['name'] ]

        # 초기 위치 토픽 발행 호출 생성: 초기 위치는 위의 pose에서 가져옵니다.
        # 이는 로봇의 초기 위치를 맵에 설정하는 데 필요합니다.
        # message = '{header: {frame_id: map}, pose: {pose: {position: {x: ' + \
        #     robot['x_pose'] + ', y: ' + robot['y_pose'] + \
        #     ', z: 0.1}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0000000}}, }}'
        message = '{header: {frame_id: map}, pose: {pose: {position: {x: ' + \
            '0.0' + ', y: ' + '0.0' + \
            ', z: 0.01}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0000000}}, }}'

        initial_pose_cmd = ExecuteProcess(
            cmd=['ros2', 'topic', 'pub', '-t', '3', '--qos-reliability', 'reliable', namespace + ['/initialpose'],
                'geometry_msgs/PoseWithCovarianceStamped', message],
            output='screen'
        )

        rviz_cmd = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav_launch_dir, 'rviz_launch.py')),
                launch_arguments={'use_sim_time': use_sim_time, 
                                  'namespace': namespace,
                                  'use_namespace': 'True',
                                  'rviz_config': rviz_config_file, 'log_level': 'warn'}.items(),
                                   condition=IfCondition(enable_rviz)
                                    )

        drive_turtlebot3_burger = Node(
            package='turtlebot3_gazebo', executable='turtlebot3_drive',
            namespace=namespace, output='screen',
            condition=IfCondition(enable_drive),
        )

        # Use RegisterEventHandler to ensure next robot rviz launch happens 
        # only after all robots are spawned
        post_spawn_event = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=last_action,
                on_exit=[initial_pose_cmd, rviz_cmd, drive_turtlebot3_burger],
            )
        )

        # Perform next rviz and other node instantiation after the previous intialpose request done
        last_action = initial_pose_cmd

        ld.add_action(post_spawn_event)
        ld.add_action(declare_params_file_cmd)
    ######################

    return ld