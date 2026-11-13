# Knuckey Rover - Master Handover Document

Generated: 17 August 2026

## Purpose
This file is a compact handover for another chat/team member. It consolidates the real rover architecture, simulation work, GitHub status, electrical testing direction, and Nav2 next steps.

## Current Snapshot
- Real rover architecture: Base Station + Rover over LoRa.
- Downlink: 10 Hz Base -> Rover command stream.
- Uplink: 2 Hz Rover -> Base telemetry stream.
- Electrical: always-on Batrium BMS, Contactor 1 for logic rails, Contactor 2 for ODrive traction bus, pre-charge circuit, flyback diodes, optoisolation and strict return rules.
- ROS rover nodes: LoRa, mission_node, nav_blackbox, selection, state_machine, ros_odrive.
- Simulation: Gazebo assets and Isaac scene/scripts committed to EmuRobotics/EmuBotMk1.
- Isaac motion: direct Python script subscribes to /cmd_vel and sets wheel joint target velocities.
- Stereo: Isaac camera topics -> relay -> stereo_image_proc -> /disparity.
- GPS: Isaac script publishes /gps/fix from rover pose.
- GitHub: PR created from feature/stereo-perception-clean into main.

## Real Rover Infrastructure
The system consists of a Base Station and a Rover communicating over LoRa. The Base Station manages maps, modes, E-stop, clear-estop authority, teleoperation commands, and path plans. The Rover executes commands, runs ROS logic, controls motors over CAN, reports telemetry, and manages power state.

### Mechanical
- 40 x 40 mm aluminium T-slot chassis.
- 10.2 inch drive wheel diameter (~259.1 mm).

### Electrical
- Architecture file states two 6S 1600 mAh 15C lithium packs in series. Earlier chat mentioned 16 Ah packs; verify physically before calculations.
- 100 A fuses on battery positive terminals.
- Physical isolator on main positive line.
- Always-on 12 V DC-DC powers Batrium Watchmon.
- Batrium K9 cell monitors, one per battery.
- Contactor 1 powers logic layer after Batrium OK + physical NC E-stop.
- Contactor 2 powers ODrive traction bus after Pi relay + LoRa heartbeat relay + NC latching button and pre-charge.
- Pre-charge uses SSR and chassis mount resistor.
- Flyback diodes protect contactor coils.
- Signal lines crossing domains require optoisolation/galvanic isolation.

## ROS Architecture
Base Station:
- Master/Mission Node: publishes /armed, /command_mode, /e-stop, /clear_estop, /path_plan.
- teleop_twist: publishes /cmd_vel_tele at 10 Hz.
- Base LoRa Node: downlink at 10 Hz, receives /status at 2 Hz.

Rover:
- LoRa Node: radio interface.
- mission_node: waypoint stack, Action Client to nav_blackbox, publishes /status.
- nav_blackbox: Action Server; outputs /cmd_vel_nav.
- selection: multiplexes /cmd_vel_nav and /cmd_vel_tele, manages E-stop CAN braking.
- state_machine: pre-charge, contactor control, lockout, mode routing.
- ros_odrive: converts /cmd_vel to CAN, publishes /bus_voltage and /main_battery_voltage.

## Simulation
Gazebo files include stereo_world.sdf, stereo_robot.sdf, URDF/Xacro, full_sim.launch.py, and display_stereo.launch.py.

Isaac files include knuckey_rover_basic.usd, stereo_robot_isaac.urdf.xacro, isaac_open_stage_play_drive.py, start_isaac_full_pipeline.sh, and isaac_stereo_pipeline.launch.py.

Important Isaac decision: Action Graph Articulation Controller movement was unreliable. The working method is the Isaac Python direct-drive script.

## GitHub
Repository: EmuRobotics/EmuBotMk1
Branch: feature/stereo-perception-clean
PR base: main

## Next Steps
1. Verify real battery capacity.
2. Run electrical commissioning checklist.
3. Validate BMS, contactors, pre-charge, fuses, and isolation.
4. Confirm ODrive CAN IDs and current limits.
5. Add /odom and /imu/data for EKF.
6. Build robot_localization EKF pipeline.
7. Implement tramline waypoint following through mission_node/nav_blackbox/Nav2.

## Prompt for Next Chat
Use this handover and knuckey_rover_architecture.md. Distinguish confirmed architecture from previous-chat context. Do not assume battery capacity until physically verified. Continue with electrical testing, real rover infrastructure, Nav2 tramline automation, Gazebo/Isaac simulation, and GitHub workflow as needed.
