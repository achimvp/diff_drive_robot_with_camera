import gymnasium as gym
from gymnasium.envs.mujoco import MujocoEnv, MujocoRenderer
import numpy as np
import matplotlib.pyplot as plt
import mujoco


DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}

WHEEL_BASE = 0.32  # Distance between the two wheels (in meters)
LEFT_WHEEL_RADIUS = 0.035  # Radius of the left wheel (in meters)
RIGHT_WHEEL_RADIUS = 0.035  # Radius of the right wheel (in meters)

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

    # Convert angular velocities to linear velocities
    left_wheel_linear_velocity = left_wheel_velocity * LEFT_WHEEL_RADIUS
    right_wheel_linear_velocity = right_wheel_velocity * RIGHT_WHEEL_RADIUS

    # Calculate the linear and angular velocity of the robot
    linear_velocity = (left_wheel_linear_velocity + right_wheel_linear_velocity) / 2
    angular_velocity = (right_wheel_linear_velocity - left_wheel_linear_velocity) / WHEEL_BASE

    return linear_velocity, angular_velocity

class BoxbotEnv(MujocoEnv):
    def __init__(self, model_path: str, frame_skip: int = 1, camera_default_config = DEFAULT_CAMERA_CONFIG, **kwargs):

        observation_space = gym.spaces.Dict(spaces={
            "state": gym.spaces.Box(
                low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32
            ),
            "image": gym.spaces.Box(
                low=0, high=255, shape=(480, 640, 3), dtype=np.uint8
            )
        })
        MujocoEnv.__init__(
            self,
            model_path=model_path,
            frame_skip=frame_skip,
            observation_space=observation_space,
            width=640,
            height=480,
            camera_name="onboard_camera",
            default_camera_config=camera_default_config,
            **kwargs
        )

    def get_camera_image(self):
        return self.mujoco_renderer.render(render_mode="rgb_array")

    def step(self, action):
        # Convert the odometry command to wheel velocities
        left_wheel_ctrl, right_wheel_ctrl = odom_to_wheel_velocities(action[:2])
        ctrl = [left_wheel_ctrl, right_wheel_ctrl, *action[2:]]

        self.do_simulation(ctrl, self.frame_skip)

        obs = self._get_obs()
        reward = self._get_reward()
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info
    
    def reset_model(self):
        self.set_state(self.init_qpos, self.init_qvel)
        obs = self._get_obs()
        return obs
    
    def _get_reward(self):
        # get the position of the robot from the simulation
        robot_pos = self.get_body_com("chassis")

        # get the postion of the goal from the simulation
        target_pos = self.get_body_com("target")  # Get the center of mass position of

        # calculate the distance to the goal
        distance_to_goal = np.linalg.norm(robot_pos - target_pos)
        distance_reward = -distance_to_goal

        reward = distance_reward
        return reward
    
    def _get_obs(self):
        # Implement the function to return the current observation
        linear_acc = self.data.sensor("imu_accel").data
        angular_vel = self.data.sensor("imu_gyro").data
        left_wheel_vel = self.data.sensor("left_wheel_vel").data
        right_wheel_vel = self.data.sensor("right_wheel_vel").data
        linear_vel_odom, angular_vel_odom = wheel_velocities_to_odom(left_wheel_vel, right_wheel_vel)
        camera_body_pos = self.data.sensor("camera_body_pos").data
        camera_head_pos = self.data.sensor("camera_head_pos").data

        camera_image = self.get_camera_image()

        state = np.concatenate([linear_acc, angular_vel, linear_vel_odom, angular_vel_odom, camera_head_pos, camera_body_pos], dtype=np.float32)
        return {"state": state, "image": camera_image}



if __name__ == "__main__":
    # env = BoxbotEnv(model_path="./configs/Mujoco/simple_world.xml", frame_skip=1, render_mode="human")
    env = BoxbotEnv(model_path="./envs/mujoco/boxbot_default_world.xml", frame_skip=50, render_mode="human")
    N_steps = 200
    N_rollouts = 2
    x_acc = np.empty((N_rollouts,N_steps))
    rewards = np.empty((N_rollouts,N_steps))
    for rollout in range(N_rollouts):
        obs, info = env.reset()
        for i in range(N_steps):
            if i > N_steps//2:
                action = [0, 1, 1, 1] # rotate in place for the first 500 steps
            else:
                action = [1, 0, -1, -1] # move forward for the next 500 steps
            obs, reward, terminated, truncated, info = env.step(action)
            x_acc[rollout, i] = obs["state"][0]
            rewards[rollout, i] = reward
            env.render()
    # print("Observation:", obs)
    # print("Info:", info)
    env.close()

    plt.plot(rewards.T)
    plt.show()