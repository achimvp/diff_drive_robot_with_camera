import gymnasium as gym
import rclpy
import numpy as np
from boxbot_interfaces.msg import BoxbotObservation 
from geometry_msgs.msg import Twist # we use this for diff drive control
from std_msgs.msg import Float32MultiArray  # we use this for camera turret commands

class GazeboEnv(gym.Env):
    def __init__(self, env_name):
        super(GazeboEnv, self).__init__()
        self.env_name = env_name
        # Initialize your Gazebo environment here
        ## Create action and observation spaces
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(5,))  # linear velocity x and y, angular velocity yaw, camera turret position yaw and pitch

        self.observation_space = gym.spaces.Dict({
            "state": gym.spaces.Box(low=-np.inf, high=np.inf, shape=(14,)),  # linear acceleration x,y,z, angular velocity x,y,z, position x, y, yaw, velocity x,y,yaw, camera turret position yaw and pitch
            "image": gym.spaces.Box(low=0, high=255, shape=(480, 640, 3), dtype=np.uint8)  # RGB image from the camera
        })

        ## Create ROS publishers and subscribers for communication with Gazebo
        rclpy.init()
        self.node = rclpy.create_node('gazebo_env')
        self.observation_subscriber = self.node.create_subscription(
            BoxbotObservation,
            '/observation',
            self._observation_callback,
            10
        )
        self.twist_publisher = self.node.create_publisher(Twist, '/cmd_vel', 10)  # Assuming you use Twist messages for velocity commands
        self.camera_turret_publisher = self.node.create_publisher(Float32MultiArray, '/camera_body_controller/commands', 10)  # Assuming you have a custom message for camera
    
    def _ros_obs_to_gym_obs(self, ros_obs):
        # Convert the ROS observation message to the format expected by the observation space
        state = np.array([
            ros_obs.linear_acceleration.x,
            ros_obs.linear_acceleration.y,
            ros_obs.linear_acceleration.z,
            ros_obs.angular_velocity.x,
            ros_obs.angular_velocity.y,
            ros_obs.angular_velocity.z,
            ros_obs.position.x,
            ros_obs.position.y,
            ros_obs.position.yaw,
            ros_obs.velocity.x,
            ros_obs.velocity.y,
            ros_obs.velocity.yaw,
            ros_obs.camera_turret_position.yaw,
            ros_obs.camera_turret_position.pitch
        ], dtype=np.float32)

        image = np.array(ros_obs.image.data, dtype=np.uint8).reshape((480, 640, 3))  # Assuming the image is sent as a flat array

        return {"state": state, "image": image}
    
    def _gym_action_to_ros_cmd(self, action):
        # Convert the action from the gym format to the ROS command message
        twist_cmd = Twist()
        twist_cmd.linear.x = action[0]  # linear velocity x
        twist_cmd.linear.y = action[1]  # linear velocity y
        twist_cmd.angular.z = action[2]  # angular velocity yaw

        camera_turret_cmd = Float32MultiArray()
        camera_turret_cmd.data = action[3:5] # yaw and pitch for camera turret

        return twist_cmd, camera_turret_cmd

    def _observation_callback(self, msg):
        # Process the incoming observation message and update the environment's state
        self.current_obs = self._ros_obs_to_gym_obs(msg)
    
    def _get_obs(self):
        pass

    def reset(self):
        # Reset the Gazebo environment and return the initial observation
        obs = self._get_obs()
        return obs, info

    def step(self, action):
        # Apply the action to the Gazebo environment and return the new observation, reward, done, and info
        twist_cmd, camera_turret_cmd = self._gym_action_to_ros_cmd(action)
        self.twist_publisher.publish(twist_cmd)
        self.camera_turret_publisher.publish(camera_turret_cmd)

        return obs, reward, terminated, truncated, info

    def render(self, mode='human'):
        # Render the Gazebo environment (if applicable)
        pass

    def close(self):
        # Clean up resources when closing the environment
        pass