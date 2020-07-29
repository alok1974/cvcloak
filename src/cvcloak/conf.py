import os


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')


class STYLESHEET:
    def _get_stylesheet(stylesheet_name):
        stylesheet = None
        stylesheet_file_path = os.path.join(
            RESOURCE_DIR,
            f'{stylesheet_name}.css',
        )
        with open(stylesheet_file_path, 'r') as f:
            stylesheet = f.read()

        return stylesheet

    dark_01 = _get_stylesheet('dark_01')
    dark_02 = _get_stylesheet('dark_02')
    dark_03 = _get_stylesheet('dark_03')
    dark_04 = _get_stylesheet('dark_04')
    dark_05 = _get_stylesheet('dark_05')
