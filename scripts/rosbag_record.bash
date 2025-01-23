#!/bin/bash

source ~/ros2_ws/install/setup.bash
source /opt/ros/humble/setup.bash

cd ~/
PATH_TO_ROOT=$(pwd)
PATH_TO_BAGFILE="${PATH_TO_ROOT}/data/bagfiles/"

if [ $# -eq 0 ]; then
  exit 1
fi

if [ "$1" = "--bagfile-name" ]; then

    echo "Bagfile record has started."
    ros2 bag record -o "${PATH_TO_BAGFILE}""$2"  /zed_front/zed_node_0/right/image_rect_color \
                                                 /zed_front/zed_node_0/left/image_rect_color  \
                                                 /zed_left/zed_node_1/right/image_rect_color  \
                                                 /zed_right/zed_node_2/left/image_rect_color  \
                                                 /ouster/points                               \
                                                 /imu/data                                    \
                                                 /navsat/fix				                          \
                                                 /tf                                          \
                                                 /tf_static

fi                                                                
