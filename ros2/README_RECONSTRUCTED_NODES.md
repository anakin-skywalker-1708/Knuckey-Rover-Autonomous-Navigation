# Reconstructed ROS 2 nodes — simulation only

These are **newly recreated example implementations** based on archived Knuckey Rover architecture notes and prior chat descriptions. **They are not the original node files**, have not been tested on a ROS 2 installation, and must not be described as the code deployed on the real rover.

## Included executable ROS 2 Python entry points

| Node | Role | Implementation boundary |
|---|---|---|
| `state_machine` | Simulated arm/precharge/lockout logic | No GPIO, SSR or contactor control |
| `selection` | Selects fresh teleop or navigation Twist by mode | Zero command on stale data |
| `cmdvel_to_can` | Converts Twist to differential wheel speeds | Publishes JSON CAN **intent** only; no CAN frames |
| `lora_bridge` | Decodes command JSON, monitors link timeout | ROS simulated radio topics only |
| `lora_rx` | Simulated radio ingress | No serial/SPI radio |
| `lora_base` | Simulated base radio relay | No physical RF |
| `master` | Base command JSON generator | No Excel reader or physical controls |
| `mission_node` | Stores path and publishes status | No Nav2 action client |
| `nav_blackbox` | Forwards simulated Nav2 Twist | Not a navigation planner |

**Critical:** Actual motor mapping, ODrive CAN IDs/payloads, wheel radius, track width, voltage calibration, GPIO wiring, radio packet schema, safety circuits and real-time watchdogs were unavailable or unverified. Defaults are illustrative and not validated. No real actuator or power-control functionality is included. The architecture describes a separate hardware LoRa watchdog and E-stop, which cannot be replaced by these software examples.

## ROS 2 Jazzy setup (Ubuntu, ROS installed)

```bash
cd ros2
colcon build --packages-select rover_control
source install/setup.bash
ros2 run rover_control state_machine
```

Run each node in a separate terminal for simulation. For radio mock testing, manually bridge `/radio_out_sim` to `/radio_in_sim` or create a separate simulator; the two are **not automatically connected**. To prevent unintended arming, `state_machine` starts E-stop latched and disarmed. `master` starts E-stop/go false and arm false.

The recreated nodes use `std_msgs` and `geometry_msgs` as simple interfaces, **not** a claim that these were the original custom ROS interfaces. See `documentation/architecture/knuckey_rover_architecture.md` for the documented system design.
