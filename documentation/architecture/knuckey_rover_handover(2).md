# Knuckey Rover Handover File

## Purpose of this file
This handover file gives another assistant, teammate, or supervisor the exact current infrastructure of the Knuckey Rover project based on the provided `knuckey_rover_architecture.md` system architecture document. Use it as the primary context for future questions about rover wiring, ROS nodes, safety logic, power sequencing, LoRa communications, CAN motor control, and mission behaviour.

---

## 1. High-Level System Infrastructure

The Knuckey Rover system is split into two major physical/software units:

1. **Base Station**
2. **Rover Unit**

The two communicate using a **LoRa network**.

### Communication rates
- **Downlink: Base Station to Rover** — command stream at **10 Hz**.
- **Uplink: Rover to Base Station** — telemetry stream at **2 Hz**.

### Base Station role
The base station is the top-level controller. It receives pre-defined field maps or GPS coordinates, plans the route, sends the desired command mode, sends manual teleoperation commands, triggers E-stop, and is the only authority allowed to issue `/clear_estop`.

### Rover role
The rover is a ROS-based autonomous vehicle. It receives commands from the base station, executes navigation logic, reports telemetry/status, handles CAN-level motor control, manages hardware power sequencing, and executes emergency braking and safety shutdowns.

---

## 2. Physical and Mechanical Infrastructure

### Chassis
- **Frame:** 40 × 40 mm aluminium T-slot extrusion.
- **Purpose:** Modular and rigid mounting structure for enclosures, batteries, electronics, contactors, motor drives, sensors, and wiring.

### Wheels
- **Drive wheel diameter:** 10.2 inches, approximately 259.1 mm.
- **Use:** Wheel diameter is used in odometry, velocity calculations, and motor driver configuration.

---

## 3. Electrical Infrastructure

## 3.1 Battery System

The rover uses two lithium battery packs wired in series.

### Battery configuration from source document
- **Battery 1:** 6S 1600 mAh 15C lithium battery.
- **Battery 2:** 6S 1600 mAh 15C lithium battery.
- **Connection:** Series connection to form a 12S equivalent pack.

### Important note
The architecture document specifies **1600 mAh**, not 16 Ah. This should be verified against the actual physical batteries because previous diagrams/conversations may have referred to larger 16 Ah packs. The handover should use the architecture document as source of truth unless the physical batteries prove otherwise.

### Battery protection
- Each battery positive terminal has a dedicated **100 A fuse**.
- The main wiring bus has:
  - one main positive terminal,
  - one main negative terminal,
  - a series jumper connecting battery 1 positive to battery 2 negative.
- A high-current physical isolator switch is placed on the main positive line.
- The isolator must only be switched off when the rover is fully stopped and motors are disabled.

---

## 3.2 BMS and Always-On Safety Circuit

The BMS safety layer remains powered independently of the main rover contactor state.

### Components
- Two **Batrium K9 cell monitors** — one per battery.
- One central **Batrium Watchmon BMS**.
- One independent **12 V DC-DC converter** powering the Batrium Watchmon directly from the battery side.

### Always-on behaviour
The Batrium Watchmon is powered before/bypassing the contactors, so it remains active even when the rest of the rover is off.

### Safety relay loop
A 12 V control loop runs through:
1. Batrium Expansion Board relay.
2. Physical normally closed E-stop switch.
3. Contactor 1 coil circuit.

### Contactor 1 enable condition
Contactor 1 energises only when:
- the physical E-stop is closed/unpressed, and
- Batrium reports no battery fault and actively pulls its relay closed.

### Fault behaviour
If Batrium detects a cell over-voltage, under-voltage, over-temperature, or another battery fault, it opens the relay. This trips Contactor 1 and shuts down the entire rover except for the always-on Batrium monitoring layer.

---

## 3.3 Dual Contactor Power Architecture

The rover uses a two-stage contactor design.

### Contactors
1. **Contactor 1 — Logic Layer Power**
2. **Contactor 2 — High-Voltage Motor Traction Bus**

