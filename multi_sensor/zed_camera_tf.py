#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
import pyzed.sl as sl
import time
from rclpy.executors import MultiThreadedExecutor


def convert2RGB(img):
    return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)


class ZedImagePublisher(Node):
    def __init__(self, camera_type="center"):
        super().__init__("zed_image_publisher")

        self.cv_bridge = CvBridge()
        self.camera_type = camera_type

        # Configuración
        self.get_logger().info("------------------------------------------------")
        self.get_logger().info("           OPENING ZED CAMERA (Images)          ")
        self.get_logger().info("------------------------------------------------")

        camera_name = None
        serial_number = None

        self.is_publishing_image = False
        self.is_publishing_camera_info = False

        if camera_type == 'center':
            self.declare_parameter('center_camera.camera_name', 'ZED1')
            self.declare_parameter('center_camera.camera_label', "0")
            self.declare_parameter('center_camera.serial_number', 0)
        
            camera_name   = self.get_parameter('center_camera.camera_name').get_parameter_value().string_value
            serial_number = self.get_parameter('center_camera.serial_number').get_parameter_value().integer_value
            camera_label  = self.get_parameter('center_camera.camera_label').get_parameter_value().integer_value

        elif camera_type == 'left':   
            self.declare_parameter('left_camera.camera_name', 'ZED1')
            self.declare_parameter('left_camera.camera_label', "1")
            self.declare_parameter('left_camera.serial_number', 0)
        
            camera_name   = self.get_parameter('left_camera.camera_name').get_parameter_value().string_value
            serial_number = self.get_parameter('left_camera.serial_number').get_parameter_value().integer_value
            camera_label  = self.get_parameter('left_camera.camera_label').get_parameter_value().integer_value

        elif camera_type == 'right':
            self.declare_parameter('right_camera.camera_name', 'ZED1')
            self.declare_parameter('right_camera.camera_label', "2")
            self.declare_parameter('right_camera.serial_number', 0)
    
            camera_name   = self.get_parameter('right_camera.camera_name').get_parameter_value().string_value
            serial_number = self.get_parameter('right_camera.serial_number').get_parameter_value().integer_value
            camera_label  = self.get_parameter('right_camera.camera_label').get_parameter_value().integer_value    

        self.camera_topic = '/' + camera_name + '/zed_node_' + str(camera_label) + '/' + camera_type + '/rgb_raw/image_raw_color'
        self.camera_info_topic = '/' + camera_name + '/zed_node_' + str(camera_label) + '/' + camera_type + '/rgb_raw/camera_info'

        self.get_logger().info('camera_name: {}'.format(camera_name))
        self.get_logger().info('camera_topic: {}'.format(self.camera_topic))
        self.get_logger().info('camera_info_topic: {}'.format(self.camera_info_topic))
        self.get_logger().info('serial_number: {}'.format(serial_number))

        self.image_pub = self.create_publisher(Image, self.camera_topic, 1)
        self.caminfo_pub = self.create_publisher(CameraInfo, self.camera_info_topic, 1)

        # Inicializar ZED
        self.zed = sl.Camera()
        init = sl.InitParameters()
        init.camera_resolution = sl.RESOLUTION.HD720
        init.camera_fps = 30
        init.depth_mode = sl.DEPTH_MODE.ULTRA
        init.coordinate_units = sl.UNIT.METER
        init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
        init.set_from_serial_number(serial_number)

        self.get_logger().info("---Starting ZED TF broadcaster node...---")

        init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
        init.coordinate_units = sl.UNIT.METER

        if self.zed.open(init) != sl.ERROR_CODE.SUCCESS:
            self.get_logger().error("Failed to open ZED camera")
            raise RuntimeError("No se pudo abrir la ZED")

        self.runtime = sl.RuntimeParameters()
        self.image_zed = sl.Mat()

        # Timer para publicar imágenes a 20 Hz
        self.timer = self.create_timer(1.0 / 20.0, self.publish_image)
        self.tf_broadcaster = TransformBroadcaster(self)

    def publish_image(self):
        if self.zed.grab(self.runtime) == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_image(self.image_zed, sl.VIEW.LEFT, sl.MEM.CPU)
            image_ocv = np.array(self.image_zed.get_data())
            zed_img = convert2RGB(image_ocv)

            zed_timestamp = self.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE)
            stamp = rclpy.time.Time(seconds=zed_timestamp.get_microseconds() / 1e6)

            msg = self.cv_bridge.cv2_to_imgmsg(zed_img, "bgr8")
            msg.header.stamp = stamp.to_msg()
            msg.header.frame_id = "zed_camera_frame"
            self.image_pub.publish(msg)

            # Mensaje CameraInfo (simplificado, puedes completarlo con intrínsecos reales)
            cam_info = CameraInfo()
            cam_info.header.stamp = msg.header.stamp
            cam_info.header.frame_id = "zed_camera_frame"
            self.caminfo_pub.publish(cam_info)

            if not self.is_publishing_image:
                self.get_logger().info('Publishing image on topic: {}'.format(self.camera_topic))
                self.is_publishing_image = True

            zed_pose = sl.Pose()
            self.zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)

            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = "velodyne"
            t.child_frame_id = "camera_link"

            # Traslación
            translation = zed_pose.get_translation(sl.Translation())
            t.transform.translation.x = translation.get()[0]
            t.transform.translation.y = translation.get()[1]
            t.transform.translation.z = translation.get()[2]

            # Rotación
            quat = zed_pose.get_orientation(sl.Orientation())
            q = quat.get()
            t.transform.rotation.x = q[0]
            t.transform.rotation.y = q[1]
            t.transform.rotation.z = q[2]
            t.transform.rotation.w = q[3]

            self.tf_broadcaster.sendTransform(t)    

    def destroy_node(self):
        self.zed.close()
        super().destroy_node()


