from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    ld = LaunchDescription()
    
    # Ouster node
    ouster_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ouster_ros"), '/launch', '/driver.launch.py'
        ])
    )
    
    # Rviz2 Configurations to be loaded by ZED Node
    rviz_config = 'rviz_visualization_lidar'
    config_rviz2 = os.path.join(
        get_package_share_directory('multi_sensor'),
        'rviz',
        rviz_config + '.rviz'
    )
    
    # Rviz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        output='screen',
        arguments=[['-d'], [config_rviz2]],
    )
    
    ld.add_action(ouster_launch)
    ld.add_action(rviz_node)
    
    return ld