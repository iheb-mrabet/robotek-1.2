from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gui = LaunchConfiguration("gui")
    use_sim_time = LaunchConfiguration("use_sim_time")

    control_config = PathJoinSubstitution(
        [FindPackageShare("mock_robot_bringup"), "config", "control.yaml"]
    )
    mission_config = PathJoinSubstitution(
        [FindPackageShare("mock_robot_bringup"), "config", "mission.yaml"]
    )

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("mock_robot_gazebo"), "launch", "simulation.launch.py"]
            )
        ),
        launch_arguments={"gui": gui, "use_sim_time": use_sim_time}.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("gui", default_value="false"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            simulation,
            Node(
                package="mock_robot_control",
                executable="waypoint_controller",
                name="waypoint_controller",
                output="screen",
                parameters=[control_config, {"use_sim_time": use_sim_time}],
            ),
            Node(
                package="mock_robot_control",
                executable="safety_controller",
                name="safety_controller",
                output="screen",
                parameters=[control_config, {"use_sim_time": use_sim_time}],
            ),
            Node(
                package="mock_robot_behavior",
                executable="mission_manager",
                name="mission_manager",
                output="screen",
                parameters=[mission_config, {"use_sim_time": use_sim_time}],
            ),
        ]
    )
