# Knuckey Rover Navigation — My Engineering Contribution

**Project:** Knuckey Rover / EmuBot Mk1  
**Role:** Robotics engineer, simulation and integration work  
**Institution:** RMIT University  
**Recognition:** RMIT EnGenius 2026 — Manufacturing, Mechatronics and Materials Engineering Prize (top project in the discipline)

> This portfolio README describes work documented in project handover materials and reports. It is not a claim of sole authorship of the team's complete codebase, hardware or prize. Confirm individual file authorship using Git history before presenting any file as exclusively yours.

## Project objective

Develop and validate an autonomy stack for an agricultural rover intended to operate along existing field tramlines. The project combines a real ROS 2 rover architecture with simulation-based testing before deployment.

## My contribution — simulation and robotics integration

### 1. Gazebo and ROS 2 simulation
- Worked on the Gazebo-based rover simulation with a world, robot description, wheel and caster geometry, stereo camera frames and GPS frame.
- Established a ROS 2 launch and teleoperation workflow using `/cmd_vel`.
- Used simulated stereo camera topics to validate the perception pipeline before more complex Isaac Sim testing.

**Documented project assets to link:** `stereo_world.sdf`, `stereo_robot.sdf`, `stereo_robot.urdf.xacro`, `full_sim.launch.py`, `display_stereo.launch.py`.

### 2. NVIDIA Isaac Sim integration
- Worked on the rover's Isaac Sim representation and Python-driven velocity control.
- Documented a control integration issue: an Action Graph Articulation Controller approach did not reliably move the rover; direct Python wheel-target velocity control was used as the working simulation approach.
- Connected simulated rover motion to ROS 2 topics and a stereo camera processing workflow.

**Documented assets:** `knuckey_rover_basic.usd`, `stereo_robot_isaac.urdf.xacro`, `isaac_open_stage_play_drive.py`, `start_isaac_full_pipeline.sh`, `isaac_stereo_pipeline.launch.py`.

### 3. Sensor integration and state estimation
- Worked with simulated GPS, IMU and wheel odometry published to ROS 2 (`/fix`, `/imu/data`, `/odom`).
- Integrated a dual-EKF localization workflow using `robot_localization` to supply a filtered pose to Nav2.
- Investigated ROS 2 Jazzy configuration and simulation-time synchronization issues during integration.

### 4. Navigation validation
- Tested point-to-point and multi-waypoint navigation in simulation using Nav2.
- The project report documents **32 of 34 tramline waypoints reached with dual EKF enabled**, compared with **28 of 34 without EKF**, across a simulated approximately 2.65 km route.
- These are **simulation results**, not verified real-field performance. Remaining failures were documented as controller goal-tolerance/time-out issues.

### 5. Real-rover architecture and integration context
- Worked with the team architecture involving a Raspberry Pi 5 running ROS 2 Jazzy, a base-station/rover LoRa link, CAN motor control through ODrive, safety state logic and E-stop handling.
- The handover describes the safety and electrical system, but **do not attribute sole design of these subsystems to me** without commit history or other proof.

## Engineering challenges and decisions

| Challenge | Approach / documented result |
|---|---|
| Reliable Isaac rover movement | Used Python direct-drive control after Action Graph controller instability |
| Consistent pose estimates | GPS + IMU + wheel odometry via local/global EKF |
| Multi-waypoint navigation | Nav2 FollowWaypoints with tramline route validation |
| Stereo pipeline integration | Standardized stereo image topics and disparity processing |
| ROS 2 timing and launch setup | Adjusted EKF launch parameters and clock settings in the simulation workflow |

## Project evidence

- [Engineering portfolio](https://anakin-skywalker-1708.github.io/Engineering-Portfolio/)
- EnGenius 2026 prize certificate (include image in `media/award-certificate.jpg`)
- Rover exhibition and prototype photos (see `media/`)
- Team repository: `EmuRobotics/EmuBotMk1` (confirm permission and appropriate public link)

## Suggested public repository structure

```text
knuckey-rover-portfolio/
├── README.md
├── docs/
│   ├── architecture-overview.md
│   ├── simulation-workflow.md
│   ├── test-results.md
│   └── contribution-evidence.md
├── media/
│   ├── award-certificate.jpg
│   ├── rover-exhibition.jpg
│   ├── rover-hardware.jpg
│   └── team-photo.jpg
└── links.md
```

Do **not** copy proprietary/team code or full technical drawings into a personal public repository without permission. Prefer linking to the team's existing public repository and your own authorized contributions. The supplied ZIP contains photographs, **not** the ROS 2 source code or CAD models.

## Verification checklist before publication

- [ ] Match code claims to your commits/PRs in `EmuRobotics/EmuBotMk1`.
- [ ] Confirm whether the later `rover_bridge.py` and dual-EKF results belong to your own authored work or the team's combined work.
- [ ] Confirm public-sharing permission for photos of teammates and team source files.
- [ ] Distinguish demonstrated simulation functionality from hardware features still being developed.


## Detailed documentation

- [ROS node catalog](documentation/architecture/NODE_CATALOG.md)
- [ROS topic and action interfaces](documentation/architecture/TOPIC_INTERFACES.md)
- [Electrical and safety design](documentation/architecture/SAFETY_AND_POWER.md)
- [Gazebo, Isaac Sim and Nav2 workflow](documentation/navigation/SIMULATION_PIPELINE.md)
- [Simulation test results and limitations](documentation/testing/TESTING_AND_LIMITATIONS.md)
- [Original code source manifest](documentation/CODE_SOURCE_MANIFEST.md)
- [Original architecture specification](documentation/architecture/knuckey_rover_architecture.md)

**Note:** Original executable ROS node source files are not bundled here; see the source manifest and the team repository.