### Main power path
```text
Main Battery Positive
    │
 [100 A Fuse]
    │
 [Physical Isolator]
    │
    ├──> [12 V DC-DC] ─────────> Batrium Watchmon (Always ON)
    │
 [Contactor 1] ── Coil controlled by Batrium OK + physical NC E-stop
    │
    ├──> [5 V DC-DC]  (2.5 A Fuse) ──> Logic Layer: Raspberry Pi 5, sensors
    ├──> [12 V DC-DC] (2.5 A Fuse) ──> Auxiliary systems and relays
    ├──> [24 V DC-DC] (2.5 A Fuse) ──> High-voltage logic/interfaces
    │
 [Contactor 2] ── Coil controlled by Pi relay + LoRa heartbeat relay + latching button
    ├──> [Pre-charge circuit: SSR + chassis-mount resistor]
    │
    └──> [High-voltage traction bus] ──> ODrive motor drivers
```

---

## 3.4 Contactor 1 — Logic Layer Power

### Function
Contactor 1 connects main battery positive to the low-voltage logic layer.

### Loads powered downstream of Contactor 1
- 5 V DC-DC converter.
- 12 V DC-DC converter.
- 24 V DC-DC converter.

Each converter is individually fused with a 2.5 A fuse according to the architecture document.

### Purpose
Contactor 1 allows the rover’s computing, sensors, relays, and low-voltage systems to power up while keeping the high-voltage motor traction bus separately controlled by Contactor 2.

---

## 3.5 Contactor 2 — Motor Traction Bus

### Function
Contactor 2 connects the main battery positive to the high-voltage motor bus feeding the ODrive motor drivers.

### Coil control loop
Contactor 2 energises only when all these interlocks are satisfied:
- Raspberry Pi 5 GPIO relay closed.
- LoRa heartbeat relay closed.
- Physical normally closed latching button closed.

### Activation rule
Both the Pi and the LoRa heartbeat must actively hold their relays closed for Contactor 2 to energise. This means the motor bus requires both onboard software permission and an external LoRa heartbeat safety signal.

### Pre-charge circuit
A bypass line across Contactor 2 contains:
- solid state relay,
- chassis-mount resistor.

This pre-charge path safely charges the ODrive/driver capacitors before the main contactor closes.

---

## 3.6 Coil EMF Protection

Both Contactor 1 and Contactor 2 have flyback diodes across their coils. These protect electronics from back-EMF voltage spikes when the coils are de-energised.

---

## 3.7 Signal Isolation and Grounding Rules

### Optoisolation
Signals from the Raspberry Pi 5 and LoRa heartbeat receiver pass through optoisolators before reaching relay boards. This reduces ground loop risk.

### Strict return rule
All voltage levels must return only to their own DC-DC converter return path.

### Cross-voltage domain rule
Any signal crossing between different voltage domains, such as 3.3 V/5 V logic to 12 V/24 V control, must be galvanically isolated.

---

## 4. Base Station Software Infrastructure

The base station is responsible for path planning, manual control, system state supervision, emergency stop, and recovery authority.

### Base Station nodes

#### 4.1 Master/Mission Node
Responsibilities:
- Takes manually inserted GPS coordinates via an Excel sheet.
- Outputs commands to the LoRa node:
  - `/armed`
  - `/command_mode`
  - `/e-stop`
  - `/clear_estop`
  - `/path_plan`
- Is the sole originator of `/clear_estop`.
- Subscribes to `/status` from the rover at 2 Hz.
- Monitors bus voltage and E-stop state.
- Sending a new `/path_plan` fully overwrites the rover’s active GPS stack.

#### 4.2 Teleop Node
Responsibilities:
- Publishes manual velocity commands to `/cmd_vel_tele` at 10 Hz.
- These commands are transmitted to the rover through the base LoRa node.

#### 4.3 Base LoRa Node
Responsibilities:
- Transmits outgoing commands to the rover at 10 Hz.
- Receives `/status` telemetry from the rover at 2 Hz.
- Publishes received telemetry to the local base station `/status` topic.

