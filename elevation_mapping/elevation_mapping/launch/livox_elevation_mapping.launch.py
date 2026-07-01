import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    elevation_share = get_package_share_directory('elevation_mapping')
    fast_lio_share = get_package_share_directory('fast_lio')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_fast_lio = LaunchConfiguration('start_fast_lio')
    start_filter = LaunchConfiguration('start_filter')
    start_visualization = LaunchConfiguration('start_visualization')
    start_rviz = LaunchConfiguration('rviz')
    fast_lio_config = LaunchConfiguration('fast_lio_config')
    rviz_config = LaunchConfiguration('rviz_config')

    elevation_params = [
        os.path.join(elevation_share, 'config', 'robots', 'humanoid_fast_lio.yaml'),
        os.path.join(elevation_share, 'config', 'postprocessing', 'postprocessor_pipeline.yaml'),
        {'use_sim_time': use_sim_time},
    ]

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'start_fast_lio',
            default_value='true',
            description='Start fast_lio, which consumes /utlidar/cloud_livox_mid360 and /utlidar/imu_livox_mid360.'),
        DeclareLaunchArgument(
            'start_filter',
            default_value='true',
            description='Start ROS2 port of pc_filter: /cloud_registered_body -> /cloud_registered/filtered.'),
        DeclareLaunchArgument(
            'start_visualization',
            default_value='true',
            description='Start grid_map_visualization nodes, like ROS1 visualization.launch.'),
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
            name='laserMapping',
            parameters=[
                PathJoinSubstitution([fast_lio_share, 'config', fast_lio_config]),
                {'use_sim_time': use_sim_time},
            ],
            output='screen',
            condition=IfCondition(start_fast_lio),
        ),

        Node(
            package='elevation_mapping_demos',
            executable='pc_filter.py',
            name='pointcloud_filter',
            parameters=[{
                'distance_threshold': -0.5,
                'input_topic': '/cloud_registered_body',
                'output_topic': '/cloud_registered/filtered',
                'target_frame': 'torso_link',
                'use_sim_time': use_sim_time,
            }],
            output='screen',
            condition=IfCondition(start_filter),
        ),

        Node(
            package='pose_publisher',
            executable='pose_publisher',
            name='node_pose_publisher',
            parameters=[{
                'publish_frequency': 10.0,
                'map_frame': 'odom_torso',
                'base_frame': 'torso_link',
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

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(elevation_share, 'launch', 'visualization.launch.py')),
            condition=IfCondition(start_visualization),
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
