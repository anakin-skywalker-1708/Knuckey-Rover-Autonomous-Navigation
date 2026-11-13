# Validation evidence and limitations

| Scenario | Waypoints reached | Total | Context |
|---|---:|---:|---|
| Dual EKF enabled | 32 | 34 | Simulated agricultural tramline route, approx. 2.65 km |
| Without EKF | 28 | 34 | Same reported simulation comparison |

These figures are from project report/handover descriptions; they are **simulation results**, not field performance. The remaining navigation failures were associated with controller goal tolerance/timeouts. Raw logs and reproducible test configuration should be added from the original rover project folder before treating this as a reproducible benchmark.

Checks to archive: launch configuration, simulation time settings, GPS/IMU/odom topics, TF tree, waypoint list, Nav2 parameter files, ROS bags, success/failure criteria, and software versions.
