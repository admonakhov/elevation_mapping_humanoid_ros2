import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    elevation_share = get_package_share_directory('elevation_mapping')
    fast_lio_share = get_package_share_directory('fast_lio')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_fast_lio = LaunchConfiguration('start_fast_lio')
    start_rviz = LaunchConfiguration('rviz')
    fast_lio_config = LaunchConfiguration('fast_lio_config')
    rviz_config = LaunchConfiguration('rviz_config')

    elevation_params = [
        os.path.join(elevation_share, 'config', 'robots', 'livox_fast_lio.yaml'),
        os.path.join(elevation_share, 'config', 'elevation_maps', 'long_range.yaml'),
        os.path.join(elevation_share, 'config', 'postprocessing', 'postprocessor_pipeline.yaml'),
        {'use_sim_time': use_sim_time},
    ]

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'start_fast_lio',
            default_value='true',
            description='Start fast_lio, which consumes /livox/lidar and /livox/imu.'),
        DeclareLaunchArgument(
            'fast_lio_config',
            default_value='mid360.yaml',
            description='fast_lio config file under fast_lio/config.'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(elevation_share, 'rviz2', 'custom_rviz2.rviz')),

        Node(
            package='fast_lio',
            executable='fastlio_mapping',
            name='fastlio_mapping',
            parameters=[
                PathJoinSubstitution([fast_lio_share, 'config', fast_lio_config]),
                {'use_sim_time': use_sim_time},
            ],
            output='screen',
            condition=IfCondition(start_fast_lio),
        ),

        Node(
            package='pose_publisher',
            executable='pose_publisher',
            name='pose_publisher',
            parameters=[{
                'publish_frequency': 30.0,
                'map_frame': 'camera_init',
                'base_frame': 'body',
                'topic_republish': '/pose',
                'use_sim_time': use_sim_time,
            }],
            output='screen',
        ),

        Node(
            package='elevation_mapping',
            executable='elevation_mapping',
            name='elevation_mapping',
            parameters=elevation_params,
            output='screen',
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            arguments=['-d', rviz_config],
            condition=IfCondition(start_rviz),
            output='screen',
        ),
    ])
