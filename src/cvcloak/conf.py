import os


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')


class STYLESHEET:
    def _get_stylesheet(stylesheet_name):
        stylesheet = None
        stylesheet_file_path = os.path.join(
            f'{RESOURCE_DIR}/css',
            f'{stylesheet_name}.css',
        )
        with open(stylesheet_file_path, 'r') as f:
            stylesheet = f.read()

        return stylesheet

    dark_01 = _get_stylesheet('dark_01')


class APP:
    NAME = "CVCLOAK"
    STYLESHEET = STYLESHEET.dark_01
    IMAGE_WIDTH = 640
    IMAGE_HEIGHT = 480
    CAMERA_DEVICE_INT = 0  # `0` is for default camera
    BUTTON_HEIGHT = 60
    SLIDER_HEIGHT = 10
    SLIDER_WIDTH = 200

    DEFAULT_BAND_1_LOW_COLOR = (0, 120, 70)
    DEFAULT_BAND_1_HIGH_COLOR = (20, 255, 255)
    DEFAULT_BAND_2_LOW_COLOR = (340, 120, 70)
    DEFAULT_BAND_2_HIGH_COLOR = (359, 255, 255)

    FONT_FAMILY = 'Andale Mono'
    FONT_FILE_PATH = os.path.join(RESOURCE_DIR, f'font/{FONT_FAMILY}.ttf')

    SPLASH_SCREEN_PATH = os.path.join(RESOURCE_DIR, 'image/splash.png')