---

## 5. Rover ROS and Software Infrastructure

The rover runs ROS with hardware-level safety watchdogs, CAN bus motor control, LoRa communications, emergency braking logic, and a two-stage power sequencing system.

---

## 5.1 Safety and Fail-Safe Mechanics

### LoRa connection timeout
An external physical hardware unit monitors the LoRa link. If the signal drops out, this hardware directly cuts power to Contactor 2, removing power from the high-voltage motor bus.

### Hardware-software state sync
The `state_machine` monitors `/bus_voltage`. If hardware cuts Contactor 2, the voltage drop is detected and the internal system state is immediately disarmed.

### ODrive watchdog fallback
The ODrive S1 motor drivers have onboard watchdogs. If `nav_blackbox` freezes and `/cmd_vel_nav` stops publishing, the `selection` node sends no command to `ros_odrive`, causing motor driver watchdogs to stop the wheels.

### E-stop types
1. **Base Station E-stop** — global override where all command topics/signals default to zero.
2. **Nav/Mission E-stop** — virtual soft stop where `mission_node` halts waypoint feeding and reports E-stop through nav status without overwriting the base hardware signal path.

---

## 5.2 Rover LoRa Node

### Function
The LoRa node is the only interface between the rover’s internal ROS network and the physical LoRa radio module.

### Workflow
- Decodes base station commands at 10 Hz.
- Packages rover `/status` telemetry for transmission to the base station at 2 Hz.

---

## 5.3 Mission Node

### Function
The `mission_node` manages the GPS waypoint stack and high-level mission execution.

### Workflow
- Receives GPS coordinate table via `/path_plan`.
- Pushes coordinates onto an internal stack.
- A new `/path_plan` overwrites the current stack.
- Acts as a ROS Action Client to send waypoint goals to `nav_blackbox`.
- Holds stack position when switching between autonomous and manual mode.
- When autonomous mode resumes, re-sends the active target waypoint to `nav_blackbox`.
- If `nav_blackbox` returns failure, sets status to `stall` or `e-stop` and halts mission execution.
- Publishes combined telemetry to `/status` at 2 Hz, including battery voltage, bus voltage, E-stop status, and navigation status.

---

## 5.4 Navigation Blackbox

### Function
`nav_blackbox` performs autonomous pathing and wheel velocity calculations.

### Interface
- Acts as a ROS Action Server.
- Receives waypoint goals from `mission_node`.
- Outputs `/cmd_vel_nav`.
- Returns action feedback and status.

---

## 5.5 Selection Node

### Function
The `selection` node is the command multiplexer and emergency braking manager.

### Inputs
- `/cmd_vel_nav`
- `/cmd_vel_tele`
- `/active_mode`
- `/e-stop`
- `/clear_estop`

### Standard operation
- If mode is autonomous, passes `/cmd_vel_nav` to `/cmd_vel`.
- If mode is manual, passes `/cmd_vel_tele` to `/cmd_vel`.
- `/cmd_vel` is consumed by `ros_odrive`.

### E-stop active braking sequence
When `/e-stop` activates:
1. Sends an RxSdo CAN write to set an emergency velocity ramp rate.
2. Sends `Set_Input_Vel` with zero velocity to force controlled rapid braking.

### E-stop recovery sequence
Recovery occurs only when valid `/clear_estop` is received from the base station Master Node.

Recovery steps:
1. Query encoder estimates and verify wheel speed is zero.
2. Restore normal soft ramp settings.
3. Check ODrive heartbeat.
4. If the driver is faulted, send `Clear_Errors` and `Set_Axis_State` to re-enter closed-loop control.
5. Re-enable `/cmd_vel` multiplexing.

---

## 5.6 State Machine Node

### Function
The `state_machine` is the hardware safety manager, power sequence controller, and lockout engine.

### Inputs
- `/command_mode`
- `/armed`
- `/main_battery_voltage`
- `/bus_voltage`
- `/e-stop`
- `/clear_estop`
- GPIO pins

