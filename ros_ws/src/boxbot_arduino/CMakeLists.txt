cmake_minimum_required(VERSION 3.8)
project(boxbot_arduino)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
set(THIS_PACKAGE_INCLUDE_DEPENDS
  hardware_interface
  pluginlib
  rclcpp
  rclcpp_lifecycle
  serial
  controller_manager
)

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
foreach(Dependency IN ITEMS ${THIS_PACKAGE_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()

add_library(boxbot_arduino SHARED src/boxbot_arduino.cpp src/wheel.cpp src/arduino_comms.cpp src/servo.cpp src/imu.cpp)

target_include_directories(
  boxbot_arduino
  PRIVATE
  include
)

ament_target_dependencies(
  boxbot_arduino
  hardware_interface
  controller_manager
  serial
  rclcpp
  pluginlib
)

pluginlib_export_plugin_description_file(hardware_interface boxbot_hardware_interface.xml)

install(
  TARGETS boxbot_arduino
  DESTINATION lib
)

ament_export_libraries(
  boxbot_arduino
)
ament_export_dependencies(
  hardware_interface
  controller_manager
  rclcpp
  pluginlib
  serial
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
