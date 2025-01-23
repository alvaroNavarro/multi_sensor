# Multi Sensor Package
 This package allows monitoring the performance of the sensors depicted in the Figure 1 (Multi sensor system) of individual manner and visualized in RVIZ. 
 
![multi-sensor system](https://github.com/user-attachments/assets/099efe78-38a7-42b2-87e6-1d05bfb00977)
                                           Figure 1. Multi sensor system

 ## Pre-Requisites
 - Ensure to have installled the drivers for the camera (In our case we are using ZED2 camera from StereoLabs).
   Please check the github repo: https://github.com/stereolabs/zed-multi-camera.git
   Remark: Check the serial number of each camera

 - Ensure to have installed the drivers for the Ouster LiDAR sensor.
   Please check the github repo: https://github.com/ouster-lidar/ouster-ros.git

 - Ensure to have installed the drivers for the XSense IMU.
   Please check the github repo: https://github.com/DEMCON/ros2_xsens_mti_driver.git
   Remark: This packet is compiled to ROS Foxy distribution. We have tested it in ROS Humble and only can get the heading information

 - Add the package gps_imu that is found in the following repository:
   https://github.com/alvaroNavarro/gps_imu   -> Subcribe to topic of GPS /navsat/fix and IMU /imu/data
   https;//github.com/alvaroNavarro/gps_node  -> Open a socket to receive the data from the mobile app and publish the data into the topic /navsat/fix
    
 ## Usage
 1. ZED package:
    - ros2 launch multi-sensor only_camera.launch.py camera:=<Number_of_camera>
      where Number of camera is:
           1. Front camera
           2. Front camera and left camera
           3. All cameras

2. Ouster package:
   - ros2 launch multi-sensor only_lidar.launch.py
  
3. IMU package
   - ros2 launch multi-sensor only_imu.launch.py   Do not forget to remove the USB permission  sudo chmod 777 /dev/ttyUSB0
  
4. All sensors
   To run all sensors, this packet contains a bash file located in the script folder. To use it do the following:
   
   - cd ~/ros2_ws/src/multi_sensor/scripts
   - sudo chmod 777 all_sensors.bash
   - ./all_sensors.bash

     This file check the permission for Xsense device. Once the node is closed, a question to save the gps and imu data will be arise.

```
function test() {
  console.log("This code will have a copy button to the right of it");
}
``` 
 
