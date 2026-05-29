# Diff drive with camera
A differential drive robot with a 2DOFs movable camera turret with the lovely nickname *boxbot*.

## Projekt overview
The repository contains a ROS2 workspace and a separate folder with RL and simulation code.

```
diff_drive_with_camera/          # Git-Root
│
├── ros_ws/                      # ROS2 Workspace
│   └── src/
│       ├── boxbot_arduino/
│       ├── boxbot_bringup/
│       ├── boxbot_interfaces/
│       ├── description/
│       └── simple_control_package/
│
└── rl/                          # RL-Code
    ├── envs/
    │   ├── __init__.py
    │   └── boxbot_env.py        # Gymnasium Wrapper
    ├── configs/                 # Hyperparameters, Training Configs
    │   └── ppo_config.yaml
    ├── scripts/                 # Entrypoints
    │   ├── train.py
    │   ├── eval.py
    │   └── export_policy.py
    ├── checkpoints/             # Trained Models
    └── README.md
```

### `boxbot_arduino`
ROS2 node to communicate with the Arduino via serial connection. Supports the communication with:
- motors
- motor encoders
- camera turret servos
- IMU

### `boxbot_adapter`
ROS2 node for collecting different sensor topics into one observation. Used for downstream tasks like RL.

### `boxbot_bringup`
Contains mostly configurations and launch scripts for starting the real robot or Gazebo simulation.

### `boxbot_interfaces`
Message, service, and action definitions used to communicate with the Boxbot.

### `description`
URDF files for the robot, mesh assets for complex parts, world files for Gazebo simulation.

### `simple_control_package`


## Install

For using the template with Gazebo Fortress switch to the `fortress` branch of this repository, otherwise use the default branch `main` for Gazebo Harmonic onwards.

### Requirements

1. Choose a ROS and Gazebo combination https://gazebosim.org/docs/latest/ros_installation

   Note: If you're using a specific and unsupported Gazebo version with ROS 2, you might need to set the `GZ_VERSION` environment variable, for example:

    ```bash
    export GZ_VERSION=harmonic
    ```
    Also need to build [`ros_gz`](https://github.com/gazebosim/ros_gz) and [`sdformat_urdf`](https://github.com/ros/sdformat_urdf) from source if binaries are not available for your chosen combination.

1. Install necessary tools

    ```bash
    sudo apt install python3-vcstool python3-colcon-common-extensions git wget
    ```

## Usage

1. Install dependencies

    ```bash
    cd ~/template_ws
    source /opt/ros/$ROS_DISTRO/setup.bash
    sudo rosdep init
    rosdep update
    rosdep install --from-paths src --ignore-src -r -i -y --rosdistro <ROS_DISTRO>
    ```

1. Build the project

    ```bash
    colcon build --cmake-args -DBUILD_TESTING=ON
    ```

1. Source the workspace

    ```bash
    source source_workspace.sh
    ```

1. Launch the simulation

    ```bash
    ros2 launch boxbot_bringup ros2_control.launch.py
    ```

1. Launch the real robot

    ```bash
    ros2 launch boxbot_bringup real_robot.launch.py
    ```

## TODOs

- [ ] Give a high level overview over the Boxbot workspace
- [x] Collect the launch scripts inside the `boxbot_bringup` package
- [ ] Write some kind of RL environment/loop for training the Boxbot
- [ ] Implement some CI/CD pipelines for the project e.g. build, lint, test
- [ ] Implement tests for different robot features