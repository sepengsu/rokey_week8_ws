cmake_minimum_required(VERSION 3.5)
project(week8_gazebo)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Python 패키지 설치
ament_python_install_package(${PROJECT_NAME})

# 리소스 설치
install(
  DIRECTORY launch models rviz urdf worlds params map
  DESTINATION share/${PROJECT_NAME}/
)

# 환경 설정 파일 설치 (파일이 존재할 경우)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/multi_robot.dsv.in")
  ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/multi_robot.dsv.in")
endif()

ament_package()