### Main responsibilities
- Routes command mode to `/active_mode`, unless E-stop is active.
- Manages manual pre-charge and arm sequence.
- Checks battery voltage before pre-charge.
- Enables pre-charge GPIO.
- Checks voltage differential between main battery and bus voltage.
- Times out pre-charge after 2 seconds if voltage differential is not within threshold.
- Closes Contactor 2 if pre-charge succeeds.
- Opens contactor and disarms the system if voltage fault or safety fault occurs.
- Prevents automatic rearming after a trip.

### Pre-charge sequence
1. Requires a fresh rising edge on `/armed` and `/e-stop`.
2. Checks Batrium BMS over CAN.
3. Aborts if main battery voltage is below 40.8 V.
4. Enables pre-charge GPIO to activate SSR and resistor path.
5. Waits until `(Main Battery Voltage - Bus Voltage) <= 2 V`.
6. If threshold is not reached within 2 seconds, aborts.
7. If successful, activates Contactor 2 and disables pre-charge.

### Lockout rule
If voltage drops below 40.8 V, or if a contactor opens because of E-stop or external LoRa cut, the system disarms. It cannot re-close automatically and requires a manual disarm/re-arm sequence.

---

## 5.7 ros_odrive Motor Drive Node

### Function
`ros_odrive` is the low-level motor interface over CAN bus.

### Responsibilities
- Converts `/cmd_vel` into CAN motor commands.
- Polls ODrive S1 motor drivers.
- Reads bus voltage and main battery voltage via CAN.
- Publishes `/bus_voltage` and `/main_battery_voltage`.
- Executes CAN frames requested by `selection` and `state_machine`.

### Logic power
ODrive logic boards receive auxiliary power separate from the high-voltage traction bus.

---

## 6. Rover-Side ROS Topic Dictionary

| Topic / Interface | Publisher / Server | Subscriber / Client | Purpose |
|---|---|---|---|
| `/e-stop` | LoRa | Mission, State Machine, Selection | Fail-safe signal. 0 = STOP, 1 = GO. |
| `/clear_estop` | LoRa | Selection, State Machine | Base-only command to clear E-stop. |
| `/command_mode` | LoRa | State Machine | Desired mode: autonomous or manual. |
| `/armed` | LoRa | State Machine | Boolean rising-edge trigger for contactor sequence. |
| `/path_plan` | LoRa | Mission Node | Stack of GPS coordinates. New path overwrites old stack. |
| `/cmd_vel_tele` | LoRa at 10 Hz | Selection Node | Manual velocity commands from base station. |
| `/cmd_vel_nav` | Nav Blackbox | Selection Node | Autonomous velocity command. |
| `/cmd_vel` | Selection Node | ros_odrive | Final multiplexed motor velocity command. |
| `/active_mode` | State Machine | Selection Node | Verified operating mode: manual, auto, or e-stop. |
| `/bus_voltage` | ros_odrive | State Machine, Mission | S1 motor driver bus voltage via CAN. |
| `/main_battery_voltage` | ros_odrive | State Machine, Mission | Batrium BMS main battery voltage via CAN. |
| `/status` | Mission Node | LoRa at 2 Hz | Combined telemetry sent to base. |
| `nav_goal` | Nav Blackbox Action Server | Mission Node Action Client | Waypoint action goal, feedback, and status interface. |

---

## 7. Normal Operating Flow

### Manual operation
1. Base station teleop node publishes `/cmd_vel_tele` at 10 Hz.
2. Base LoRa node sends command to rover.
3. Rover LoRa node decodes command.
4. State machine verifies `/active_mode`.
5. Selection node passes `/cmd_vel_tele` to `/cmd_vel`.
6. `ros_odrive` converts `/cmd_vel` into CAN commands.
7. ODrive motor drivers drive the wheels.
8. Mission node reports status back to base through LoRa at 2 Hz.

