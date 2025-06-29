import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as ROSImage
from interfaces.msg import Float32MultiArray2D
from std_msgs.msg import String, UInt8

import message_filters
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import cv2
import cv_bridge
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QImage

class ROSConnector(QObject):
    camera_image_ready = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bridge = cv_bridge.CvBridge()
        self.view_mode = "Tracking"

        rclpy.init()
        self.node = rclpy.create_node('ui_connector')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=20
        )

        self.mode_pub = self.node.create_publisher(String, '/system/mode', 10)
        self.command_pub = self.node.create_publisher(String, '/system/commands', 10)

        self.image_sub = message_filters.Subscriber(
            self.node, ROSImage, '/camera/image_raw', qos_profile=qos_profile
        )
        self.detections_sub = message_filters.Subscriber(
            self.node, Float32MultiArray2D, '/imageproc/results', qos_profile=qos_profile
        )

        self.ts = message_filters.ApproximateTimeSynchronizer(
            [self.image_sub, self.detections_sub],
            queue_size=30,
            slop=0.1,
            allow_headerless=False
        )
        self.ts.registerCallback(self._callback)

        self.ros_timer = QTimer()
        self.ros_timer.timeout.connect(self._spin_once)
        self.ros_timer.start(5)

    def set_view_mode(self, mode: str):
        self.view_mode = mode
        print(f"[ROSConnector] View mode changed to: {mode}")

    def publish_mode_change(self, mode_name: str):
        msg = String()
        msg.data = mode_name
        self.mode_pub.publish(msg)
        print(f"[ROSConnector] Published mode: {mode_name}")

    def publish_system_command(self, command: str):
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)
        print(f"[ROSConnector] Published system command: {command}")

    def publish_laser_power(self, power: int):
        msg = String()
        msg.data = f"laser_power: {power}"
        self.command_pub.publish(msg)
        print(f"[ROSConnector] Published laser power: {msg.data}")

    def publish_movement_command(self, direction: str):
        msg = String()
        msg.data = f"move:{direction}"
        self.command_pub.publish(msg)
        print(f"[ROSConnector] Sent movement command: {msg.data}")

    def publish_shoot_command(self):
        msg = String()
        msg.data = "shoot"
        self.command_pub.publish(msg)
        print(f"[ROSConnector] Sent shoot command!")

    def _callback(self, image_msg: ROSImage, detections_msg: Float32MultiArray2D):
        try:
            frame = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')

            if self.view_mode == "Tracking":
                detections = np.array(
                    detections_msg.data, dtype=np.float32
                ).reshape(detections_msg.rows, detections_msg.cols)

                for det in detections:
                    x1, y1, x2, y2, obj_id, conf, _ = det
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    obj_id = int(obj_id)
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    label = f"ID: {obj_id}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_image_ready.emit(qimage.copy())

        except Exception as e:
            print(f"[ROSConnector] Callback Error: {e}")

    def _spin_once(self):
        rclpy.spin_once(self.node, timeout_sec=0.001)

    def shutdown(self):
        self.ros_timer.stop()
        self.node.destroy_node()
        rclpy.shutdown()
