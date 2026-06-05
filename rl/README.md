# Reinforcement Learning for the Boxbot
This folder contains the parts to train RL policies for the Boxbot. It supports different Gazebo environments.
The structure is as follows:
- `algos`
- `configs`
- `envs`
- `scripts`
- `checkpoints`

## Environments
RL environments are implemented in the `envs` folder. We support MuJoCo environments for now.
The folder `mujoco` contains the MJCF files for the Boxbot, the actuators and sensors, and a simple maze world. The file `mujoco_env.py` contains a `MujocoEnv` wrapper around this maze world. This wrapper exposes the standard `Gymnasium` API for RL environments.

## Scripts
To train, evaluate and export policies dedicated scripts are avaialabel in the `scripts` folder. These can also be used for automatic experiment runs. 

For testing purposes the folder `scripts` also contains a ROS node to bridge between the RL policy's format for actions and observations and the format used in ROS messages.

## Hyperparameters and Configurations
`yaml` files with hyperparameters and configurations for different policy networks and RL algorithms are available in the `configs` folder.

## Algorithms
The `algos` folder contains implementations of different RL algorithms. In the future this might become a linked repository.