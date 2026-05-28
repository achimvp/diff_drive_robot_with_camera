# Reinforcement Learning for the Boxbot
This folder contains the parts to train RL policies for the Boxbot. It supports different Gazebo environments.
The structure is as follows:
- `algos`
- `configs`
- `envs`
- `scripts`
- `checkpoints`

## Environments
RL environments are implemented in the `envs` folder. We support Gazebo environments for now.

## Scripts
To train, evaluate and export policies dedicated scripts are avaialabel in the `scripts` folder. These can also be used for automatic experiment runs.

## Hyperparameters and Configurations
`yaml` files with hyperparameters and configurations for different policy networks and RL algorithms are available in the `configs` folder.

## Algorithms
The `algos` folder contains implementations of different RL algorithms. In the future this might become a linked repository.