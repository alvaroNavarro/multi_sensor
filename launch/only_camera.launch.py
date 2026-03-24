from launch import LaunchDescription, LaunchContext
from launch_ros.actions import Node
from launch.actions import (IncludeLaunchDescription, 
                            DeclareLaunchArgument,
                            LogInfo,
                            OpaqueFunction)

from launch.substitutions import (LaunchConfiguration,
                                  TextSubstitution)

from launch_ros.substitutions import FindPackageShare                                      
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os
from ament_index_python.packages import get_package_share_directory

    
def launch_setup(context, *args, **kwargs):
    
    camera = LaunchConfiguration('camera')
    camera_type = str(camera.perform(context))
    
    actions=[]
    
    params = os.path.join(
    	get_package_share_directory('multi_sensor'),
    	'config',
    	'params.yaml'
    )
        
    zed_parameters = [
       params,
       {
           'camera': camera_type
       }
    ]

    # Zed node
    cameras_launch = Node(
        package='multi_sensor',
        executable='zed_camera_tf',
        name='Zed_node',
        output='screen',
        parameters=zed_parameters
    )
    
    # Rviz2 Configurations to be loaded by ZED Node
    if camera_type == "center":
        rviz_config = 'rviz_visualization_cameras_1'
    elif camera_type == "left":    
        rviz_config = 'rviz_visualization_cameras_2'
    elif camera_type == "right":
        rviz_config = 'rviz_visualization_cameras_all'    
        
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
    
    actions.append(cameras_launch)
    actions.append(rviz_node)
    
    return actions
    
def generate_launch_description():    
    
    ld = LaunchDescription()    
    ld.add_action(OpaqueFunction(function=launch_setup))
        
    return ld    
