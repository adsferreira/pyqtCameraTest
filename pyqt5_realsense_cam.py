import numpy as np
import pyrealsense2 as rs
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QWidget, QVBoxLayout


def np_color_img_to_q_image(color_image):
    h, w, channel = color_image.shape
    q_image = QImage(color_image.data, w, h, channel * w, QImage.Format_RGB888)

    return q_image


def np_depth_img_to_q_img(depth_image):
    h, w, channel = depth_image.shape
    q_image = QImage(depth_image.data, w, h, channel * w, QImage.Format_RGB888)

    return q_image


class QRealSenseCam(QThread):
    frames_ready = pyqtSignal(QImage, QImage)

    def __init__(self, resolution, frame_rate):
        super().__init__()
        # configure depth and color streams
        self.__config = rs.config()
        self.__pipeline = rs.pipeline()
        self.__resolution = resolution
        self.__frame_rate = frame_rate
        self.__is_cam_running = True
        self.__align = rs.align(rs.stream.color)
        self.__config_rs()
        self.__start_rs()

    def __config_rs(self):
        self.__config.enable_stream(
            rs.stream.depth, self.__resolution[0], self.__resolution[1], rs.format.z16, self.__frame_rate)
        self.__config.enable_stream(
            rs.stream.color, self.__resolution[0], self.__resolution[1], rs.format.rgb8, self.__frame_rate)

    def __start_rs(self):
        self.__pipeline.start(self.__config)

    def run(self):
        # decimate.set_option(rs.option.filter_magnitude, 2 ** self._state.decimate)
        colorizer = rs.colorizer()

        try:
            while self.__is_cam_running:
                # wait for a coherent color frame
                frames = self.__pipeline.wait_for_frames()
                # align the depth frame to color frame
                aligned_frames = self.__align.process(frames)

                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                # apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())
                color_image = np.asanyarray(color_frame.get_data())

                depth_image = np_depth_img_to_q_img(depth_colormap)
                color_image = np_color_img_to_q_image(color_image)

                self.frames_ready.emit(depth_image, color_image)
        finally:
            self.stop()

    def stop(self):
        self.__pipeline.stop()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.__widget = QWidget()
        self.__depth_label = QLabel()
        self.__rgb_label = QLabel()
        self.__qv_box_layout = QVBoxLayout()
        self.__qv_box_layout.addWidget(self.__depth_label)
        self.__qv_box_layout.addWidget(self.__rgb_label)
        self.__widget.setLayout(self.__qv_box_layout)
        self.setCentralWidget(self.__widget)
        self.show()

    @QtCore.pyqtSlot(QImage, QImage)
    def receive_frame(self, depth, rgb):
        self.__depth_label.setPixmap(QPixmap.fromImage(depth))
        self.__rgb_label.setPixmap(QPixmap.fromImage(rgb))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    cam = QRealSenseCam((640, 480), 30)
    cam.frames_ready.connect(main_win.receive_frame)
    cam.start()
    sys.exit(app.exec_())
