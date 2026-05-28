from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp({
    "headless": False,
    "renderer": "RayTracedLighting"
})

import os
import yaml
from omni.isaac.core import World
from omni.isaac.sensor import LidarRtx
from omni.isaac.urdf import URDFImporter
from pxr import Gf

# -----------------------------------------------------------------------------
# Paths (adjust or parametrize)
# -----------------------------------------------------------------------------
PKG_ROOT = os.environ["BOXBOT_DESCRIPTION_PATH"]
URDF_PATH = os.path.join(PKG_ROOT, "urdf", "robot.urdf")
SENSOR_CONFIG = os.path.join(PKG_ROOT, "config", "isaac_sensors.yaml")

ROBOT_PRIM_PATH = "/World/BoxBot"

# -----------------------------------------------------------------------------
# Create world
# -----------------------------------------------------------------------------
world = World(stage_units_in_meters=1.0)
stage = world.stage

# -----------------------------------------------------------------------------
# Import URDF
# -----------------------------------------------------------------------------
importer = URDFImporter()
importer.import_robot(
    urdf_path=URDF_PATH,
    prim_path=ROBOT_PRIM_PATH,
    merge_fixed_joints=True,
    import_inertia=True,
    create_physics_scene=True
)

# -----------------------------------------------------------------------------
# Load sensor registry
# -----------------------------------------------------------------------------
with open(SENSOR_CONFIG, "r") as f:
    sensors = yaml.safe_load(f)

# -----------------------------------------------------------------------------
# Attach sensors
# -----------------------------------------------------------------------------
for name, cfg in sensors.items():

    if cfg["type"] == "rtx_lidar":
        parent = f"{ROBOT_PRIM_PATH}/{cfg['parent_link']}"

        LidarRtx(
            prim_path=f"{parent}/{name}",
            parent=parent,
            translation=Gf.Vec3d(0, 0, 0),
            min_range=cfg["min_range"],
            max_range=cfg["max_range"],
            horizontal_fov=cfg["horizontal_fov"],
            horizontal_resolution=cfg["horizontal_resolution"],
            rotation_rate=cfg["update_rate"]
        )

# -----------------------------------------------------------------------------
# Reset & run
# -----------------------------------------------------------------------------
world.reset()

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()
