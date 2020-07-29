# -*- coding: utf-8 -*-
from distutils.core import setup
from glob import glob

PACKAGE_NAME = 'cvcloak'
PACKAGE_VERSION = '0.1'

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='The magic inivisibility cloak implemented in opencv',
    author='Alok Gandhi',
    author_email='alok.gandhi2002@gmail.com',
    url='https://github.com/alok1974/cloak',
    packages=[
        'cvcloak',
        'cvcloak.resources',
    ],
    package_data={
        'cvcloak': ['*.py'],
        'cvcloak.resources': ['*.png', '*.css', '*.ttf'],
    },
    package_dir={
        'cvcloak': 'src/cvcloak'
    },
    scripts=glob('src/scripts/*'),
    install_requires=[
        'numpy >=1.19.1',
        'opencv-contrib-python-headless>=4.3.0.36',
        'PySide2>=5.15.0',
        'qimage2ndarray>=1.8.3',
        'shiboken2>=5.15.0',
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment :: Board Games',
        'License :: OSI Approved :: MIT License',
    ],
)
