import os
from time import sleep

from gz.sim import Server, ServerConfig
from gz.transport import Node
from gz.msgs.world_control_pb2 import WorldControl
from gz.msgs.boolean_pb2 import Boolean

file_path = os.path.dirname(os.path.realpath(__file__))

node = Node()

from gz.msgs.world_stats_pb2 import WorldStatistics
import threading

class SimStats:
    def __init__(self, world_name: str):
        self._iterations = 0
        self._lock = threading.Lock()
        
        node = Node()
        node.subscribe(
            WorldStatistics,
            f"/world/{world_name}/stats",
            self._cb
        )

    def _cb(self, msg: WorldStatistics) -> None:
        print(f"Received stats: iterations={msg.iterations}")
        with self._lock:
            self._iterations = msg.iterations

    @property
    def iterations(self) -> int:
        with self._lock:
            return self._iterations

def set_paused(world_name: str, paused: bool):
    """
    This function is used to pause and unpause the simulation.
    """
    req = WorldControl()
    req.pause = paused
    node.request("/world/" + world_name + "/control", req, WorldControl, Boolean, 1000)

def step(server, n_steps):
    server.run(True, n_steps, False) # _blocking, _iterations, _paused

if __name__ == "__main__":
    config = ServerConfig()
    config.set_sdf_file(os.path.join(file_path, '../configs/simple_world.sdf'))
    server = Server(config)
    server.run(False, 0, False) # _blocking, _iterations, _paused
    sleep(0.1)

    print(node.topic_list())
    stats = SimStats("empty")

    print("Running the server for 100 steps to initialize the world...")
    step(server, 100)
    print(node.topic_list())

    # server.run(True, 200, False) # _blocking, _iterations, _paused
    sleep(0.1)

    print(stats.iterations)
    print("Server has been initialized. You can now interact with the world.")







# import os
# import gymnasium as gym
# import numpy as np

# from gz.common import set_verbosity
# from gz.sim import TestFixture, World, world_entity, Model, Link, get_install_prefix
# from gz.math import Vector3d

# # from stable_baselines3 import PPO
# import time
# import subprocess

# # use xacro to generate the robot description
# # then spawn the robot in the world using the gazebo api

# file_path = os.path.dirname(os.path.realpath(__file__))

# def run_gui():
#     """
#     This function looks for your gz sim installation and looks for
#     an instance of the gui client
#     """
#     if os.name == 'nt':
#         base = os.path.join(get_install_prefix(), "libexec", "runGui.exe")
#     else:
#         base = os.path.join(get_install_prefix(), "libexec", "gz", "sim10", "gz-sim-gui-client")
#     subprocess.Popen(base)

# class GzRewardScorer:
#     """
#     This Gazebo System is used to introspect and score the world.
#     """
#     def __init__(self):
#         """
#         We initiallize a TestFixture: This is a simple fixture that is used
#         to load our gazebo world. We also inject the code to be executed
#         on each run.
#         """
#         self.fixture = TestFixture(os.path.join(file_path, '../configs/simple_world.sdf'))
#         self.fixture.on_pre_update(self.on_pre_update)
#         self.fixture.on_post_update(self.on_post_update)
#         self.command = None # This variable is used as a bridge between Gymnasium and gazebo
#         self.fixture.finalize()
#         self.server = self.fixture.server()
#         self.terminated = False

#     def on_pre_update(self, info, ecm):
#         """
#         on_pre_update is used to command the model vehicle.
#         """
#         world = World(world_entity(ecm))
#         self.model = Model(world.model_by_name(ecm, "vehicle_green"))
#         self.pole_entity = self.model.link_by_name(ecm, "pole")
#         self.chassis_entity = self.model.link_by_name(ecm, "chassis")
#         self.pole = Link(self.pole_entity)
#         self.pole.enable_velocity_checks(ecm)
#         self.chassis = Link(self.chassis_entity)
#         self.chassis.enable_velocity_checks(ecm)
#         if self.command == 1:
#             self.chassis.add_world_force(ecm, Vector3d(2000, 0, 0))
#         elif self.command == 0:
#             self.chassis.add_world_force(ecm, Vector3d(-2000, 0, 0))

#     def on_post_update(self, info, ecm):
#         """
#         on_post_update is used to read the current state of the world. We write the
#         state to a local field.
#         """
#         pole_pose = self.pole.world_pose(ecm).rot().euler().y()
#         if self.pole.world_angular_velocity(ecm) is not None:
#             pole_angular_vel = self.pole.world_angular_velocity(ecm).y()
#         else:
#             pole_angular_vel = 0
#             print("Warning failed to get angular velocity")
#         cart_pose = self.chassis.world_pose(ecm).pos().x()
#         cart_vel = self.chassis.world_linear_velocity(ecm)

#         if cart_vel is not None:
#             cart_vel = cart_vel.x()
#         else:
#             cart_vel = 0
#             print("Warning failed to get cart velocity")
#         # Write the state to the environment
#         self.state = np.array([cart_pose, cart_vel, pole_pose, pole_angular_vel], dtype=np.float32)
#         if not self.terminated:
#             self.terminated = pole_pose > 0.48 or pole_pose < -0.48 or cart_pose > 4.8 or cart_pose < -4.8

#         if self.terminated:
#             self.reward = 0.0
#         else:
#             self.reward = 1.0

#     def step(self, action, paused=False):
#         """
#         Execute the server.

#         There is a bit of nuance in this instance,
#         our environment has control over every 5 simulation steps.
#         We block the server till those 5 steps are completed.
#         """
#         self.command = action
#         self.server.run(True, 5, paused)
#         obs = self.state
#         reward = self.reward
#         return obs, reward, self.terminated, False, {}

#     def reset(self):
#         """
#         This function simply resets the server
#         """
#         self.server.reset_all()
#         self.command = None
#         self.terminated = False
#         obs, reward_, term_, tunc_, other_= self.step(None, paused=False)
#         return obs, {}



# class CustomCartPole(gym.Env):
#     """
#     Wrapper around GzRewardScorer that adapts the reward scorer to work with
#     gymnasium.
#     """
#     def __init__(self, env_config):
#         self.env = GzRewardScorer()
#         self.action_space = gym.spaces.Discrete(2)
#         self.observation_space = gym.spaces.Box(
#             np.array([-10, float("-inf"), -0.418, -3.4028235e+38]),
#             np.array([10, float("inf"), 0.418, 3.4028235e+38]),
#             (4,), np.float32)

#     def reset(self, seed=123):
#         return self.env.reset()

#     def step(self, action):
#         obs, reward, terminated, truncated, info = self.env.step(action)
#         return  obs, reward, terminated, truncated, info

# env = CustomCartPole({})
# model = lambda x: np.random.randint(0, 2, size=(1,))
# # model = PPO("MlpPolicy", env, verbose=1)
# # model.learn(total_timesteps=25_000)

# # vec_env = model.get_env()
# # obs = vec_env.reset()
# obs, _ = env.reset()

# # Spawn your GUI and see the model you inferred
# run_gui()
# time.sleep(10)
# for i in range(50000):
#     # action, _state = model.predict(obs, deterministic=True)
#     action = model(obs)
#     obs, reward, terminated, truncated, info = env.step(action)