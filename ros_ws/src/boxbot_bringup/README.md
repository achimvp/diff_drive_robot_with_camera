# boxbot_bringup

## Overview

`boxbot_bringup` contains different launch scripts to start the Boxbot simulations and/or real robot.

**What This Package Does**
- Launches Gazebo simulation or real robot
- Spawns the Boxbot robot in the Gazebo simulation
- Starts the rviz visualization
- Starts the controllers (ROS2 control) for camera turret and diff drive
- Starts the sensor broadcasters (ROS2 control) for camera and IMU
- Starts observation collection node for synchronized whole robot observation

## Quick Start

### Basic Simulation

### Real robot
By default the launch script for the real robot also spins up a digital twin in RViz. To prevent RViz from starting set the `spin_up_digital_twin` flag to `false`.

## Launch Files
