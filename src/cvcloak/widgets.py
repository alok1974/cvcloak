import enum
from functools import partial
import contextlib


from PySide2 import QtWidgets, QtCore, QtGui


from .conf import APP


@contextlib.contextmanager
def block_widget_signals(widget):
    widget.blockSignals(True)
    yield
    widget.blockSignals(False)


@enum.unique
class SLIDER_TYPE(enum.Enum):
    h = 0
    s = 1
    v = 2


class HSBWidget(QtWidgets.QWidget):
    SLIDER_MIN_MAX_VAL_MAP = {
        SLIDER_TYPE.h: (0, 359),
        SLIDER_TYPE.s: (0, 255),
        SLIDER_TYPE.v: (0, 255),

    }

    COLOR_CHANGED_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self._name = name

        self._h = 0
        self._s = 0
        self._v = 0

        self._setup_ui()
        self._connect_signals()

    @property
    def color(self):
        return (self._h, self._s, self._v)

    @color.setter
    def color(self, color):
        self._h, self._s, self._v = color
        self._update_color_info()
        for slider, val in zip(
                [self._h_slider, self._s_slider, self._v_slider],
                list(color),
        ):
            with block_widget_signals(slider):
                slider.setValue(val)

    def _setup_ui(self):
        self.setStyleSheet('QWidget { border: none }')

        self._main_layout = QtWidgets.QVBoxLayout(self)

        self._name_layout = self._create_name_layout()
        self._main_layout.addLayout(self._name_layout)

        self._color_layout = self._create_color_layout()
        self._main_layout.addLayout(self._color_layout)

        self._update_color_info()

    def _create_name_layout(self):
        self._name_layout = QtWidgets.QHBoxLayout()

        self._name_label = QtWidgets.QLabel(self._name)
        self._name_layout.addWidget(self._name_label)

        self._name_layout.addStretch(1)

        self._color_text_label = self._create_color_text_label()
        self._name_layout.addWidget(self._color_text_label)

        return self._name_layout

    def _create_color_text_label(self):
        self._color_text_label = QtWidgets.QLabel()
        self._color_text_label.setFixedHeight(14)
        self._color_text_label.setAlignment(QtCore.Qt.AlignLeft)
        font_id = QtGui.QFontDatabase().addApplicationFont(APP.FONT_FILE_PATH)
        if font_id == -1:
            error_msg = f'Could not load font from {APP.FONT_FILE_PATH}'
            raise RuntimeError(error_msg)
        font = QtGui.QFont(APP.FONT_FAMILY)
        font.setPointSize(12)
        self._color_text_label.setFont(font)

        return self._color_text_label

    def _create_color_layout(self):
        self._color_layout = QtWidgets.QHBoxLayout()

        self._color_label = QtWidgets.QLabel()
        self._color_label.setMinimumWidth(30)
        self._color_layout.addWidget(self._color_label)

        self._slider_group_layout = self._create_slider_group_layout()
        self._color_layout.addLayout(self._slider_group_layout)

        return self._color_layout

    def _create_slider_group_layout(self):
        self._slider_group_layout = QtWidgets.QVBoxLayout()
        widgets = self._create_slider_layout(slider_type=SLIDER_TYPE.h)
        self._h_layout, self._h_label, self._h_slider = widgets
        widgets = self._create_slider_layout(slider_type=SLIDER_TYPE.s)
        self._s_layout, self._s_label, self._s_slider = widgets
        widgets = self._create_slider_layout(slider_type=SLIDER_TYPE.v)
        self._v_layout, self._v_label, self._v_slider = widgets
        for t in [self._h_layout, self._s_layout, self._v_layout]:
            self._slider_group_layout.addLayout(t)

        return self._slider_group_layout

    def _connect_signals(self):
        self._h_slider.valueChanged.connect(
            partial(
                self._value_changed,
                slider_type=SLIDER_TYPE.h
            )
        )

        self._s_slider.valueChanged.connect(
            partial(
                self._value_changed,
                slider_type=SLIDER_TYPE.s
            )
        )

        self._v_slider.valueChanged.connect(
            partial(
                self._value_changed,
                slider_type=SLIDER_TYPE.v
            )
        )

    def _value_changed(self, val, slider_type):
        if slider_type == SLIDER_TYPE.h:
            self._h = val
        elif slider_type == SLIDER_TYPE.s:
            self._s = val
        elif slider_type == SLIDER_TYPE.v:
            self._v = val
        else:
            error_msg = f'SLIDER TYPE {slider_type} is not defined!!'
            raise ValueError(error_msg)

        self._update_color_info()

        self.COLOR_CHANGED_SIGNAL.emit((self._h, self._s, self._v))

    def _get_color_style_string(self):
        return(
            'QWidget { background-color: '
            f'hsv({self._h}, {self._s}, {self._v})}}'
        )

    def _get_color_text_string(self):
        return(
            f'[{str(self._h).zfill(3)}, '
            f'{str(self._s).zfill(3)}, '
            f'{str(self._v).zfill(3)}]'
        )

    def _update_color_info(self):
        color_style = self._get_color_style_string()
        self._color_label.setStyleSheet(color_style)
        color_text = self._get_color_text_string()
        self._color_text_label.setText(color_text)

    def _create_slider(self, slider_type=SLIDER_TYPE.h):
        min_val, max_val = self.SLIDER_MIN_MAX_VAL_MAP.get(slider_type)
        default_val = int((max_val - min_val) / 2)
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimumWidth(APP.SLIDER_WIDTH)
        slider.setMaximumHeight(APP.SLIDER_HEIGHT)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setSingleStep(1)

        with block_widget_signals(slider):
            slider.setValue(default_val)
            if slider_type == SLIDER_TYPE.h:
                self._h = default_val
            elif slider_type == SLIDER_TYPE.s:
                self._s = default_val
            elif slider_type == SLIDER_TYPE.v:
                self._v = default_val
            else:
                error_msg = f'SLIDER TYPE {slider_type} is not defined!!'
                raise ValueError(error_msg)

        return slider

    def _create_slider_layout(self, slider_type=SLIDER_TYPE.h):
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(str(slider_type.name).upper())
        label.setFixedHeight(12)
        slider = self._create_slider(slider_type=slider_type)
        layout.addWidget(label)
        layout.addWidget(slider)
        return layout, label, slider


