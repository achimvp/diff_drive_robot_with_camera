from setuptools import find_packages, setup

package_name = 'simple_control_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tony',
    maintainer_email='prittwitza@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'move_straight_publisher_node = simple_control_package.move_straight_publisher_node:main',
            'move_circle_publisher_node = simple_control_package.move_circle_publisher_node:main',
            'look_around_node = simple_control_package.look_around_node:main',
            'look_around_joint_publisher_node = simple_control_package.look_around_joint_publisher_node:main',
            # 'observation_aggregation_node = simple_control_package.observation_aggregation_node:main',
            'observation_collection_node = simple_control_package.observation_collection_node:main',
        ],
    },
)