### Autonomous operation
1. Base station Master/Mission Node sends `/path_plan`.
2. Rover LoRa node receives and publishes `/path_plan` internally.
3. `mission_node` overwrites its waypoint stack with the new path.
4. `mission_node` sends active waypoint to `nav_blackbox` as `nav_goal`.
5. `nav_blackbox` computes velocity and publishes `/cmd_vel_nav`.
6. Selection node passes `/cmd_vel_nav` to `/cmd_vel` when active mode is autonomous.
7. `ros_odrive` executes motor commands over CAN.
8. `mission_node` reports mission and battery status through `/status`.

---

## 8. Power-Up and Arming Flow

1. Battery packs are connected in series.
2. 100 A fuses protect the battery positive lines.
3. Physical isolator is switched on.
4. Always-on 12 V DC-DC powers Batrium Watchmon.
5. Batrium checks cell monitor state through the two K9 monitors.
6. If battery state is safe and the physical E-stop is unpressed, Contactor 1 can energise.
7. Contactor 1 powers 5 V, 12 V, and 24 V auxiliary converters.
8. Pi, sensors, relays, and logic systems boot.
9. To arm traction, the state machine requires a valid rising edge on `/armed` and safe E-stop state.
10. State machine checks main battery voltage; aborts if below 40.8 V.
11. State machine enables pre-charge through SSR and resistor.
12. State machine waits until bus voltage is within 2 V of main battery voltage.
13. If successful within 2 seconds, Contactor 2 closes.
14. High-voltage traction bus powers ODrive motor drivers.
15. Pre-charge path is disabled.
16. Rover is ready for manual or autonomous velocity command flow.

---

## 9. E-Stop and Recovery Flow

### E-stop activation
E-stop can occur from:
- base station global E-stop,
- nav/mission soft stop,
- physical E-stop,
- Batrium battery fault,
- LoRa connection timeout,
- low-voltage or bus-voltage fault.

### Effects
- Command topics/signals default to zero for base E-stop.
- `selection` sends emergency braking CAN commands.
- LoRa timeout hardware cuts Contactor 2 directly.
- State machine detects bus voltage drop and disarms.
- No automatic rearming is allowed.

### Recovery
Recovery requires `/clear_estop` from the base station Master Node. The rover cannot self-clear an E-stop.

Recovery requires:
1. Confirm zero wheel speed.
2. Restore normal velocity ramp rate.
3. Clear ODrive errors if required.
4. Re-enter closed-loop control if required.
5. Re-enable command multiplexing.
6. Manual disarm/re-arm sequence if contactor lockout occurred.

---

## 10. Key Safety Rules

- Physical isolator must only be switched off when the rover is stopped and motors are disabled.
- Batrium BMS must remain always-on.
- Contactor 1 requires both physical E-stop unpressed and Batrium OK.
- Contactor 2 requires Pi relay, LoRa heartbeat relay, and latching button all closed.
- Cross-voltage signals must be galvanically isolated.
- Each voltage level must return only to its own DC-DC converter.
- Rover cannot automatically recover from E-stop.
- `/clear_estop` can originate only from the base station Master Node.
- Pre-charge must complete before closing Contactor 2.
- Pre-charge aborts if bus voltage does not come within 2 V of main battery voltage within 2 seconds.
- Main battery voltage below 40.8 V prevents or trips traction arming.

---

## 11. Important Values to Preserve

| Item | Value |
|---|---|
| Downlink rate | 10 Hz |
| Uplink telemetry rate | 2 Hz |
| Chassis | 40 × 40 mm aluminium T-slot extrusion |
| Wheel diameter | 10.2 inches / ~259.1 mm |
| Battery config | two 6S 1600 mAh 15C lithium packs in series |
| Battery equivalent | 12S equivalent pack |
| Battery fuse | 100 A per battery positive |
| Logic converter branches | 5 V, 12 V, 24 V |
| Converter branch fuses | 2.5 A according to source architecture |
| Pre-charge threshold | Main battery voltage - bus voltage <= 2 V |
| Pre-charge timeout | 2 seconds |
| Low-voltage lockout | 40.8 V |
| Motor command output | `/cmd_vel` to `ros_odrive` |
| Manual command source | `/cmd_vel_tele` |
| Autonomous command source | `/cmd_vel_nav` |
| Clear E-stop authority | Base Station Master Node only |

