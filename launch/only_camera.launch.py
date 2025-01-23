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
    num_cams = int(camera.perform(context))
    
    if num_cams > 3:
        return [
            LogInfo(msg=TextSubstitution(
                text='The number of cameras chosen is incorrect.'))
        ]
        
    if num_cams == 1:
        default_value_names   = '[zed_front]'
        default_value_models  = '[zed2]'
        default_value_serials = '[24605482]'
        
    elif num_cams == 2:    
        default_value_names   = '[zed_front, zed_left]'
        default_value_models  = '[zed2, zed2]'
        default_value_serials = '[24605482, 24749858]'
        
    elif num_cams == 3:    
        default_value_names   = '[zed_front, zed_left, zed_right]'
        default_value_models  = '[zed2, zed2, zed2]'
        default_value_serials = '[24605482, 24749858, 28465220]'              
    
    cam_names   = DeclareLaunchArgument('cam_names',   default_value=default_value_names)
    cam_models  = DeclareLaunchArgument('cam_models',  default_value=default_value_models)    
    cam_serials = DeclareLaunchArgument('cam_serials', default_value=default_value_serials)
    
    actions = [cam_names, cam_models, cam_serials]  
    
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
    
    # Rviz2 Configurations to be loaded by ZED Node
    if num_cams == 1:
        rviz_config = 'rviz_visualization_cameras_1'
    elif num_cams == 2:    
        rviz_config = 'rviz_visualization_cameras_2'
    elif num_cams == 3:
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
