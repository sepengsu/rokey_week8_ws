from setuptools import find_packages, setup
from glob import glob
import os
from pathlib import Path

package_name = 'week8_gazebo'

def copy_folder_file(source_dir, target_dir, pattern="**/*"):
    """
    Collect files matching the pattern and preserve their relative folder structure.

    Args:
        source_dir (str): Root directory to search for files.
        target_dir (str): Destination base directory for files.
        pattern (str): Glob pattern for file search (default: "**/*").

    Returns:
        list: List of tuples suitable for `data_files` in setup.py.
    """
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    data_files = []
    
    # Search for files matching the pattern
    for filepath in source_dir.glob(pattern):
        if filepath.is_file():  # Ensure it's a file
            # Compute relative path from the source directory
            relative_path = filepath.relative_to(source_dir)
            # Create the target installation path
            install_path = target_dir / relative_path.parent
            # Append to the data files list
            data_files.append((str(install_path), [str(filepath)]))
    
    return data_files

launchs = copy_folder_file("launch", f"share/{package_name}/launch")
maps = copy_folder_file("map", f"share/{package_name}/map")
models = copy_folder_file("models", f"share/{package_name}/models")
params = copy_folder_file("params", f"share/{package_name}/params")
rviz = copy_folder_file("rviz", f"share/{package_name}/rviz")
urdf = copy_folder_file("urdf", f"share/{package_name}/urdf")
worlds = copy_folder_file("worlds", f"share/{package_name}/worlds")
config = copy_folder_file("config", f"share/{package_name}/config")
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        *launchs,
        *maps,
        *models,
        *params,
        *rviz,
        *urdf,
        *worlds,
        *config,
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jaewon',
    maintainer_email='na06219@naver.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'compressed_node = week8_gazebo.compressed_node:main',
            'keyboard_control = week8_gazebo.keyboard_control:main',
        ],
    },
)
