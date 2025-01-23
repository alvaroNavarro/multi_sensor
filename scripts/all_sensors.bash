#!/bin/bash

source ~/ros2_ws/install/setup.bash
source /opt/ros/humble/setup.bash

cd ~/
PATH_TO_ROOT=$(pwd)
PATH_TO_DATA_FOLDER="${PATH_TO_ROOT}/Documents/data_gps_imu/"

echo "Checking whether the device is connected to port ttyUSB0..."
sleep 2

IMU_SERIAL="Xsens_MTi_USB_Converter_DB6YQZ20"

devs=$( (                                                              
for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev ); do    
    # ( to launch a subshell here                                      
    (                                                                  
        syspath="${sysdevpath%/dev}"                                   
        devname="$(udevadm info -q name -p $syspath)"                  
        [[ "$devname" == "bus/"* ]] && exit                            
        eval "$(udevadm info -q property --export -p $syspath)"        
        [[ -z "$ID_SERIAL" ]] && exit                                  
        echo "/dev/$devname - $ID_SERIAL"                              
    )& # & here is causing all of these queries to run simultaneously  
done                                                                   
# wait then gives a chance for all of the iterations to complete       
wait                                                                   
# output order is random due to multiprocessing so sort results        
) | sort )                                                             

var=$(echo "${devs}" | grep "$IMU_SERIAL" | awk '{print $1}' )    

if [[ -z "$var" ]]; then
    echo "Xsense_MTi not found. Please, check the connections"
    #exit 1
fi  

echo "---XSense MTi found!----"                                                           
echo "Changing the permission for Xsense sensor connected to port ttyUSB0"
sudo chmod 777 /dev/ttyUSB0

echo "Xsense ready to be launched ----"
echo "******************************************************************************"
echo "                          Multi sensor system"
echo "******************************************************************************"
echo ""
echo "This script allows starting the multi sensor devices used to implement"
echo "perception tasks. The information will be saved into ROS Bag file and "
echo "at the same time it can be visualized in RVIZ.."
echo ""
echo "The information published is mentioned as follows:"
echo "1. (Node)Zed cameras -> (Topics) /zed_<pos>/zed_node_0/rgb_raw/image_raw_color"
echo "       Where pos is: front, or left or right"
echo "2. (Node)Ouster  -> (Topic) /ouster/points"
echo "3. (Node)GPS_IMU -> (Topic) /imu/data /navsat/fix"
echo "4. (Node) RVIZ"

read -p "Press ENTER key to start:  "

sleep 2

#Launch the ROS node ---------------------------------
#ros2 launch multi_sensor view_all_sensors_v2.launch.py 
#-----------------------------------------------------     

echo ""
echo "-------------------------------------------------------------------------"
echo "The process has finished."
echo "The data folder is copied to the path: <ROOT>/Documents/data_gps_imu/"
echo "¿Do you want to save the file? "
echo "1: Yes"
echo "2: No"
read -p "Choose the option: " OP

if [[ "$OP" == 1 ]]; then

    if [ ! -d "$PATH_TO_DATA_FOLDER" ]; then
        echo "$PATH_TO_DATA_FOLDER does not exist. The folder will be created"
        mkdir $PATH_TO_DATA_FOLDER
    fi 

    #Check whether the file exits.
    file="${PATH_TO_ROOT}"/ros2_ws/install/gps_imu/share/gps_imu/data/waypoints_xytheta.csv

    if [ ! -f $file ]; then
        echo "The File waypoints_xytheta.csv not exists"
    else    
        mv ~/ros2_ws/install/gps_imu/share/gps_imu/data/waypoints_xytheta.csv ${PATH_TO_DATA_FOLDER}
    fi    
else
    echo "The current file will be erased of the folder"
    rm -r "${PATH_TO_ROOT}"/ros2_ws/install/gps_imu/share/gps_imu/data/waypoints_xytheta.csv
fi  

echo "Done."
 


