from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    ld = LaunchDescription()
    
    # Imu node
    imu_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ros2_xsens_mti_driver"), '/launch', '/xsens_mti_node.launch.py'
        ])
    )
    
    # Save imu data node
    save_imu_data_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("imu_values"), '/launch', '/imu_values.launch.py'
        ])
    )
    
    # Display de imu frame in rviz
    imu_display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ros2_xsens_mti_driver"), '/launch', '/display.launch.py'
        ])
    )
    
    ld.add_action(imu_launch)
    ld.add_action(save_imu_data_launch)
    ld.add_action(imu_display_launch)
    
    return ld