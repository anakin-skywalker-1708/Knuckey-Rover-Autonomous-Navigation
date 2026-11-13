# Electrical and safety architecture — design documentation only

The documented design uses an always-on Batrium Watchmon with two K9 cell monitors, a physical NC E-stop, Contactor 1 for logic power, and Contactor 2 for the ODrive traction bus. Contactor 2 depends on Pi GPIO, independent LoRa heartbeat and a latching interlock. A resistor/SSR pre-charge circuit charges the traction bus before contactor closure.

The architecture specifies an abort below 40.8 V, pre-charge bus difference <= 2 V within 2 seconds, and **no automatic re-arm after a fault**. These values describe the source design, **not validated safe operating instructions**. Physical component ratings, battery capacity (1600 mAh vs 16 Ah discrepancy), GPIO, CAN IDs, contactor ratings and pre-charge resistor must be verified against actual hardware before commissioning. Never use this portfolio as a wiring or safety commissioning manual.

See the complete source `knuckey_rover_architecture.md` and `knuckey_rover_handover(2).md`.
