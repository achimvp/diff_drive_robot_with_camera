import sys
from glob import glob
from setuptools import find_packages, setup

package_name = 'package_that_uses_the_camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/configs', glob('configs/yolov3.cfg')),
        ('share/' + package_name + '/models', glob('models/yolov3.weights')),
        ('share/' + package_name + '/models', glob('models/yolov8.onnx')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tony',
    maintainer_email='tony@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_streamer = package_that_uses_the_camera.camera_streamer:main',
            'yolo_detector = package_that_uses_the_camera.yolo_detector:main',
        ],
    },
)
