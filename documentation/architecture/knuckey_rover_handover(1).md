
# Knuckey Rover / EmuBot ROS2 Stereo Simulation Handover

## 1. Project Context

This project is a ROS2 + Gazebo Harmonic simulation for a capstone autonomy-driven agricultural seeder/rover. The simulated rover currently includes:

- Differential-drive rover motion using `/cmd_vel`
- Two Gazebo stereo cameras modelled after Intel RealSense D415-style values
- ROS2 camera image topics
- Custom CameraInfo publisher
- Stereo disparity pipeline using `stereo_image_proc`
- Point cloud generation from disparity using a custom Python node
- GPS work-in-progress: simulated GPS publisher works; Gazebo NavSat approach is being tested but has caused Gazebo crashes

The goal is to build a reusable simulation stack that can later be migrated to Isaac Sim and integrated into the EmuBot GitHub repository.

---

## 2. Current Environment

Main environment used:

```bash
Ubuntu
ROS2 Jazzy
Gazebo Harmonic / gz sim 8.x
VS Code
Python ROS2 package using ament_python
```

Main workspace:

```bash
~/knuckey_rover_ws
```

Main package:

```bash
~/knuckey_rover_ws/src/knuckey_rover
```

EmuBot repository cloned separately at:

```bash
~/EmuBot
```

Every new terminal should usually source:

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash
```

For EmuBot repo work:

```bash
source /opt/ros/jazzy/setup.bash
source ~/EmuBot/install/setup.bash
```

---

## 3. Important Files in `knuckey_rover`

### 3.1 Gazebo files

```text
~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf
~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf
```

Use these for Gazebo simulation.

- `stereo_world.sdf`: world, ground plane, required Gazebo systems/plugins
- `stereo_robot.sdf`: rover body, wheels, casters, cameras, camera sensors, diff-drive plugin, optional GPS visual link

Important: spawn the SDF file, not the URDF:

```bash
file:=/home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf
```

### 3.2 ROS TF / RViz file

```text
~/knuckey_rover_ws/src/knuckey_rover/urdf/stereo_robot.urdf.xacro
```

Use this for:

- `robot_state_publisher`
- RViz TF tree
- RobotModel display

Do not use the old generated `stereo_robot.urdf` for Gazebo. It may still contain older Gazebo Classic camera plugin references such as:

```xml
libgazebo_ros_camera.so
```

That is not appropriate for Jazzy + Gazebo Harmonic.

### 3.3 Python nodes

Python package folder:

```text
~/knuckey_rover_ws/src/knuckey_rover/knuckey_rover/
```

Important Python files:

```text
camera_info_pub.py
stereo_teleop_pointcloud.py
fake_gps_pub.py
sim_gps_from_odom.py  # recommended if using odom-derived simulated GPS
```

### 3.4 Launch file

A full launch file was drafted at:

```text
~/knuckey_rover_ws/src/knuckey_rover/launch/full_sim.launch.py
```

Its goal is to start:

- Gazebo world
- Spawn rover
- Robot state publisher
- ROS-Gazebo camera bridge
- CameraInfo publisher
- GPS publisher
- topic relays
- disparity node

---

## 4. What Currently Works

The following stack was working before the NavSat/GPS changes:

```text
Gazebo rover model spawns
Gazebo cameras publish /camera_left and /camera_right
ROS-Gazebo bridge brings images into ROS2
custom camera_info_pub publishes CameraInfo topics
relays convert topics to stereo_image_proc expected names
stereo_image_proc publishes /disparity
custom node can publish /stereo/points
teleop can drive rover via /cmd_vel
fake GPS publisher can publish /gps/fix
```

Core working topics included:

```text
/camera_left
/camera_right
/camera_left/camera_info
/camera_right/camera_info
/left/image_rect
/right/image_rect
/left/camera_info
/right/camera_info
/disparity
/stereo/points
/cmd_vel
/gps/fix
```

---

## 5. Full Manual Startup Sequence for Working Stereo Pipeline

Open separate terminals for long-running commands.

### Terminal 1: start Gazebo world

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash

ros2 launch ros_gz_sim gz_sim.launch.py \
  gz_args:="/home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf"
```

