#include "boxbot_arduino/servo.hpp"

#include <cmath>


Servo::Servo(const std::string &servo_name)

{
  setup(servo_name);
}


void Servo::setup(const std::string &servo_name)
{
  name = servo_name;
}

double Servo::calcPos()
{
  return (enc - 90) / 360.0 * 2 * M_PI; // Do I have to convert this to radians? It is already in degrees, so maybe not? Depends on how the Arduino is sending it. If it is sending degrees, then we can just use it as is. If it is sending radians, then we need to convert it to degrees. For now, let's assume it is sending degrees and we want to use it as is.
}