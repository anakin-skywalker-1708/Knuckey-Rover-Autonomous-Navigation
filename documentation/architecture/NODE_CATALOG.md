# ROS node catalog — documented architecture

**Status:** Architecture specification, not a verified inventory of running code. The original team source files have not been copied into this portfolio package.

| Location | Node | Responsibility | Interfaces |
|---|---|---|---|
| Base | Master/Mission | GPS mission input, mode, arming, E-stop authority | `/armed`, `/command_mode`, `/e-stop`, `/clear_estop`, `/path_plan`, `/status` |
| Base | `teleop_twist` | Manual velocity at 10 Hz | `/cmd_vel_tele` |
| Base | LoRa | Commands downlink 10 Hz; status uplink 2 Hz | Radio bridge |
| Rover | LoRa | Decode base commands and transmit status | Command topics; `/status` |
| Rover | `mission_node` | Waypoint stack, action client, status at 2 Hz | `/path_plan`, `nav_goal`, `/status` |
| Rover | `nav_blackbox` | Navigation action server, wheel velocities | `nav_goal`, `/cmd_vel_nav` |
| Rover | `selection` | Manual/autonomous command selection and E-stop braking | `/cmd_vel_tele`, `/cmd_vel_nav`, `/active_mode`, `/cmd_vel` |
| Rover | `state_machine` | Pre-charge, contactor control, lockout and modes | `/armed`, `/e-stop`, `/clear_estop`, `/bus_voltage`, `/main_battery_voltage` |
| Rover | `ros_odrive` | Velocity to CAN; ODrive/BMS readings | `/cmd_vel`, `/bus_voltage`, `/main_battery_voltage` |

See `knuckey_rover_architecture.md` for the full design and safety requirements. Message types for custom topics and the action schema require verification against the actual source repository.