---

## 12. Open Verification Items

These items should be verified with the physical rover or latest team documentation:

1. Confirm whether battery capacity is actually **1600 mAh** or **16 Ah**.
2. Confirm the exact DC-DC converter models and current ratings.
3. Confirm whether 2.5 A fuses are on converter input or output branches.
4. Confirm physical pre-charge resistor value and wattage rating.
5. Confirm ODrive S1 model, motor current limits, and CAN node IDs.
6. Confirm exact LoRa heartbeat hardware implementation.
7. Confirm GPIO pin assignments for Pi relay, pre-charge SSR, and Contactor 2 control.
8. Confirm Batrium CAN message format and voltage decoding.
9. Confirm whether the ROS implementation is ROS 2 or mixed ROS/ROS 2; the architecture file refers to ROS generally but uses ROS-style topics/actions.
10. Confirm final topic message types for `/path_plan`, `/status`, and `nav_goal`.

---

## 13. Handover Prompt for Another Chat

Copy this into a new chat along with the architecture document:

```text
You are helping me continue the Knuckey Rover project. Use the uploaded architecture document as the source of truth. The rover has a Base Station and Rover communicating over LoRa. Downlink is 10 Hz and uplink telemetry is 2 Hz. The rover uses two 6S 1600 mAh 15C lithium batteries in series with 100 A fuses and a physical isolator. Batrium Watchmon and two K9 cell monitors provide always-on BMS safety. Contactor 1 powers the logic layer through 5 V, 12 V, and 24 V DC-DC converters. Contactor 2 powers the high-voltage ODrive motor traction bus and is controlled through Pi relay, LoRa heartbeat relay, and latching button interlocks. A pre-charge circuit using an SSR and chassis-mount resistor must bring bus voltage within 2 V of main battery voltage within 2 seconds before Contactor 2 closes. The state machine aborts if main battery voltage is below 40.8 V and does not allow auto-rearm after safety trip.

Software architecture: Base Station Master/Mission Node sends /armed, /command_mode, /e-stop, /clear_estop, and /path_plan to LoRa. Teleop publishes /cmd_vel_tele at 10 Hz. Rover LoRa decodes commands. mission_node manages GPS waypoint stack and sends nav_goal actions to nav_blackbox. nav_blackbox outputs /cmd_vel_nav. selection node multiplexes /cmd_vel_nav or /cmd_vel_tele into /cmd_vel based on /active_mode and handles E-stop active braking/recovery over CAN. state_machine handles contactor/power sequencing, pre-charge, voltage lockout, and active mode. ros_odrive converts /cmd_vel to CAN motor commands and publishes /bus_voltage and /main_battery_voltage. /status is published at 2 Hz back to base. The Base Station Master Node is the only source allowed to clear E-stop using /clear_estop.

Help me with future work using this architecture without contradicting these details. If a detail is missing, ask me to verify it against hardware or the source file.
```

---

## 14. Recommended Next Engineering Tasks

1. Build a power-up test checklist based on the dual contactor sequence.
2. Create a ROS node interface specification for every topic in the dictionary.
3. Define message schemas for `/status`, `/path_plan`, and `nav_goal`.
4. Write state-machine pseudocode for pre-charge, arm, disarm, E-stop, and recovery.
5. Write `selection` node pseudocode for manual/autonomous command multiplexing and CAN E-stop braking.
6. Validate battery capacity and update runtime calculations.
7. Create wiring validation checklist for Batrium, contactors, flyback diodes, optoisolators, and DC-DC returns.
8. Create CAN frame map for ODrive commands and BMS voltage readings.
9. Simulate LoRa dropout and confirm Contactor 2 cuts out physically.
10. Confirm that software state mirrors hardware contactor state using `/bus_voltage`.
