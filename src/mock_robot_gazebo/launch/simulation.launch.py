from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gui = LaunchConfiguration("gui")
    use_sim_time = LaunchConfiguration("use_sim_time")

    world_path = PathJoinSubstitution(
        [FindPackageShare("mock_robot_gazebo"), "worlds", "warehouse_world.sdf"]
    )
    bridge_config = PathJoinSubstitution(
        [FindPackageShare("mock_robot_gazebo"), "config", "bridge.yaml"]
    )
    model_path = PathJoinSubstitution(
        [
            FindPackageShare("mock_robot_description"),
            "urdf",
            "mock_delivery_robot.urdf.xacro",
        ]
    )
    robot_description = Command(["xacro ", model_path])

    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": ["-r ", world_path]}.items(),
        condition=IfCondition(gui),
    )
    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"])
        ),
        launch_arguments={"gz_args": ["-r -s ", world_path]}.items(),
        condition=UnlessCondition(gui),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("gui", default_value="false"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            gazebo_gui,
            gazebo_headless,
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[
                    {"robot_description": robot_description},
                    {"use_sim_time": use_sim_time},
                ],
            ),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name",
                    "mock_delivery_robot",
                    "-topic",
                    "robot_description",
                    "-x",
                    "0.0",
                    "-y",
                    "0.0",
                    "-z",
                    "0.12",
                ],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="ros_gz_bridge",
                parameters=[{"config_file": bridge_config}],
                output="screen",
            ),
        ]
    )
