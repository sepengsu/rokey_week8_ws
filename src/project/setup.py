from setuptools import find_packages, setup
from glob import glob
package_name = 'project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (f'share/{package_name}/launch', glob('launch/*.launch.py')),
        (f'share/{package_name}/config', glob('config/*.yaml')),
        (f'share/{package_name}/ui', glob('ui/*.ui')),
        (f'share/{package_name}/yolo', glob('yolo/*.pt')),
        (f'share/{package_name}/database', glob('database/*.db')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jaenote',
    maintainer_email='na06219@naver.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': ['pytest', 'mock'],
    },
    entry_points={
        'console_scripts': [
            'gui = project.gui:main',
            'robot_cam = project.robot_cam:main',
            'world_cam = project.detection.world_cam:main',
            'control = project.control:main',
        ],
    },
)
