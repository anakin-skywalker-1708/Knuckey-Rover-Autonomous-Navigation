# Simulation, perception and navigation workflow

## Gazebo Harmonic / ROS 2 Jazzy

Documented assets in the original team workspace include `stereo_world.sdf`, `stereo_robot.sdf`, `stereo_robot.urdf.xacro`, `full_sim.launch.py`, `display_stereo.launch.py`, `camera_info_pub.py`, `stereo_teleop_pointcloud.py`, `fake_gps_pub.py`, and `sim_gps_from_odom.py`.

Gazebo publishes stereo camera imagery, bridged into ROS 2. CameraInfo and relay topics feed `stereo_image_proc`, which generates `/disparity`; a custom node can produce `/stereo/points`. Differential-drive teleoperation uses `/cmd_vel`. The handover warns to spawn the Gazebo **SDF** rather than the older generated URDF containing Gazebo Classic plugins.

## Isaac Sim

Documented original assets include `knuckey_rover_basic.usd`, `stereo_robot_isaac.urdf.xacro`, `isaac_open_stage_play_drive.py`, `start_isaac_full_pipeline.sh`, and `isaac_stereo_pipeline.launch.py`. The project handover records that Action Graph Articulation Controller motion was unreliable; direct Python control of wheel joint velocity targets was the working approach. Camera relay, stereo disparity and simulated GPS were integrated.

## Localization and navigation

GPS, IMU and wheel odometry are used with `robot_localization` and dual-EKF state estimation, supplying pose estimates to Nav2 for simulated tramline waypoint navigation. Distinguish completed simulation tests from real-rover field validation.

**Source code:** These filenames are references to the team workspace, not recreated implementations. Obtain original source from the authorized `EmuRobotics/EmuBotMk1` repository or the rover workspace.
