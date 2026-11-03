import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_share = get_package_share_directory(
        'one_joint_robot_description'
    )

    xacro_file = os.path.join(
        package_share, 'urdf', 'one_joint_robot.urdf.xacro'
    )
    srdf_file = os.path.join(
        package_share, 'config', 'moveit_robot.srdf'
    )
    rviz_file = os.path.join(
        package_share, 'config', 'moveit.rviz'
    )

    with open(srdf_file, 'r', encoding='utf-8') as srdf:
        robot_description_semantic = srdf.read()

    robot_description = {
        'robot_description': ParameterValue(
            Command(['xacro ', xacro_file]), value_type=str
        )
    }

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='moveit_rviz',
        output='screen',
        arguments=['-d', rviz_file],
        parameters=[
            robot_description,
            {'robot_description_semantic': robot_description_semantic},
            {'use_sim_time': True}
        ]
    )

    return LaunchDescription([rviz_node])