Press Play in Gazebo.

### Terminal 2: spawn rover

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash

ros2 launch ros_gz_sim gz_spawn_model.launch.py \
  world:=stereo_world \
  file:=/home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf \
  entity_name:=knuckey_rover \
  x:=0.0 y:=0.0 z:=0.08
```

Check:

```bash
gz model --list
```

Expected:

```text
ground_plane
knuckey_rover
```

### Terminal 3: bridge camera images and cmd_vel

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/camera_left@sensor_msgs/msg/Image@gz.msgs.Image \
/camera_right@sensor_msgs/msg/Image@gz.msgs.Image \
/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

Check:

```bash
ros2 topic hz /camera_left
ros2 topic hz /camera_right
```

### Terminal 4: publish CameraInfo

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash

ros2 run knuckey_rover camera_info_pub
```

Check:

```bash
ros2 topic hz /camera_left/camera_info
ros2 topic hz /camera_right/camera_info
```

### Terminals 5–8: relays for stereo_image_proc

The installed Jazzy `disparity_node` expected these topic names:

```text
/left/image_rect
/right/image_rect
/left/camera_info
/right/camera_info
```

Relay the actual topics:

```bash
ros2 run topic_tools relay /camera_left /left/image_rect
```

```bash
ros2 run topic_tools relay /camera_right /right/image_rect
```

```bash
ros2 run topic_tools relay /camera_left/camera_info /left/camera_info
```

```bash
ros2 run topic_tools relay /camera_right/camera_info /right/camera_info
```

If needed:

```bash
sudo apt install ros-jazzy-topic-tools
```

### Terminal 9: run disparity

```bash
source /opt/ros/jazzy/setup.bash
source ~/knuckey_rover_ws/install/setup.bash

ros2 run stereo_image_proc disparity_node --ros-args \
  -p approximate_sync:=true \
  -p queue_size:=50
```

Check:

```bash
ros2 topic hz /disparity
```

### View disparity

```bash
ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/disparity
```

---

## 6. Point Cloud Node

The custom Python node `stereo_teleop_pointcloud.py` does two things:

1. Keyboard teleop by publishing `/cmd_vel`
2. Converts `/disparity` to a point cloud published on:

```text
/stereo/points
```

Run after cameras, CameraInfo, relays, and disparity are working:

```bash
ros2 run knuckey_rover stereo_teleop_pointcloud
```

Check:

```bash
ros2 topic hz /stereo/points
```

View in RViz:

```bash
rviz2
```

Add:

```text
PointCloud2
```

Topic:

```text
/stereo/points
```

Set Fixed Frame appropriately, usually:

```text
base_link
```

If TF is missing, run robot_state_publisher:

```bash
xacro ~/knuckey_rover_ws/src/knuckey_rover/urdf/stereo_robot.urdf.xacro > /tmp/stereo_robot.urdf
ros2 run robot_state_publisher robot_state_publisher /tmp/stereo_robot.urdf
```

---

## 7. CameraInfo Publisher Details

The working version of `camera_info_pub.py` should publish CameraInfo messages synchronized to image timestamps, not arbitrary timer timestamps. This matters because `stereo_image_proc` needs image and camera info timestamps to match closely.

Core behaviour:

```text
Subscribe: /camera_left, /camera_right
Publish:   /camera_left/camera_info, /camera_right/camera_info
```

D415-like values used:

```text
width = 1280
height = 720
horizontal FOV = 65 degrees
baseline = 0.055 m
```

Right camera projection matrix must include baseline:

```text
Tx = -fx * baseline
```

Frame IDs must match incoming image frame IDs. Previously observed image frame IDs were:

