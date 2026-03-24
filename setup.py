import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'multi_sensor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'scripts'), glob(os.path.join('scripts','rosbag_record.bash'))),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', 'params.yaml')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='univalle',
    maintainer_email='alvaro.navarro@correounivalle.edu.co',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'zed_camera_tf = multi_sensor.zed_camera_tf:main',
        ],
    },
)