class ZedTFBroadcaster(Node):
    def __init__(self, serial_number=0):
        super().__init__("zed_tf_broadcaster")

        self.get_logger().info("---Starting ZED TF broadcaster node...---")

        # Inicializar ZED
        self.zed = sl.Camera()
        init_params = sl.InitParameters()
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
        init_params.coordinate_units = sl.UNIT.METER
        init_params.set_from_serial_number(serial_number)

        if self.zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            self.get_logger().error("Error abriendo la cámara")
            raise RuntimeError("No se pudo abrir la ZED")

        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer para publicar a 30 Hz
        self.timer = self.create_timer(1.0 / 30.0, self.publish_tf)

    def publish_tf(self):
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed_pose = sl.Pose()
            self.zed.getPosition(zed_pose, sl.REFERENCE_FRAME.WORLD)

            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = "odom"
            t.child_frame_id = "base_link"

            # Traslación
            translation = zed_pose.get_translation(sl.Translation())
            t.transform.translation.x = translation.get()[0]
            t.transform.translation.y = translation.get()[1]
            t.transform.translation.z = translation.get()[2]

            # Rotación
            quat = zed_pose.get_orientation(sl.Orientation())
            q = quat.get()
            t.transform.rotation.x = q[0]
            t.transform.rotation.y = q[1]
            t.transform.rotation.z = q[2]
            t.transform.rotation.w = q[3]

            self.tf_broadcaster.sendTransform(t)

    def destroy_node(self):
        self.zed.close()
        super().destroy_node()


#------------------------------------------------------------------
#               MAIN
#------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)

    executor = MultiThreadedExecutor()

    # Nodo temporal para leer parámetro global
    temp_node = Node("camera_selector")
    temp_node.declare_parameter("camera", "center")
    mode = temp_node.get_parameter("camera").get_parameter_value().string_value

    nodes = []

    if mode == "center":
        nodes.append(ZedImagePublisher(camera_type="center"))

    elif mode == "left":
        nodes.append(ZedImagePublisher(camera_type="left"))

    elif mode == "right":
        nodes.append(ZedImagePublisher(camera_type="right"))

    elif mode == "dual":
        nodes.append(ZedImagePublisher(camera_type="left"))
        nodes.append(ZedImagePublisher(camera_type="right"))

    elif mode == "all":
        nodes.append(ZedImagePublisher(camera_type="center"))
        nodes.append(ZedImagePublisher(camera_type="left"))
        nodes.append(ZedImagePublisher(camera_type="right"))

    else:
        raise ValueError(f"Modo de cámara no válido: {mode}")

    for node in nodes:
        executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()