```text
knuckey_rover/left_camera_link/camera_left
knuckey_rover/right_camera_link/camera_right
```

The corrected CameraInfo node copied the image message timestamp and frame ID from each image.

---

## 8. GPS Status and Options

### 8.1 Current working GPS option

The working safe GPS method was a ROS2 Python publisher:

```text
fake_gps_pub.py
```

It publishes:

```text
/gps/fix : sensor_msgs/msg/NavSatFix
```

But this is not tied to rover motion. It gives simulated static/noisy GPS values around Melbourne.

Command:

```bash
ros2 run knuckey_rover fake_gps_pub
```

Check:

```bash
ros2 topic echo /gps/fix --once
ros2 topic hz /gps/fix
```

### 8.2 Better GPS option if NavSat is unstable

The better simulation-friendly GPS method is:

```text
/odom → sim_gps_from_odom.py → /gps/fix
```

This makes GPS values follow rover motion without using Gazebo’s NavSat sensor.

Steps:

1. Bridge `/odom` if available:

```bash
gz topic -l | grep odom
ros2 run ros_gz_bridge parameter_bridge /odom@nav_msgs/msg/Odometry@gz.msgs.Odometry
```

2. Run:

```bash
ros2 run knuckey_rover sim_gps_from_odom
```

Then:

```bash
ros2 topic echo /gps/fix
```

### 8.3 NavSat approach currently being tested

The user wanted to try Gazebo NavSat to bypass odom conversion:

```text
Gazebo NavSat sensor → /gps/fix
```

This is cleaner if it works.

Required additions:

In `stereo_world.sdf`, inside `<world name="stereo_world">`:

```xml
<plugin
  filename="gz-sim-navsat-system"
  name="gz::sim::systems::NavSat">
</plugin>

<spherical_coordinates>
  <surface_model>EARTH_WGS84</surface_model>
  <latitude_deg>-37.8136</latitude_deg>
  <longitude_deg>144.9631</longitude_deg>
  <elevation>30.0</elevation>
  <heading_deg>0</heading_deg>
</spherical_coordinates>
```

In `stereo_robot.sdf`, inside `gps_link`:

```xml
<sensor name="gps_sensor" type="navsat">
  <always_on>true</always_on>
  <update_rate>10</update_rate>
  <topic>/gps/fix</topic>
</sensor>
```

Bridge:

```bash
ros2 run ros_gz_bridge parameter_bridge \
/gps/fix@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat
```

### 8.4 NavSat crash issue

Gazebo previously crashed after adding NavSat. The crash log showed a segmentation fault inside the Gazebo sensors render thread:

```text
libgz-sim-sensors-system.so
RenderThread()
Ogre2Scene::SetBackgroundColor(...)
Segmentation fault
```

A discovered issue was that `stereo_world.sdf` had the `gz-sim-sensors-system` plugin duplicated twice. That must be fixed:

Keep only one:

```xml
<plugin
  filename="gz-sim-sensors-system"
  name="gz::sim::systems::Sensors">
</plugin>
```

Do not duplicate it.

Also avoid running multiple `/gps/fix` publishers at once:

```bash
pkill -f fake_gps_pub
pkill -f sim_gps_from_odom
```

Check publisher count:

```bash
ros2 topic info /gps/fix
```

Expected:

```text
Publisher count: 1
```

---

## 9. Troubleshooting Known Issues

### 9.1 Gazebo camera topics do not appear

Make sure `stereo_world.sdf` includes exactly one sensors plugin:

```xml
<plugin
  filename="gz-sim-sensors-system"
  name="gz::sim::systems::Sensors">
</plugin>
```

Gazebo must be playing. Cameras do not publish while paused.

Check:

```bash
gz topic -l | grep camera
ros2 topic hz /camera_left
```

### 9.2 RViz says no image

Common causes:

- Gazebo paused
- image bridge not running
- topic not selected in RViz image display
- RViz fixed frame not available

