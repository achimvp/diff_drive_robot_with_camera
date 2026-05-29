# Start the real robot with ros2_control controllers and broadcasters
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    package_name = "boxbot_bringup"

    # Load the robot description from the xacro file
    urdf_file = PathJoinSubstitution(
        [FindPackageShare("description"), "urdf", "robot.urdf.xacro"]
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

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare(package_name), "config", "ros2_control.yaml"]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
    )

    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager', '--service-call-timeout', '30'],
    )
    load_imu_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['imu_sensor_broadcaster', '--controller-manager', '/controller_manager', '--service-call-timeout', '30'],
    )
    load_camera_body_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['camera_body_controller', '--controller-manager', '/controller_manager'],
    )
    load_diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
    )
    
    delay_imu_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_imu_broadcaster],
        )
    )

    delay_controllers = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_imu_broadcaster,
            on_exit=[load_camera_body_controller, load_diff_drive_controller],
        )
    )

    camera_node = Node(
        package="v4l2_camera",
        executable="v4l2_camera_node",
        output="screen",
        parameters=[{
            "image_size": [640,480],
            "camera_frame_id": "camera_link_optical"
        }]
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
        control_node,
        rsp_node,
        camera_node,
        load_joint_state_broadcaster,
        delay_imu_broadcaster,
        delay_controllers,
    ])