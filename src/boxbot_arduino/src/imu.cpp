#include "boxbot_arduino/imu.hpp"

IMU::IMU(const std::string &imu_name)

{
  setup(imu_name);
}

void IMU::setup(const std::string &imu_name)
{
  name = imu_name;
}