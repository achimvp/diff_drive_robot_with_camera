from launch import LaunchDescription
from launch.actions import ExecuteProcess
import os

def generate_launch_description():

    return LaunchDescription([
        ExecuteProcess(
            cmd=[
                "bash", "-c",
                f"export BOXBOT_DESCRIPTION_PATH={os.getcwd()} && "
                "isaac-sim python isaac/launch_sim.py"
            ],
            output="screen"
        )
    ])
