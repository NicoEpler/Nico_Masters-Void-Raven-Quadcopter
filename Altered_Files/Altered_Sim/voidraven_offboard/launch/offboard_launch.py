#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    yaml_file_path = '/home/nico/ros2_ws/src/voidraven_offboard/resource'
    return LaunchDescription([
        Node(
            package='voidraven_offboard',
            executable='position_command_input',
            name='position_command_input',
            prefix='gnome-terminal --'
        ),
        Node(
            package='voidraven_offboard',
            executable='position_control',
            name='position_control',
            prefix='gnome-terminal --'
        ),
        Node(
            package='voidraven_offboard',
            executable='visualizer',
            name='visualizer'
        ),
        Node(
            package='voidraven_offboard',
            executable='terminal_launches',
            name='terminal_launches',
            prefix='gnome-terminal --'
        ),
        # Bridge ROS topics and Gazebo messages for establishing communication
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            parameters=[{
                'config_file': os.path.join(yaml_file_path, 'ros_gz_bridge.yaml'),
                'qos_overrides./tf_static.publisher.durability': 'transient_local',
                'use_sim_time': True,
            }],
            output='screen'
        )
    ])
