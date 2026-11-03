import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def load_yaml(package_share, file_name):
    file_path = os.path.join(package_share, 'config', file_name)
    with open(file_path, 'r', encoding='utf-8') as yaml_file:
        return yaml.safe_load(yaml_file)


def generate_launch_description():
    package_name = 'one_joint_robot_description'
    package_share = get_package_share_directory(package_name)

    xacro_file = os.path.join(
        package_share, 'urdf', 'one_joint_robot.urdf.xacro'
    )
    srdf_file = os.path.join(
        package_share, 'config', 'moveit_robot.srdf'
    )

    with open(srdf_file, 'r', encoding='utf-8') as srdf:
        robot_description_semantic = srdf.read()

    robot_description = {
        'robot_description': ParameterValue(
            Command(['xacro ', xacro_file]), value_type=str
        )
    }
    semantic_description = {
        'robot_description_semantic': robot_description_semantic
    }

    joint_limits = load_yaml(package_share, 'moveit_joint_limits.yaml')
    ompl_config = load_yaml(package_share, 'moveit_ompl_planning.yaml')
    moveit_controllers = load_yaml(package_share, 'moveit_controllers.yaml')

    planning_pipelines = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl'
    }
    ompl_parameters = {'ompl': ompl_config}
    robot_description_planning = {
        'robot_description_planning': joint_limits
    }

    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01
    }

    planning_scene_monitor = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True
    }

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            semantic_description,
            robot_description_planning,
            planning_pipelines,
            ompl_parameters,
            moveit_controllers,
            trajectory_execution,
            planning_scene_monitor,
            {'use_sim_time': True}
        ]
    )

    return LaunchDescription([move_group_node])
