import sys


from PySide2 import QtCore, QtWidgets, QtGui
import qimage2ndarray  # This import should always follow Pyside2 imports
import cv2


class MainApp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.video_size = QtCore.QSize(640, 480)
        self.setup_ui()
        self.setup_camera()

    def setup_ui(self):
        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(self.video_size)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.quit_button)

        self.setLayout(self.main_layout)

    def setup_camera(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size.width())
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size.height())

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(30)

    def display_video_stream(self):
        ret, frame = self.capture.read()

        # Wait till capture initializes
        if not ret:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        image = qimage2ndarray.array2qimage(frame)  # SOLUTION FOR MEMORY LEAK
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))


def run():
    app = QtWidgets.QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
