#include "boxbot_arduino/boxbot_arduino.hpp"


#include "hardware_interface/types/hardware_interface_type_values.hpp"



BoxbotSystemHardware::BoxbotSystemHardware()
    : logger_(rclcpp::get_logger("BoxbotSystemHardware"))
{}


hardware_interface::CallbackReturn BoxbotSystemHardware::on_init(const hardware_interface::HardwareComponentInterfaceParams & params)
{
  if (hardware_interface::SystemInterface::on_init(params) != CallbackReturn::SUCCESS)
  {
    return CallbackReturn::ERROR;
  }

  RCLCPP_INFO(logger_, "Configuring...");

  time_ = std::chrono::system_clock::now();

  cfg_.left_wheel_name = info_.hardware_parameters["left_wheel_name"];
  cfg_.right_wheel_name = info_.hardware_parameters["right_wheel_name"];
  cfg_.loop_rate = std::stof(info_.hardware_parameters["loop_rate"]);
  cfg_.device = info_.hardware_parameters["device"];
  cfg_.baud_rate = std::stoi(info_.hardware_parameters["baud_rate"]);
  cfg_.timeout = std::stoi(info_.hardware_parameters["timeout"]);
  cfg_.enc_counts_per_rev_left = std::stoi(info_.hardware_parameters["enc_counts_per_rev_left"]);
  cfg_.enc_counts_per_rev_right = std::stoi(info_.hardware_parameters["enc_counts_per_rev_right"]);

  cfg_.camera_body_name = info_.hardware_parameters["camera_body_name"];
  cfg_.camera_head_name = info_.hardware_parameters["camera_head_name"];
  cfg_.imu_name = info_.hardware_parameters["imu_name"];

  // Set up the wheels
  l_wheel_.setup(cfg_.left_wheel_name, cfg_.enc_counts_per_rev_left);
  r_wheel_.setup(cfg_.right_wheel_name, cfg_.enc_counts_per_rev_right);

  // Set up the camera turret
  camera_body_.setup(cfg_.camera_body_name);
  camera_head_.setup(cfg_.camera_head_name);

  // Set up the IMU
  imu_.setup(cfg_.imu_name);

  // Set up the Arduino
  arduino_.setup(cfg_.device, cfg_.baud_rate, cfg_.timeout);  

  RCLCPP_INFO(logger_, "Finished Configuration");

  return CallbackReturn::SUCCESS;
}
hardware_interface::CallbackReturn BoxbotSystemHardware::on_configure(
  const rclcpp_lifecycle::State & previous_state)
{
  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> BoxbotSystemHardware::export_state_interfaces()
{
  // We need to set up a position and a velocity interface for each wheel

  std::vector<hardware_interface::StateInterface> state_interfaces;

  state_interfaces.emplace_back(hardware_interface::StateInterface(l_wheel_.name, hardware_interface::HW_IF_VELOCITY, &l_wheel_.vel));
  state_interfaces.emplace_back(hardware_interface::StateInterface(l_wheel_.name, hardware_interface::HW_IF_POSITION, &l_wheel_.pos));
  state_interfaces.emplace_back(hardware_interface::StateInterface(r_wheel_.name, hardware_interface::HW_IF_VELOCITY, &r_wheel_.vel));
  state_interfaces.emplace_back(hardware_interface::StateInterface(r_wheel_.name, hardware_interface::HW_IF_POSITION, &r_wheel_.pos));
  state_interfaces.emplace_back(hardware_interface::StateInterface(camera_body_.name, hardware_interface::HW_IF_POSITION, &camera_body_.pos));
  state_interfaces.emplace_back(hardware_interface::StateInterface(camera_body_.name, hardware_interface::HW_IF_VELOCITY, &camera_body_.vel));
  state_interfaces.emplace_back(hardware_interface::StateInterface(camera_head_.name, hardware_interface::HW_IF_POSITION, &camera_head_.pos));
  state_interfaces.emplace_back(hardware_interface::StateInterface(camera_head_.name, hardware_interface::HW_IF_VELOCITY, &camera_head_.vel));

  // Add IMU state interfaces
  // auto imu_state_interfaces = imu_.export_state_interfaces();
  // state_interfaces.insert(state_interfaces.end(), imu_state_interfaces.begin(), imu_state_interfaces.end());
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "orientation.x", &imu_.orientation[0]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "orientation.y", &imu_.orientation[1]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "orientation.z", &imu_.orientation[2]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "orientation.w", &imu_.orientation[3]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "angular_velocity.x", &imu_.angular_velocity[0]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "angular_velocity.y", &imu_.angular_velocity[1]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "angular_velocity.z", &imu_.angular_velocity[2]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "linear_acceleration.x", &imu_.linear_acceleration[0]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "linear_acceleration.y", &imu_.linear_acceleration[1]));
  state_interfaces.emplace_back(hardware_interface::StateInterface(imu_.name, "linear_acceleration.z", &imu_.linear_acceleration[2]));


  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> BoxbotSystemHardware::export_command_interfaces()
{
  // We need to set up a velocity command interface for each wheel

  std::vector<hardware_interface::CommandInterface> command_interfaces;

  command_interfaces.emplace_back(hardware_interface::CommandInterface(l_wheel_.name, hardware_interface::HW_IF_VELOCITY, &l_wheel_.cmd));
  command_interfaces.emplace_back(hardware_interface::CommandInterface(r_wheel_.name, hardware_interface::HW_IF_VELOCITY, &r_wheel_.cmd));
  command_interfaces.emplace_back(hardware_interface::CommandInterface(camera_body_.name, hardware_interface::HW_IF_POSITION, &camera_body_.cmd));
  command_interfaces.emplace_back(hardware_interface::CommandInterface(camera_head_.name, hardware_interface::HW_IF_POSITION, &camera_head_.cmd));

  return command_interfaces;
}


