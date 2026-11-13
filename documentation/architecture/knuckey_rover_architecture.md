# Knuckey Rover - System Architecture & Hardware Specification

> **Note for AI Assistants**: This document outlines the ROS-based architecture, physical mechanics, electrical power distribution, safety contactors, node configurations, logic flows, CAN bus framing protocols, and communication protocols for the "Knuckey Rover" project. Please use this as the primary context for answering questions regarding system logic, electrical wiring, physical specs, troubleshooting, safety protocols, CAN messaging, or node development.

## 1. System Overview
The Knuckey Rover operates via a Base Station and a Rover unit communicating over a LoRa network.
* **Downlink (Base -> Rover)**: High-frequency command streaming at **10Hz** for responsive teleoperation and control.
* **Uplink (Rover -> Base)**: Throttled telemetry streaming at **2Hz** to prevent LoRa bandwidth saturation.
* **Base Station**: Receives pre-defined maps (e.g., Tom's farm GPS data), plans routes, and dictates operating modes (Autonomous vs. Manual/Tele-op). It serves as the primary controller for mission execution, safety (E-stop), and recovery (`/clear_estop`).
* **Rover**: A ROS-based autonomous vehicle that follows commands from the base station, executes navigation logic, reports telemetry/status, handles CAN-level motor control, and executes emergency braking and multi-stage hardware power management.

---

## 2. Physical & Mechanical Design
* **Chassis Frame**: Built from **40x40mm Aluminum T-Slot Extrusion**, providing a modular and structurally rigid mounting platform for hardware, enclosures, and drive systems.
* **Drive Wheel Diameter**: **10.2 inches** (~259.1 mm), used for odometry, velocity calculations, and motor driver configuration.

---

## 3. Electrical Design & Power Distribution

### 3.1. Battery Configuration & Protection
* **Battery Pack**: Two **6S 1600mAh 15C** Lithium batteries wired in **series** (forming a 12S equivalent nominal pack).
* **Fusing**: Dedicated **100A fuses** connected directly to the positive terminal of each battery.
* **Main Wiring Bus**: Arranged with one main positive terminal, one main negative terminal, and a series jumper connecting the positive of battery 1 to the negative of battery 2.
* **Physical Isolator Switch**: A high-current physical isolator switch is located on the main positive line.
  * *Operational Rule*: Must **only** be deactivated when the rover is fully stopped and motors are already disabled.

### 3.2. BMS & Always-On Safety Circuit
* **Cell Monitoring**: Two **Batrium K9 cell monitors** (one per battery) interface with a central **Batrium Watchmon** BMS.
* **Independent Power Supply**: An independent **12V DC-DC converter** powers the Batrium Watchmon directly from the battery side (bypassing all contactors). This ensures the Batrium BMS remains active 100% of the time, regardless of contactor states.
* **Batrium Expansion Board Relay**:
  * The 12V output powers a control loop running in series through the Batrium Expansion Board relay and a physical **Normally Closed (NC) E-Stop switch**.
  * **Contactor 1 Interlock**: Both the physical E-Stop must be closed (unpressed) **AND** the Batrium system must actively pull its relay closed (no battery faults detected) for Contactor 1 to energize.
  * **Fault Trigger**: If Batrium detects any battery fault (cell over/under voltage, over-temp), it opens the relay, tripping Contactor 1 and shutting down the entire rover except for the Batrium monitoring system itself.

### 3.3. Dual Contactor Architecture & DC-DC Layers

```
Main Battery Positive
        │
  [100A Fuse]
        │
 [Physical Isolator]
        │
   ├──> [12V DC-DC] ─────────> Batrium Watchmon (Always ON)
        │
  [Contactor 1] ──(Coil: Batrium OK + Physical NC E-Stop)
        │
        ├──> [5V DC-DC]  (2.5A Fuse) ──> Logic Layer (Raspberry Pi 5, Sensors)
        ├──> [12V DC-DC] (2.5A Fuse) ──> Auxiliary Systems / Relays
        ├──> [24V DC-DC] (2.5A Fuse) ──> High-Voltage Logic / Interfaces
        │
  [Contactor 2] ──(Coil: Series Relays [Pi 5 + LoRa Heartbeat] + Latching Button)
   ├── [Pre-charge Circuit: SSR + Chassis Mount Resistor]
        │
        └──> [High-Voltage Traction Bus] ──> ODrive Motor Drivers
```

#### Contactor 1 (Logic Layer Power)
* Connects Main Battery Positive to the **Logic Layer** (powers all computing and low-voltage systems; excludes the motor traction bus).
* **Downstream Converters**: Feeds three dedicated DC-DC converters, each individually fused with a **2.5A fuse**:
  * **5V DC-DC Converter**
  * **12V DC-DC Converter**
  * **24V DC-DC Converter**

#### Contactor 2 (High-Voltage Motor Traction Bus)
* Connects the Main Battery Positive directly to the high-voltage motor bus (ODrive motor drivers).
* **Coil Control Loop**: Powered via downstream logic power and wired through a series of safety interlocks:
  * A **Raspberry Pi 5 GPIO relay**.
  * A **LoRa Heartbeat relay**.
  * A physical **Normally Closed (NC) Latching Button**.
  * *Activation Rule*: **Both** the Pi 5 and the LoRa Heartbeat must actively hold their respective relays closed to energize Contactor 2.
* **Pre-charge Relay Circuit**: A secondary bypass line spans across the terminals of Contactor 2 via a **Solid State Relay (SSR)** in series with a **chassis-mount resistor** to safely charge driver capacitors prior to closing Contactor 2.

#### Coil EMF Protection
* Both Contactor 1 and Contactor 2 are fitted with **flyback diodes** across their coils to safely collapse back-EMF spikes upon coil release.

### 3.4. Signal Isolation & Ground Loop Prevention
* **Optoisolation**: Signal lines from the Raspberry Pi 5 and the LoRa heartbeat receiver pass through **optoisolators** before connecting to the relay board to eliminate ground loops.
* **Strict Return Rule**: **All voltage levels MUST always return exclusively to their respective DC-DC converter.**
* **Cross-Voltage Domain Rule**: Any communications or signals spanning across different voltage domains (e.g., 3.3V/5V logic to 12V/24V levels) **MUST be galvanically isolated**.

---

## 4. Base Station Architecture
The base station is responsible for path planning, manual control, overarching system state, and emergency recovery authority.

### Workflows & Nodes
* **Master/Mission Node**: 
  * Takes manually inserted GPS coordinates via an Excel sheet.
  * Outputs topics to LoRa Node: `/armed`, `/command_mode`, `/e-stop`, `/clear_estop`, and `/path_plan`.
  * **E-Stop Clear Authority**: Serves as the **sole originator** of the `/clear_estop` signal. The Rover cannot recover from an E-stop automatically; recovery requires an explicit command from the Master Node.
  * Publishing a new `/path_plan` completely **overwrites** the active GPS stack on the Rover.
  * Subscribes to `/status` (received from the Rover at 2Hz) and monitors `bus_voltage` and E-stop status.
* **Teleop Node (`teleop_twist`)**: 
  * Outputs manual driving commands to `/cmd_vel_tele` at **10Hz**, which feeds into the LoRa node.
* **Base LoRa Node**: 
  * Transmits outgoing commands (`/armed`, `/command_mode`, `/e-stop`, `/clear_estop`, `/path_plan`, `/cmd_vel_tele`) to the Rover at **10Hz**.
  * Receives `/status` payload from the Rover at **2Hz** and publishes it to the local Base Station `/status` topic.

---

## 5. Rover ROS & Software Architecture
The Rover runs on ROS (Robot Operating System) coupled with hardware-level safety watchdogs, CAN bus framing protocols, and active motor braking sequences.

### 5.1. Safety & Fail-Safe Mechanics (Hardware & Software)
* **LoRa Connection Timeout**: An **external physical hardware unit** monitors the LoRa link. If signal dropout occurs, this unit directly cuts power to Contactor 2, removing power from the high-voltage motor bus instantly.
* **Hardware-Software State Sync**: The `state_machine` continuously monitors `/bus_voltage`. If physical safety hardware cuts Contactor 2, `state_machine` detects the sudden voltage drop and immediately disarms the internal system state.
* **Motor Driver Watchdogs & Silent Fallback**: The ODrive (S1) motor drivers feature onboard software watchdogs. If `nav_blackbox` freezes or crashes, `/cmd_vel_nav` stops publishing. `selection` passes no commands to `ros_odrive`, triggering the driver watchdogs to safely stop the wheels.
* **Volatile E-Stop Signals**:
  * **Base Station E-Stop**: Global override where all topics/signals default to `0`.
  * **Nav / Mission E-Stop**: Virtual soft stop where `mission_node` halts feeding points and reports `e-stop` via the nav status payload without clobbering base hardware signals.

### 5.2. LoRa Node
* **Function**: Sole interface between Rover's internal ROS network and physical LoRa radio module.
* **Workflow**: Decodes Base Station commands at 10Hz; packages internal status (`/status`) for transmission back to base at 2Hz.

### 5.3. Mission Node (`mission_node`)
* **Function**: Manages GPS waypoint stack and high-level mission execution using a **ROS Action Client**.
* **Workflow**:
  * Receives table of GPS coordinates via `/path_plan` and pushes them onto a stack. Receiving a new `/path_plan` overwrites the existing stack.
  * Acts as a **ROS Action Client** to send waypoints as action goals to `nav_blackbox`.
  * **Mode Switch & Resume**: Switching modes (Autonomous <-> Manual) holds the stack position. Re-activating Autonomous mode re-sends the active target waypoint goal to `nav_blackbox`.
  * **Error Handling**: If nav action server returns a failure status, sets internal status to `stall`/`e-stop` and halts mission execution.
  * **Telemetry Output**: Reads both `main_battery_voltage` and `bus_voltage`, combining them with current E-stop status and nav status into `/status` (published at 2Hz).

### 5.4. Navigation Blackbox (`nav_blackbox`)
* **Function**: Autonomous pathing and wheel velocity calculations acting as a **ROS Action Server**.
* **Inputs/Outputs**: Receives waypoint goals from `mission_node` action client; outputs `/cmd_vel_nav` and returns action feedback/status.

### 5.5. Selection Node (`selection`) & E-Stop CAN Protocol
* **Function**: Multiplexer for motor commands and manager of CAN-level active emergency braking and recovery sequences.
* **Inputs**: `/cmd_vel_nav`, `/cmd_vel_tele`, `/active_mode`, `/e-stop`, `/clear_estop`.
* **Standard Operation**: Directs `/cmd_vel_nav` (Auto mode) or `/cmd_vel_tele` (Manual mode) to `/cmd_vel`.
* **E-Stop Active Braking Sequence**:
  Upon activation of `/e-stop` (or mode override to E-stop):
  1. **Write Fast Ramp Rate**: Issues RxSdo (`CMD_ID: 0x004`) with an 8-byte payload (`Opcode = 1 [Write]`, `Endpoint_ID` for `axis0.controller.config.vel_ramp_rate`) to set an **emergency ramp rate** (e.g., `20.0 turns/s²`).
  2. **Command Zero Velocity**: Immediately issues `Set_Input_Vel` (`CMD_ID: 0x00D`) with `Input_Vel = 0.0` to force rapid controlled braking.
* **E-Stop Recovery Sequence**:
  Executed **ONLY** when a valid `/clear_estop` command is received from the Base Station Master Node:
  1. **Verify Zero Velocity**: Queries `Get_Encoder_Estimates` (`CMD_ID: 0x009`) to confirm wheel speed is `0.0` and the vehicle is completely stationary.
  2. **Restore Soft Ramp Settings**: Issues RxSdo (`CMD_ID: 0x004`) to write standard driving acceleration back to `vel_ramp_rate`.
  3. **Clear Faults & Re-Arm ODrive (If Tripped)**: Hard braking may trigger over-voltage or DC bus current spikes. Checks ODrive Heartbeat (`CMD_ID: 0x001`). If `Axis_State != 8` (`CLOSED_LOOP_CONTROL`):
     * Sends `Clear_Errors` (`CMD_ID: 0x018`, payload `1`).
     * Sends `Set_Axis_State` (`CMD_ID: 0x007`, payload `8`) to re-enable closed-loop control.
  4. **Resume Command Flow**: Re-enables `/cmd_vel` multiplexing to stream teleop/navigation commands to `ros_odrive`.

### 5.6. State Machine Node (`state_machine`)
* **Function**: Hardware safety manager, power sequence controller, and lock-out engine.
* **Inputs**: `/command_mode`, `/armed`, `/main_battery_voltage`, `/bus_voltage`, `/e-stop`, `/clear_estop`, and GPIO pins.
* **Sequence Logic**:
  1. **Mode Routing**: Relays `/command_mode` to `/active_mode` (held low if `/e-stop` is active).
  2. **Manual Pre-Charge & Arm Sequence**:
     * **Rising-Edge Trigger**: Arming requires a fresh rising-edge broadcast (`0` -> `1`) on `/armed` and `/e-stop`. Persistent `1` states across reboots will not initiate auto-arm.
     * **Battery Pre-Check**: Checks Batrium BMS reading over CAN. If `Main Battery Voltage < 40.8V`, the sequence aborts before engaging pre-charge.
     * State machine enables Pre-charge GPIO pin (SSR + chassis mount resistor).
     * Evaluates voltage differential over CAN: `(Main Battery Voltage - Bus Voltage) <= 2V`.
     * **Timeout Safeguard**: Starts a **2-second timer**. If differential threshold (`<= 2V`) is not met within 2 seconds, pre-charge sequence **aborts**.
     * If successful, activates Contactor 2 GPIO pin and disables pre-charge circuit.
  3. **Latching Voltage & Fault Lockout**:
     * Continuously monitors battery voltages via CAN.
     * If voltage drops below **40.8V** (or contactor opens due to E-stop / external hardware LoRa cut), contactor opens immediately and internal ROS state sets to **disarmed**.
     * **No Auto-Rearm**: Once tripped or opened, the contactor cannot re-close automatically. It requires a manual disarm/re-arm sequence to re-trigger the pre-charge sequence.

### 5.7. Motor Drive Node (`ros_odrive`)
* **Function**: Low-level hardware interface for wheel motors (S1 drivers) over CAN bus.
* **Logic Power**: ODrive logic boards receive auxiliary power separate from the main high-voltage traction bus.
* **Workflow**:
  * Converts `/cmd_vel` into CAN commands for wheel motors.
  * Polls drivers and reads both **Bus Voltage** and **Main Battery Voltage** (from Batrium BMS) via CAN bus; publishes to `/bus_voltage` and `/main_battery_voltage`.
  * Handles lower-level execution of CAN frames requested by `selection` / `state_machine`.

---

## 6. ROS Topic Dictionary (Rover Side)

| Topic / Interface | Type | Publisher / Server | Subscriber / Client | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/e-stop` | Topic | LoRa | Mission, State Machine, Selection | Fail-safe safety signal (0 = STOP, 1 = GO). |
| `/clear_estop` | Topic | LoRa | Selection, State Machine | Command originating ONLY from Base Station Master Node to clear E-stop. |
| `/command_mode` | Topic | LoRa | State Machine | Desired operating mode (`autonomous` or `manual`). |
| `/armed` | Topic | LoRa | State Machine | Boolean trigger (0 -> 1 rising edge required) for contactor sequence. |
| `/path_plan` | Topic | LoRa | Mission Node | Stack of GPS coordinates for the mission (Overwrites stack on send). |
| `/cmd_vel_tele` | Topic | LoRa (10Hz) | Selection Node | Manual driving velocity commands from base station. |
| `/cmd_vel_nav` | Topic | Nav Blackbox | Selection Node | Autonomous driving velocity commands. |
| `/cmd_vel` | Topic | Selection Node | ros_odrive | Multiplexed motor velocity command sent to CAN drivers. |
| `/active_mode`| Topic | State Machine | Selection Node | Verified operational state (`manual`, `auto`, `e-stop`). |
| `/bus_voltage` | Topic | ros_odrive | State Machine, Mission | S1 motor driver bus voltage via CAN. |
| `/main_battery_voltage` | Topic | ros_odrive | State Machine, Mission | Batrium BMS main battery voltage via CAN. |
| `/status` | Topic | Mission Node | LoRa (2Hz) | Combined telemetry (voltages, e-stop state, nav state) transmitted at 2Hz. |
| `nav_goal` | ROS Action | Nav Blackbox (Server) | Mission Node (Client) | Action interface for waypoint dispatch, status, and feedback. |
