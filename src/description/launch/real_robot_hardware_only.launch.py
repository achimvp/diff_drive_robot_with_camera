# Start the real robot with ros2_control controllers and broadcasters
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    package_name = "description"

    # Load the robot description from the xacro file
    urdf_file = PathJoinSubstitution(
        [FindPackageShare(package_name), "urdf", "robot.urdf.xacro"]
    )

    robot_description_content = Command(
        [
            "xacro ",
            urdf_file,
            " use_gazebo:=false",
        ]
    )

    robot_description = ParameterValue(robot_description_content, value_type=str)

    # Publish the robot pdescription using robot_state_publisher
    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    # Start Gazebo with the specified world file
    # pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    # world_file = PathJoinSubstitution(
    #     [FindPackageShare('description'), "gazebo", "simple_world.sdf"]
    # )
    
    # gz_sim = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
    #     launch_arguments={'gz_args': world_file, 'shutdown_on_exit': 'true'}.items(),
    # )

    # (Optional) Start RViz to visualize the robot
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", PathJoinSubstitution(
            [FindPackageShare(package_name), "config", "rviz.yaml"]
        )],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare(package_name), "config", "ros2_control.yaml"]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
    )

    # Spawn the robot in Gazebo
    # spawn = Node(package='ros_gz_sim', executable='create',
    #     parameters=[{
    #         'name': 'boxbot',
    #         'x': 0.0,
    #         'z': 0.2,
    #         'Y': 0.0,
    #         'topic': '/robot_description'}],
    #     output='screen')

    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen'
    )
    load_imu_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'imu_sensor_broadcaster'],
        output='screen'
    )
    load_camera_body_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'camera_body_controller'],
        output='screen'
    )
    load_diff_drive_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'diff_drive_controller'],
        output='screen'
    )
    # Gazebo ROS bridge for joint states
    # gz_ros_bridge_node = Node(
    #     package='ros_gz_bridge',
    #     executable='parameter_bridge',
    #     parameters=[
    #         {'config_file': PathJoinSubstitution([FindPackageShare(package_name), 'config', 'ros2_control_gz_bridge.yaml']),
    #         'qos_overrides./tf_static.publisher.durability': 'transient_local',
    #         }
    #     ],
    #     output='screen'
    # )


    return LaunchDescription([
        DeclareLaunchArgument(
            name="use_sim_time",
            default_value="false", # use_sim_time=false for rviz (otherwise tf issues)
            description="Use simulation (Gazebo) clock if true"
        ),
        # gz_sim,
        # spawn,
        control_node,
        rsp_node,
        # jsp_node,
        # rviz_node,
        # gz_ros_bridge_node,
        load_joint_state_broadcaster,
        load_imu_broadcaster,
        load_camera_body_controller,
        load_diff_drive_controller,
    ])