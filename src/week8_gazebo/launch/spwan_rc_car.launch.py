from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable, ExecuteProcess
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Package and file paths
    pkg_name = 'week8_gazebo'
    pkg_dir = FindPackageShare(pkg_name).find(pkg_name)

    gazebo_model_path = PathJoinSubstitution([pkg_dir, 'models'])
    gazebo_plugin_path = PathJoinSubstitution(['/opt/ros/humble/lib'])

    world_file = PathJoinSubstitution([pkg_dir, 'worlds', 'week8_world.world'])
    sdf_path = PathJoinSubstitution([pkg_dir, 'models', 'rc_car', 'car_model.sdf'])

    # Robot parameters
    robot_name = LaunchConfiguration('robot_name', default='rc_car')
    robot_namespace = LaunchConfiguration('namespace', default='/rc_car')
    robot_x_pose = LaunchConfiguration('x_pose', default='0.0')
    robot_y_pose = LaunchConfiguration('y_pose', default='0.0')
    robot_z_pose = LaunchConfiguration('z_pose', default='0.01')

    # Gazebo process with additional physics plugin
    gazebo_process = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_file, '-s', 'libgazebo_ros_factory.so', '-s', 'libgazebo_ros_init.so'],
        output='screen'
    )

    # Joint State Publisher Node (removed URDF dependency)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        namespace=robot_namespace,
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_gui': True}]
    )

    # Spawn RC Car Node
    spawn_rc_car = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-file', sdf_path,
            '-entity', robot_name,
            '-robot_namespace', robot_namespace,
            '-x', robot_x_pose, '-y', robot_y_pose, '-z', robot_z_pose, '-Y', '0.0'
        ],
        output='screen'
    )

    return LaunchDescription([
        # Set environment variables
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', gazebo_plugin_path),

        # Launch Joint State Publisher
        joint_state_publisher,
        # Launch Gazebo
        gazebo_process,
        spawn_rc_car
    ])