hardware_interface::CallbackReturn BoxbotSystemHardware::on_activate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Starting Controller...");

  arduino_.sendEmptyMsg();
  // arduino.setPidValues(9,7,0,100);
  // arduino.setPidValues(14,7,0,100);
  arduino_.setPidValues(30, 20, 0, 100);

  return CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn BoxbotSystemHardware::on_deactivate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(logger_, "Stopping Controller...");

  return CallbackReturn::SUCCESS;
}

hardware_interface::return_type BoxbotSystemHardware::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{

  // TODO fix chrono duration

  // Calculate time delta
  auto new_time = std::chrono::system_clock::now();
  std::chrono::duration<double> diff = new_time - time_;
  double deltaSeconds = diff.count();
  time_ = new_time;


  if (!arduino_.connected())
  {
    return return_type::ERROR;
  }


  // Read encoder values
  arduino_.readEncoderValues(l_wheel_.enc, r_wheel_.enc);
  
  double pos_prev = l_wheel_.pos;
  l_wheel_.pos = l_wheel_.calcEncAngle();
  l_wheel_.vel = (l_wheel_.pos - pos_prev) / deltaSeconds;

  pos_prev = r_wheel_.pos;
  r_wheel_.pos = r_wheel_.calcEncAngle();
  r_wheel_.vel = (r_wheel_.pos - pos_prev) / deltaSeconds;
  
  arduino_.readServoValues(camera_body_.enc, camera_head_.enc);
  pos_prev = camera_body_.pos;
  camera_body_.pos = camera_body_.calcPos();
  camera_body_.vel = (camera_body_.pos - pos_prev) / deltaSeconds;

  pos_prev = camera_head_.pos;
  camera_head_.pos = camera_head_.calcPos();
  camera_head_.vel = (camera_head_.pos - pos_prev) / deltaSeconds;

  // Read IMU values
  arduino_.readIMUValues(imu_.linear_acceleration, imu_.angular_velocity);

  return return_type::OK;

  
}

hardware_interface::return_type BoxbotSystemHardware::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{

  if (!arduino_.connected())
  {
    return return_type::ERROR;
  }

  arduino_.setMotorValues(l_wheel_.cmd / l_wheel_.rads_per_count / cfg_.loop_rate, r_wheel_.cmd / r_wheel_.rads_per_count / cfg_.loop_rate);
  arduino_.setServoValues(camera_body_.cmd / (2 * M_PI) * 360 + 90, camera_head_.cmd / (2 * M_PI) * 360 + 90);


  return return_type::OK;


  
}



#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  BoxbotSystemHardware, hardware_interface::SystemInterface
)