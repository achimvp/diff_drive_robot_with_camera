#ifndef BOXBOT_ARDUINO_CONFIG_H
#define BOXBOT_ARDUINO_CONFIG_H

#include <string>


struct Config
{
  std::string left_wheel_name = "left_wheel";
  std::string right_wheel_name = "right_wheel";
  float loop_rate = 30;
  std::string device = "/dev/ttyACM0";
  int baud_rate = 115200;
  int timeout = 1000;
  int enc_counts_per_rev_left = 6533;
  int enc_counts_per_rev_right = 6533;
  std::string camera_body_name = "camera_body_joint";
  std::string camera_head_name = "camera_head_joint";
  std::string imu_name = "imu_sensor";
  std::string imu_topic = "imu/data";
};


#endif // BOXBOT_ARDUINO_CONFIG_H