Use:

```bash
LIBGL_ALWAYS_SOFTWARE=1 rviz2
```

if RViz crashes with OpenGL.

### 9.3 Disparity exists but does not publish

Check all four input rates:

```bash
ros2 topic hz /left/image_rect
ros2 topic hz /right/image_rect
ros2 topic hz /left/camera_info
ros2 topic hz /right/camera_info
```

If missing, relays are not running.

Check node subscriptions:

```bash
ros2 node info /disparity_node
```

Working topic layout for the installed node:

```text
/left/image_rect
/right/image_rect
/left/camera_info
/right/camera_info
```

### 9.4 CameraInfo publisher count is 1 but no messages

Replace `camera_info_pub.py` with the clean version that subscribes to image topics and publishes info in callbacks. The timer-based version caused timestamp problems or stopped publishing after edits.

### 9.5 Gazebo instantly shuts down after NavSat

First restore working backups:

```bash
cp ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot_backup_before_navsat.sdf \
   ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf

cp ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world_backup_before_navsat.sdf \
   ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf
```

Then retest stereo. If stable, retry NavSat carefully or use `sim_gps_from_odom`.

### 9.6 Capture Gazebo crash logs

Run Gazebo verbose and save output:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py \
  gz_args:="-v 4 /home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf" \
  2>&1 | tee ~/gazebo_debug.log
```

Then inspect:

```bash
cat ~/gazebo_debug.log | tail -80
```

### 9.7 Validate SDF files

```bash
gz sdf -k ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf
gz sdf -k ~/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf
```

Note: `Valid` only means the SDF syntax is valid; Gazebo may still crash from plugin/runtime issues.

---

## 10. GitHub / EmuBot Integration Status

The user cloned the EmuBot repository into Ubuntu:

```bash
cd ~
git clone https://github.com/alexguymcintosh/EmuBot.git
cd EmuBot
```

A new package was created inside:

```bash
cd ~/EmuBot/src
ros2 pkg create --build-type ament_python emubot_perception
```

Copied over:

```text
camera_info_pub.py
stereo_teleop_pointcloud.py
```

To integrate fully, also copy:

```text
fake_gps_pub.py
sim_gps_from_odom.py
```

or port them to `emubot_perception` if needed.

`setup.py` entry points in EmuBot should include:

```python
entry_points={
    'console_scripts': [
        'camera_info_pub = emubot_perception.camera_info_pub:main',
        'stereo_teleop_pointcloud = emubot_perception.stereo_teleop_pointcloud:main',
    ],
},
```

For Git:

```bash
git config --global user.name "Manas Desai"
git config --global user.email "s3964030@student.rmit.edu.au"
```

GitHub push requires token/GitHub CLI, not normal password:

```bash
sudo apt install gh
gh auth login
```

---

## 11. Isaac Sim Migration Plan

The key idea is not to move all ROS code. Keep the ROS pipeline and replace Gazebo with Isaac as the simulator.

Current Gazebo pipeline:

```text
Gazebo → /camera_left, /camera_right → CameraInfo → stereo_image_proc → /disparity → /stereo/points
```

Isaac pipeline should become:

```text
Isaac Sim → /camera_left, /camera_right → CameraInfo → stereo_image_proc → /disparity → /stereo/points
```

Steps:

1. Install/open Isaac Sim with ROS2 Jazzy environment sourced.
2. Enable Isaac ROS2 Bridge extension.
3. Create a simple scene with one camera first.
4. Publish `/camera_left` and `/camera_left/camera_info`.
5. Add right camera with D415-like baseline:

```text
left y = +0.0275
right y = -0.0275
baseline = 0.055 m
resolution = 1280x720
FOV ≈ 65 degrees
```

6. Publish:

```text
/camera_left
/camera_right
/camera_left/camera_info
/camera_right/camera_info
```

7. Reuse existing relays and `stereo_image_proc`.
8. Later add `/cmd_vel` control and GPS.

---

## 12. Recommended Next Steps

### Immediate next step

Stabilize NavSat decision:

Option A: Keep testing Gazebo NavSat after fixing duplicate sensors plugin.

Option B: Use the robust approach:

```text
/odom → sim_gps_from_odom → /gps/fix
```

This gives GPS values tied to rover motion and avoids Gazebo crashes.

### After GPS is stable

1. Update `full_sim.launch.py` to include the chosen GPS method.
2. Save an RViz config under:

```text
config/stereo_rover.rviz
```

3. Add obstacle detection from `/stereo/points`:

```text
filter front region
ignore ground
if object distance < threshold → stop / warn
```

4. Push cleaned project into EmuBot branch:

```bash
git checkout -b feature/stereo-perception
```

5. Add README, screenshots, demo video, and docs.

---

## 13. Most Important Warnings for the Next Chat

1. Do not spawn `stereo_robot.urdf` in Gazebo. Use `stereo_robot.sdf`.
2. Use `stereo_robot.urdf.xacro` only for TF/RViz.
3. Keep only one `gz-sim-sensors-system` plugin in `stereo_world.sdf`.
4. Do not run fake GPS and NavSat GPS at the same time.
5. If NavSat crashes Gazebo, use `sim_gps_from_odom` instead.
6. `stereo_image_proc` needed relays because the node expected `/left/...` and `/right/...` topic names.
7. Gazebo camera sensors publish only when Gazebo is playing.
8. If RViz crashes, use:

```bash
LIBGL_ALWAYS_SOFTWARE=1 rviz2
```

9. Before rebuilding, save files and then run:

```bash
cd ~/knuckey_rover_ws
rm -rf build install log
colcon build
source install/setup.bash
```

10. If a new executable does not show in `ros2 pkg executables knuckey_rover`, check `setup.py`, save it, and rebuild clean.

---

## 14. Key Commands Quick Reference

Start world:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py \
  gz_args:="/home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_world.sdf"
```

