import sys


from PySide2 import QtCore, QtWidgets, QtGui
import qimage2ndarray  # This import should always follow Pyside2 imports
import cv2
import numpy as np


from . import conf


class MainApp(QtWidgets.QWidget):
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480
    CAMERA_DEVICE_INT = 0  # `0` is for default camera
    STYLESHEET = conf.STYLESHEET.dark_01
    TITLE = "CVCLOAK"
    MARGIN = 40
    BOTTOM_LAYOUT_HEIGHT = 60

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._capture = None
        self._background = None
        self._frame = None
        self._image = None

        self._setup_ui()
        self._setup_camera()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(self.TITLE)
        self.setFixedSize(
            self.IMAGE_WIDTH + self.MARGIN,
            self.IMAGE_HEIGHT + (2 * self.MARGIN) + self.BOTTOM_LAYOUT_HEIGHT,
        )
        self.setStyleSheet(self.STYLESHEET)

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._image_layout = self._create_image_layout()
        self._main_layout.addLayout(self._image_layout)

        self._bottom_layout = self._create_bottom_layout()
        self._main_layout.addLayout(self._bottom_layout)

    def _create_image_layout(self):
        self._image_layout = QtWidgets.QVBoxLayout()

        self._image_label = QtWidgets.QLabel()
        self._image_label.setFixedSize(self.IMAGE_WIDTH, self.IMAGE_HEIGHT)

        self._image_layout.addWidget(self._image_label)

        return self._image_layout

    def _create_bottom_layout(self):
        self._bottom_layout = QtWidgets.QHBoxLayout()

        self._close_btn = QtWidgets.QPushButton("Close")
        self._close_btn.setFixedHeight(self.BOTTOM_LAYOUT_HEIGHT)

        self._bottom_layout.addWidget(self._close_btn)

        return self._bottom_layout

    def _setup_camera(self):
        self._initialize_capture()
        self._background = self._get_background()
        self._timer = QtCore.QTimer()
        self._timer.start(30)

    def _connect_signals(self):
        self._timer.timeout.connect(self._display_video_stream)
        self._close_btn.clicked.connect(self._close)

    def _initialize_capture(self):
        self._capture = cv2.VideoCapture(self.CAMERA_DEVICE_INT)
        while True:
            if self._capture.isOpened():
                break
            self._capture.open()

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.IMAGE_WIDTH)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.IMAGE_HEIGHT)

    def _get_background(self):
        ret = False
        frame = None
        while True:
            for _ in range(30):
                ret, frame = self._capture.read()
                frame = cv2.flip(frame, 1)
            if ret:
                break

        if frame is None:
            self._capture.release()
            error_msg = (
                "Unable to initialize the background!"
            )
            raise RuntimeError(error_msg)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    def _display_video_stream(self):
        ret, frame = self._capture.read()

        # Wait till capture initializes
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame = cv2.flip(frame, 1)
        self._frame = self._process_capture(frame)

        # Using `qimage2ndarray` to fix memory leak
        self._image = qimage2ndarray.array2qimage(self._frame)

        self._image_label.setPixmap(QtGui.QPixmap.fromImage(self._image))

    def _process_capture(self, frame):
        lower_red = np.array([0, 120, 70])  # #452424
        upper_red = np.array([10, 255, 255])  # #ff5500
        red_low = cv2.inRange(frame, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])  # #45242a
        upper_red = np.array([180, 255, 255])  # ##ff0000
        red_high = cv2.inRange(frame, lower_red, upper_red)

        mask1 = red_low + red_high
        mask1 = cv2.morphologyEx(
            mask1,
            cv2.MORPH_OPEN,
            np.ones((3, 3), np.uint8),
            iterations=8,
        )
        mask1 = cv2.morphologyEx(
            mask1,
            cv2.MORPH_DILATE,
            np.ones((3, 3), np.uint8),
            iterations=1,
        )

        mask2 = cv2.bitwise_not(mask1)

        res1 = cv2.bitwise_and(self._background, self._background, mask=mask1)
        res2 = cv2.bitwise_and(frame, frame, mask=mask2)
        composite = cv2.addWeighted(res1, 1, res2, 1, 0)

        return cv2.cvtColor(composite, cv2.COLOR_HSV2RGB)

    def _close(self):
        self._capture.release()
        cv2.destroyAllWindows()
        self.close()


def run():
    app = QtWidgets.QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
