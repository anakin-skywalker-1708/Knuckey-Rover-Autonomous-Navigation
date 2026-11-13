# Original code and node source manifest

The following files are **referenced in project handovers** but **their executable source bytes were not available in the materials accessible for this packaging step**. They have not been fabricated.

## Gazebo / ROS
- `worlds/stereo_world.sdf`
- `worlds/stereo_robot.sdf`
- `urdf/stereo_robot.urdf.xacro`
- `launch/full_sim.launch.py`
- `launch/display_stereo.launch.py`
- `knuckey_rover/camera_info_pub.py`
- `knuckey_rover/stereo_teleop_pointcloud.py`
- `knuckey_rover/fake_gps_pub.py`
- `knuckey_rover/sim_gps_from_odom.py`

## Isaac Sim
- `knuckey_rover_basic.usd`
- `stereo_robot_isaac.urdf.xacro`
- `isaac_open_stage_play_drive.py`
- `start_isaac_full_pipeline.sh`
- `isaac_stereo_pipeline.launch.py`

## Real rover architecture nodes
- Base master/mission and LoRa nodes
- Rover LoRa, `mission_node`, `nav_blackbox`, `selection`, `state_machine`, `ros_odrive`

Actual filenames/locations for the real-rover nodes, and their implementation status, must be verified in Git history. Original team repository: https://github.com/EmuRobotics/EmuBotMk1 (historical branch: `feature/stereo-perception-clean`). Add files only where publication is authorized, with original attribution and licensing retained.

## Recreated code added (2026-11-13)
The files under `ros2/src/rover_control/` are **new reconstructions**. They are not recovered originals and are not hardware-ready. See `ros2/README_RECONSTRUCTED_NODES.md`.