Spawn rover:

```bash
ros2 launch ros_gz_sim gz_spawn_model.launch.py \
  world:=stereo_world \
  file:=/home/manas-desai/knuckey_rover_ws/src/knuckey_rover/worlds/stereo_robot.sdf \
  entity_name:=knuckey_rover \
  x:=0.0 y:=0.0 z:=0.08
```

Bridge images and cmd_vel:

```bash
ros2 run ros_gz_bridge parameter_bridge \
/camera_left@sensor_msgs/msg/Image@gz.msgs.Image \
/camera_right@sensor_msgs/msg/Image@gz.msgs.Image \
/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

CameraInfo:

```bash
ros2 run knuckey_rover camera_info_pub
```

Relays:

```bash
ros2 run topic_tools relay /camera_left /left/image_rect
ros2 run topic_tools relay /camera_right /right/image_rect
ros2 run topic_tools relay /camera_left/camera_info /left/camera_info
ros2 run topic_tools relay /camera_right/camera_info /right/camera_info
```

Disparity:

```bash
ros2 run stereo_image_proc disparity_node --ros-args \
  -p approximate_sync:=true \
  -p queue_size:=50
```

Point cloud / teleop custom node:

```bash
ros2 run knuckey_rover stereo_teleop_pointcloud
```

Fake GPS:

```bash
ros2 run knuckey_rover fake_gps_pub
```

Check GPS:

```bash
ros2 topic echo /gps/fix --once
ros2 topic hz /gps/fix
```

Check disparity:

```bash
ros2 topic hz /disparity
```

Check point cloud:

```bash
ros2 topic hz /stereo/points
```

Clean kill:

```bash
pkill -f gz
pkill -f ros_gz
pkill -f parameter_bridge
pkill -f camera_info_pub
pkill -f disparity_node
pkill -f topic_tools
pkill -f fake_gps_pub
pkill -f sim_gps_from_odom
```
