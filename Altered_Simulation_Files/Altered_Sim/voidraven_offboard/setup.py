from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'voidraven_offboard'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share' + package_name + '/resouce', glob('ros_gz_bridge/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nico',
    maintainer_email='23910712@sun.ac.za',
    description='TODO: Package description',
    license='TODO: License declaration',
    # tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'position_command_input = voidraven_offboard.position_command_input:main',
            'position_control = voidraven_offboard.position_control:main',
            'visualizer = voidraven_offboard.visualizer:main',
            'terminal_launches = voidraven_offboard.terminal_launches:main',
        ],
    },
)