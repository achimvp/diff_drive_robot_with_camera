import gymnasium as gym
from gymnasium.envs.mujoco import MujocoEnv
import numpy as np
import matplotlib.pyplot as plt

DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}

def odom_to_wheel_velocities(odom_cmd):
    """
    Convert an odometry command (linear and angular velocity) to left and right wheel velocities.
    This is a common conversion for differential drive robots.

    Args:
        odom_cmd: A tuple (linear_velocity, angular_velocity)
    Returns:
        A tuple (left_wheel_velocity, right_wheel_velocity)
    """
    linear_velocity, angular_velocity = odom_cmd
    WHEEL_BASE = 0.3  # Distance between the two wheels (in meters)
    LEFT_WHEEL_RADIUS = 0.05  # Radius of the left wheel (in meters)
    RIGHT_WHEEL_RADIUS = 0.05  # Radius of the right wheel (in
    
    # Calculate the left and right wheel velocities
    left_wheel_velocity = linear_velocity - (angular_velocity * WHEEL_BASE / 2)
    left_wheel_angular_velocity = left_wheel_velocity / LEFT_WHEEL_RADIUS  # Assuming wheel radius is 0.1 meters
    right_wheel_velocity = linear_velocity + (angular_velocity * WHEEL_BASE / 2)
    right_wheel_angular_velocity = right_wheel_velocity / RIGHT_WHEEL_RADIUS  # Assuming wheel radius is 0.1 meters
    
    return left_wheel_angular_velocity, right_wheel_angular_velocity

def wheel_velocities_to_odom(left_wheel_velocity, right_wheel_velocity):
    """
    Convert left and right wheel velocities to an odometry command (linear and angular velocity).
    This is the inverse of the odom_to_wheel_velocities function.

    Args:
        left_wheel_velocity: Angular velocity of the left wheel (in radians per second)
        right_wheel_velocity: Angular velocity of the right wheel (in radians per second)
    Returns:
        A tuple (linear_velocity, angular_velocity)
    """
    WHEEL_BASE = 0.3  # Distance between the two wheels (in meters)
    LEFT_WHEEL_RADIUS = 0.05  # Radius of the left wheel (in meters)
    RIGHT_WHEEL_RADIUS = 0.05  # Radius of the right wheel (in meters)

    # Convert angular velocities to linear velocities
    left_wheel_linear_velocity = left_wheel_velocity * LEFT_WHEEL_RADIUS
    right_wheel_linear_velocity = right_wheel_velocity * RIGHT_WHEEL_RADIUS

    # Calculate the linear and angular velocity of the robot
    linear_velocity = (left_wheel_linear_velocity + right_wheel_linear_velocity) / 2
    angular_velocity = (right_wheel_linear_velocity - left_wheel_linear_velocity) / WHEEL_BASE

    return linear_velocity, angular_velocity

class BoxbotEnv(MujocoEnv):
    def __init__(self, model_path: str, frame_skip: int = 1, camera_default_config = DEFAULT_CAMERA_CONFIG, **kwargs):

        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32
        )
        MujocoEnv.__init__(
            self,
            model_path=model_path,
            frame_skip=frame_skip,
            observation_space=self.observation_space,
            default_camera_config=camera_default_config,
            **kwargs
        )
        print(self.model.actuator_ctrlrange)
        print(self.action_space)
        # self.do_simulation([0, 0, 0], self.frame_skip)  # Initialize the simulation

    def step(self, action):
        # Implement the step function to interact with the environment
        left_wheel_ctrl, right_wheel_ctrl = odom_to_wheel_velocities(action[:2]) # Convert odometry command to wheel velocities
        ctrl = [left_wheel_ctrl, right_wheel_ctrl, *action[2:]]
        print(f"Action: {action}, Left Wheel Ctrl: {left_wheel_ctrl}, Right Wheel Ctrl: {right_wheel_ctrl}")
        self.do_simulation(ctrl, self.frame_skip)
        obs = self._get_obs()
        reward = 0.0  # Define your reward function here
        terminated = False  # Define your termination condition here
        truncated = False  # Define your truncation condition here
        info = {}  # Add any additional info you want to return
        return obs, reward, terminated, truncated, info

    def reset_model(self):
        # Implement the reset_model function to reset the environment

        self.set_state(self.init_qpos, self.init_qvel)
        obs = self._get_obs()
        return obs
    
    def _get_obs(self):
        # Implement the function to return the current observation
        linear_acc = self.data.sensor("imu_accel").data
        angular_vel = self.data.sensor("imu_gyro").data
        left_wheel_vel = self.data.sensor("left_wheel_vel").data
        right_wheel_vel = self.data.sensor("right_wheel_vel").data
        linear_vel_odom, angular_vel_odom = wheel_velocities_to_odom(left_wheel_vel, right_wheel_vel)
        camera_body_pos = self.data.sensor("camera_body_pos").data
        camera_head_pos = self.data.sensor("camera_head_pos").data

        observation = np.concatenate([linear_acc, angular_vel, linear_vel_odom, angular_vel_odom, camera_head_pos, camera_body_pos])
        return observation.astype(np.float32)



if __name__ == "__main__":
    # env = BoxbotEnv(model_path="./configs/Mujoco/simple_world.xml", frame_skip=1, render_mode="human")
    env = BoxbotEnv(model_path="./envs/mujoco/boxbot_default_world.xml", frame_skip=50, render_mode="human")
    obs, info = env.reset()
    N = 500
    x_acc = np.empty((N,))
    for i in range(N):
        if i > N//2:
            action = [0, 1, 1, 1] # rotate in place for the first 500 steps
        else:
            action = [1, 0, -1, -1] # move forward for the next 500 steps
        obs, reward, terminated, truncated, info = env.step(action)
        x_acc[i] = obs[0]
        env.render()
    print("Observation:", obs)
    print("Info:", info)
    env.close()

    plt.plot(x_acc)
    plt.show()