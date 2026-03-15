from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = "description"

    urdf_file = PathJoinSubstitution(
        [FindPackageShare(package_name), "urdf", "robot.urdf.xacro"]
    )

    robot_description_content = Command(
        [
            "xacro ",
            urdf_file,
            " use_sim:=true",
        ]
    )

    robot_description = {"robot_description": ParameterValue(robot_description_content, value_type=str)}

    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    jsp_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

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

    return LaunchDescription([
        DeclareLaunchArgument(
            name="use_sim_time",
            default_value="false", # use_sim_time=false for rviz (otherwise tf issues)
            description="Use simulation (Gazebo) clock if true"
        ),
        rsp_node,
        jsp_node,
        rviz_node,
    ])