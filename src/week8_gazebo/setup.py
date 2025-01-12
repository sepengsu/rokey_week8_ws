from setuptools import setup

package_name = 'week8_gazebo'

setup(
    name=package_name,
    version='2.2.6',  # package.xml과 동일하게 설정
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaewon Seo',
    maintainer_email='na06219@g.skku.edu',
    description='Multi robot support with TurtleBot3 using ROS 2 Humble',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'compressed_node = week8_gazebo.compressed_node:main',
        ],
    },
)
