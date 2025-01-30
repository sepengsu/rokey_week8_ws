from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
import os
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = 'week8_gazebo'
    pkg_dir = FindPackageShare(pkg_name).find(pkg_name)

    # urdf_path = os.path.join(pkg_dir, 'urdf', 'turtlebot3_waffle.urdf')
    urdf_path = os.path.join(pkg_dir, 'urdf', 'teslaModel3.urdf')

    # 로봇 상태 퍼블리셔
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[urdf_path]
    )

    # 조인트 상태 퍼블리셔
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # controller_manager 실행
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[{'use_sim_time': True}, os.path.join(pkg_dir, 'config', 'controllers.yaml')],
        output='screen'
    )

    # rviz2 실행
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_dir, 'rviz', 'show_model.rviz')]
    )
    return LaunchDescription([
        robot_state_publisher_node,
        # joint_state_publisher_node,
        # controller_manager_node,
        rviz2_node 
    ])