class ColorBandWidget(QtWidgets.QFrame):
    LOW_COLOR_CHANGED_SIGNAL = QtCore.Signal(tuple)
    HIGH_COLOR_CHANGED_SIGNAL = QtCore.Signal(tuple)

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self._name = name

        self._low_color = None
        self._high_color = None

        self._setup_ui()
        self._connect_signals()

    @property
    def low_color(self):
        return self._low_widget.color

    @low_color.setter
    def low_color(self, color):
        self._low_widget.color = color

    @property
    def high_color(self):
        return self._high_widget.color

    @high_color.setter
    def high_color(self, color):
        self._high_widget.color = color

    def _setup_ui(self):
        self.setStyleSheet('QWidget { border: 1px solid #5A5A5A }')
        self._label = QtWidgets.QLabel(self._name)
        self._label.setStyleSheet('QWidget { border: none }')

        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._low_widget = HSBWidget(name='LOW', parent=self)
        self._high_widget = HSBWidget(name='HIGH', parent=self)

        self._main_layout.addWidget(self._label)
        self._main_layout.addWidget(self._low_widget)
        self._main_layout.addWidget(self._high_widget)

    def _connect_signals(self):
        self._low_widget.COLOR_CHANGED_SIGNAL.connect(self._low_color_changed)
        self._high_widget.COLOR_CHANGED_SIGNAL.connect(
            self._high_color_changed
        )

    def _low_color_changed(self, color):
        self.LOW_COLOR_CHANGED_SIGNAL.emit(color)

    def _high_color_changed(self, color):
        self.HIGH_COLOR_CHANGED_SIGNAL.emit(color)
