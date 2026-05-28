# Full aggregated observation for the boxbot
std_msgs/Header header

# IMU
float32[3] linear_acceleration
float32[3] angular_velocity

# Odometry
float32[3] position
float32[3] velocity

# Camera Turret
boxbot_interfaces/CameraTurretPosition camera_turret_position

# Image
sensor_msgs/Image camera_image
sensor_msgs/CameraInfo camera_info