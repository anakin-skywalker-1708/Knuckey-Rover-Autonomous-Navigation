# ROS topics and action interfaces

Extracted from the project's architecture specification. These are **topic/interface names**, not verified ROS message definitions.

| Interface | Source | Destination | Purpose |
|---|---|---|---|
| `/e-stop` | Rover LoRa | Mission, State Machine, Selection | Fail-safe: 0 stop, 1 go |
| `/clear_estop` | Rover LoRa (base-authorized) | Selection, State Machine | Explicit recovery authorization |
| `/command_mode` | Rover LoRa | State Machine | Manual or autonomous request |
| `/armed` | Rover LoRa | State Machine | New rising-edge arm request |
| `/path_plan` | Rover LoRa | Mission | GPS waypoint stack, replaces previous |
| `/cmd_vel_tele` | Rover LoRa | Selection | Teleoperation at 10 Hz |
| `/cmd_vel_nav` | Nav Blackbox | Selection | Autonomous velocity |
| `/cmd_vel` | Selection | ros_odrive | Selected motor velocity |
| `/active_mode` | State Machine | Selection | Verified operating mode |
| `/bus_voltage` | ros_odrive | State Machine, Mission | ODrive traction bus voltage |
| `/main_battery_voltage` | ros_odrive | State Machine, Mission | Batrium BMS voltage |
| `/status` | Mission | LoRa | Telemetry at 2 Hz |
| `nav_goal` | Mission action client | Nav Blackbox action server | Goal, feedback, completion |

Do not assume message types, QoS, topic remaps or namespaced forms until verified in code.
