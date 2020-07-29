import sys
import enum
from functools import partial


from PySide2 import QtCore, QtWidgets, QtGui
import qimage2ndarray  # This import should always follow Pyside2 imports
import cv2
import numpy as np


from .conf import APP
from .widgets import ColorBandWidget, block_widget_signals


@enum.unique
class BAND_TYPE(enum.Enum):
    FIRST = 0
    SECOND = 1


@enum.unique
class RANGE_TYPE(enum.Enum):
    LOW = 0
    HIGH = 1


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._capture = None
        self._background = None
        self._frame = None
        self._image = None
        self._show_calib = False

        self._band_1_low_color = None
        self._band_1_high_color = None
        self._band_2_low_color = None
        self._band_2_high_color = None

        self._setup_ui()
        self._setup_camera()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(APP.NAME)
        self.setStyleSheet(APP.STYLESHEET)

        self._main_layout = QtWidgets.QHBoxLayout(self)

        self._calib_widget = self._create_calib_widget()
        self._calib_widget.setVisible(False)
        self._main_layout.addWidget(self._calib_widget)

        self._viewer_widget = self._create_viewer_widget()
        self._main_layout.addWidget(self._viewer_widget)

        self._main_layout.setAlignment(QtCore.Qt.AlignHCenter)
        self._main_layout.setContentsMargins(1, 1, 1, 1)
        self.setFixedSize(self._main_layout.sizeHint())

        self.move(300, 80)

    def _create_viewer_widget(self):
        self._viewer_widget = QtWidgets.QWidget()
        self._viewer_widget.setStyleSheet('QWidget { border: none }')

        self._viewer_layout = QtWidgets.QVBoxLayout(self._viewer_widget)

        self._image_layout = self._create_image_layout()
        self._viewer_layout.addLayout(self._image_layout)

        self._bottom_layout = self._create_bottom_layout()
        self._viewer_layout.addLayout(self._bottom_layout)

        return self._viewer_widget

    def _create_image_layout(self):
        self._image_layout = QtWidgets.QVBoxLayout()
        self._image_label = QtWidgets.QLabel()
        self._image_label.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A; }'
        )
        self._image_label.setMinimumSize(APP.IMAGE_WIDTH, APP.IMAGE_HEIGHT)
        self._image_layout.addWidget(self._image_label)

        return self._image_layout

    def _create_bottom_layout(self):
        self._bottom_layout = QtWidgets.QHBoxLayout()
        self._calib_btn = QtWidgets.QPushButton("Open Calibration")
        self._calib_btn.setMinimumHeight(APP.BUTTON_HEIGHT)
        self._calib_btn.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A; }'
        )

        self._close_btn = QtWidgets.QPushButton("Close")
        self._close_btn.setMinimumHeight(APP.BUTTON_HEIGHT)
        self._close_btn.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A; }'
        )
        self._bottom_layout.addWidget(self._calib_btn)
        self._bottom_layout.addWidget(self._close_btn)

        return self._bottom_layout

    def _create_calib_widget(self):
        self._calib_widget = QtWidgets.QWidget()
        self._calib_widget.setStyleSheet(
            'QWidget { border: none }'
        )

        self._calib_layout = QtWidgets.QVBoxLayout(self._calib_widget)

        self._band_1_widget = self._create_band_widget(
            band_type=BAND_TYPE.FIRST
        )
        self._band_2_widget = self._create_band_widget(
            band_type=BAND_TYPE.SECOND
        )

        self._hue_label = QtWidgets.QLabel('MASTER HUE')
        self._hue_gradient_label = QtWidgets.QLabel()
        self._hue_gradient_label.setStyleSheet(
            '* {'
            'background: qlineargradient( '
            'x1:0 y1:0, x2:1 y2:0, '
            'stop:0 hsv(0, 255, 255), '
            'stop:0.17 hsv(60, 255, 255), '
            'stop:0.33 hsv(120, 255, 255), '
            'stop:0.50 hsv(180, 255, 255), '
            'stop:0.67 hsv(240, 255, 255), '
            'stop:0.83 hsv(300, 255, 255), '
            'stop:1 hsv(0, 255, 255)'
            ');}'
        )
        self._hue_gradient_label.setMaximumHeight(APP.SLIDER_HEIGHT)
        self._hue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._hue_slider.setTracking(True)
        self._hue_slider.setMinimumWidth(APP.SLIDER_WIDTH)
        self._hue_slider.setMaximumHeight(APP.SLIDER_HEIGHT)
        self._hue_slider.setMinimum(0)
        self._hue_slider.setMaximum(359)
        self._hue_slider.setValue(359)
        self._hue_slider.setSingleStep(1)

        self._reset_calib_btn = QtWidgets.QPushButton("Default")
        self._reset_calib_btn.setMinimumHeight(APP.BUTTON_HEIGHT)
        self._reset_calib_btn.setStyleSheet(
            'QWidget { border: 1px solid #5A5A5A; }'
        )

        self._calib_layout.addWidget(self._band_1_widget)
        self._calib_layout.addWidget(self._band_2_widget)
        self._calib_layout.addWidget(self._hue_label)
        self._calib_layout.addWidget(self._hue_gradient_label)
        self._calib_layout.addWidget(self._hue_slider)
        self._calib_layout.addWidget(self._reset_calib_btn)

        return self._calib_widget

    def _create_band_widget(self, band_type=BAND_TYPE.FIRST):
        name = None
        low_color = None
        high_color = None

        if band_type == BAND_TYPE.FIRST:
            name = 'COLOR BAND 1'
            low_color = APP.DEFAULT_BAND_1_LOW_COLOR
            self._band_1_low_color = self._rescale_color_for_cv(low_color)

            high_color = APP.DEFAULT_BAND_1_HIGH_COLOR
            self._band_1_high_color = self._rescale_color_for_cv(high_color)

        elif band_type == BAND_TYPE.SECOND:
            name = 'COLOR BAND 2'
            low_color = APP.DEFAULT_BAND_2_LOW_COLOR
            self._band_2_low_color = self._rescale_color_for_cv(low_color)

            high_color = APP.DEFAULT_BAND_2_HIGH_COLOR
            self._band_2_high_color = self._rescale_color_for_cv(high_color)

        widget = ColorBandWidget(
            name=name,
            parent=self,
        )
        widget.low_color = low_color
        widget.high_color = high_color

        return widget

    def _reset_calib(self):
        low_color_1 = APP.DEFAULT_BAND_1_LOW_COLOR
        self._band_1_widget.low_color = low_color_1
        self._band_1_low_color = self._rescale_color_for_cv(low_color_1)

        high_color_1 = APP.DEFAULT_BAND_1_HIGH_COLOR
        self._band_1_widget.high_color = high_color_1
        self._band_1_high_color = self._rescale_color_for_cv(high_color_1)

        low_color_2 = APP.DEFAULT_BAND_2_LOW_COLOR
        self._band_2_widget.low_color = low_color_2
        self._band_2_low_color = self._rescale_color_for_cv(low_color_2)

        high_color_2 = APP.DEFAULT_BAND_2_HIGH_COLOR
        self._band_2_widget.high_color = high_color_2
        self._band_2_high_color = self._rescale_color_for_cv(high_color_2)

        with block_widget_signals(self._hue_slider):
            self._hue_slider.setValue(359)

    def _setup_camera(self):
        self._initialize_capture()
        self._background = self._get_background()
        self._timer = QtCore.QTimer()
        self._timer.start(30)

    def _connect_signals(self):
        self._timer.timeout.connect(self._display_video_stream)
        self._close_btn.clicked.connect(self._close)
        self._calib_btn.clicked.connect(self._toggle_calib)
        self._reset_calib_btn.clicked.connect(self._reset_calib)
        self._hue_slider.valueChanged.connect(self._hue_changed)

        self._band_1_widget.LOW_COLOR_CHANGED_SIGNAL.connect(
            partial(
                self._color_changed,
                band_type=BAND_TYPE.FIRST,
                range_type=RANGE_TYPE.LOW,
            )
        )

        self._band_1_widget.HIGH_COLOR_CHANGED_SIGNAL.connect(
            partial(
                self._color_changed,
                band_type=BAND_TYPE.FIRST,
                range_type=RANGE_TYPE.HIGH,
            )
        )

        self._band_2_widget.LOW_COLOR_CHANGED_SIGNAL.connect(
            partial(
                self._color_changed,
                band_type=BAND_TYPE.SECOND,
                range_type=RANGE_TYPE.LOW,
            )
        )

        self._band_2_widget.HIGH_COLOR_CHANGED_SIGNAL.connect(
            partial(
                self._color_changed,
                band_type=BAND_TYPE.SECOND,
                range_type=RANGE_TYPE.HIGH,
            )
        )

    def _initialize_capture(self):
        self._capture = cv2.VideoCapture(APP.CAMERA_DEVICE_INT)
        while True:
            if self._capture.isOpened():
                break
            self._capture.open()

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, APP.IMAGE_WIDTH)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, APP.IMAGE_HEIGHT)

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
        # Define 1st color band
        lower_band_1 = np.array(list(self._band_1_low_color))
        upper_band_1 = np.array(list(self._band_1_high_color))
        color_band_1 = cv2.inRange(frame, lower_band_1, upper_band_1)

        # Define second color band
        lower_band_2 = np.array(list(self._band_2_low_color))
        upper_band_2 = np.array(list(self._band_2_high_color))
        color_band_2 = cv2.inRange(frame, lower_band_2, upper_band_2)

        # Combine color bands into single mask
        color_mask = color_band_1 + color_band_2

        # Apply noise filter to color mask
        color_mask = cv2.morphologyEx(
            color_mask,
            cv2.MORPH_OPEN,
            np.ones((3, 3), np.uint8),
            iterations=8,
        )

        # Apply smooth filter to color mask
        color_mask = cv2.morphologyEx(
            color_mask,
            cv2.MORPH_DILATE,
            np.ones((3, 3), np.uint8),
            iterations=1,
        )

        # Replace the mask color with color from
        # captured one frame background
        masked_bg = cv2.bitwise_and(
            self._background,
            self._background,
            mask=color_mask,
        )

        # Get the inverse of the color mask
        inverse_color_mask = cv2.bitwise_not(color_mask)

        # Get the color of the current frame sans the color mask
        masked_frame = cv2.bitwise_and(frame, frame, mask=inverse_color_mask)

        # Composite the background and current frame colors
        composite = cv2.addWeighted(masked_bg, 1, masked_frame, 1, 0)

        # Convert HSV to RGB for display
        final_composite = cv2.cvtColor(composite, cv2.COLOR_HSV2RGB)

        return final_composite

    def _toggle_calib(self):
        self._show_calib = not(self._show_calib)
        self._calib_widget.setVisible(self._show_calib)
        if self._show_calib:
            self._calib_btn.setText('Close Calibration')
            self.setFixedSize(self._main_layout.sizeHint())
        else:
            self._close_btn.setFixedHeight(APP.BUTTON_HEIGHT)
            self._calib_btn.setFixedHeight(APP.BUTTON_HEIGHT)
            self._calib_btn.setText("Open Calibration")
            self.setFixedSize(self._main_layout.sizeHint())

    def _close(self):
        self._capture.release()
        cv2.destroyAllWindows()
        self.close()

    def _pick_color(self):
        color = QtWidgets.QColorDialog.getColor()
        self._color_label.setStyleSheet(
            "QWidget { background-color: %s}" % color.name())

    def _color_changed(
            self, color,
            band_type=BAND_TYPE.FIRST, range_type=RANGE_TYPE.LOW
    ):
        color = self._rescale_color_for_cv(color)

        if band_type == BAND_TYPE.FIRST:
            if range_type == RANGE_TYPE.LOW:
                self._band_1_low_color = color
            elif range_type == RANGE_TYPE.HIGH:
                self._band_1_high_color = color
            else:
                error_msg = 'Invalid range type!!'
                raise ValueError(error_msg)
        elif band_type == BAND_TYPE.SECOND:
            if range_type == RANGE_TYPE.LOW:
                self._band_2_low_color = color
            elif range_type == RANGE_TYPE.HIGH:
                self._band_2_high_color = color
            else:
                error_msg = 'Invalid range_type!!'
                raise ValueError(error_msg)
        else:
            error_msg = 'Invalid band_type'
            raise ValueError(error_msg)

    def _rescale_color_for_cv(self, color):
        h, s, v = color
        return int(h / 2), s, v

    def _hue_changed(self, val):
        h2, l2, h1, l1 = None, None, None, None

        if val == 359 or val == 0:
            h2 = 359
            l2 = 339
            h1 = 20
            l1 = 0
        elif val <= 20:
            h2 = val
            l2 = 339 + val
            h1 = val + 20
            l1 = val
        elif val >= 339:
            h2 = val
            l2 = val - 20
            h1 = val - 339
            l1 = val
        else:
            h2 = val
            l2 = val - 20
            h1 = val + 20
            l1 = val

        _, s, v = self._band_2_high_color
        color = h2, s, v
        self._band_2_widget.high_color = color
        self._band_2_high_color = self._rescale_color_for_cv(color)

        _, s, v = self._band_2_low_color
        color = l2, s, v
        self._band_2_widget.low_color = color
        self._band_2_low_color = self._rescale_color_for_cv(color)

        _, s, v = self._band_1_high_color
        color = h1, s, v
        self._band_1_widget.high_color = color
        self._band_1_high_color = self._rescale_color_for_cv(color)

        _, s, v = self._band_1_low_color
        color = l1, s, v
        self._band_1_widget.low_color = color
        self._band_1_low_color = self._rescale_color_for_cv(color)


def run():
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
