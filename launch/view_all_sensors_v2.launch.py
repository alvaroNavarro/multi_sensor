from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (IncludeLaunchDescription, 
                            DeclareLaunchArgument,
                            TimerAction)
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    ld = LaunchDescription()
    
    ld.add_action(DeclareLaunchArgument('cam_names',   default_value='[zed_front, zed_left, zed_right]'))
    ld.add_action(DeclareLaunchArgument('cam_models',  default_value='[zed2, zed2, zed2]'))    
    ld.add_action(DeclareLaunchArgument('cam_serials', default_value='[24605482, 24749858, 28465220]'))
    
    # Address for right_camera = 28465220        
    
    # Zed node
    cameras_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("zed_multi_camera"),'/launch','/zed_multi_camera.launch.py']),
        launch_arguments=[
            ('cam_names',   LaunchConfiguration('cam_names')),
            ('cam_models',  LaunchConfiguration('cam_models')),
            ('cam_serials', LaunchConfiguration('cam_serials'))
        ]                
    )
    
    # Ouster node
    ouster_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ouster_ros"), '/launch', '/driver.launch.py'
        ])
    )        
    
    # GPS_IMU node
    gps_imu_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("gps_imu"), '/launch', '/gps_imu_driver.launch.py'
        ])
    )
    
    # Rviz2 Configurations to be loaded by ZED Node
    rviz_config = 'rviz_visualization'
    config_rviz2 = os.path.join(
        get_package_share_directory('multi_sensor'),
        'rviz',
        rviz_config + '.rviz'
    )
    
    # # Rviz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        output='screen',
        arguments=[['-d'], [config_rviz2]],
    )
    
    ld.add_action(cameras_launch)
    ld.add_action(ouster_launch)
    ld.add_action(gps_imu_launch)
    ld.add_action(rviz_node)
    
    return ld
    