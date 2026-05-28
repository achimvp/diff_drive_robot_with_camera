#ifndef BOXBOT_ARDUINO_IMU_H
#define BOXBOT_ARDUINO_IMU_H

#include <string>



class IMU
{
    public:

    std::string name = "";
    double orientation[4] = {0, 0, 0, 1}; // Quaternion (x, y, z, w)
    double angular_velocity[3] = {0, 0, 0}; // (x, y, z)
    double linear_acceleration[3] = {0, 0, 0}; // (x, y, z)

    IMU() = default;

    IMU(const std::string &imu_name);
    
    void setup(const std::string &imu_name);


};


#endif // BOXBOT_ARDUINO_IMU_H