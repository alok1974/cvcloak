from PySide2 import QtWidgets, QtGui


class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        lay = QtWidgets.QVBoxLayout(self)
        button = QtWidgets.QPushButton("Select color")
        button.clicked.connect(self.on_clicked)
        self.label = QtWidgets.QLabel()
        self.label.setAutoFillBackground(True)
        self.label.setFixedSize(100, 100)

        lay.addWidget(button)
        lay.addWidget(self.label)

    def on_clicked(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            palette = self.label.palette()
            palette.setColor(QtGui.QPalette.Background, color)
            self.label.setPalette(palette)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
