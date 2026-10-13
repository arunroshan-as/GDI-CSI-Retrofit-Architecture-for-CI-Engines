# ECU Interface (interface level)

This repository does not contain ECU firmware. The embedded implementation (STM32, CKP decoding, scheduling) lives with the parent project:
[Hydrogen-IC-Engine-Retrofit-for-Heavy-Commercial-Vehicles](https://github.com/arunroshan-as/Hydrogen-IC-Engine-Retrofit-for-Heavy-Commercial-Vehicles).

## Signals consumed by the ECU
| Signal | Use |
|---|---|
| CKP (60-2 wheel) | crank angle and speed, gap-based reference |
| CAM phase | 720 deg phase (compression vs exhaust TDC) |
| MAP / IAT | charge mass, lambda estimate |
| Rail pressure / temperature | injection duration compensation |
| H2 leak sensor(s) | L0/L1 safety trips |
| Knock / ion or cylinder-pressure proxy | L3 combustion limits |
| Lambda sensor (where fitted) | trim |

## Outputs
| Output | Content |
|---|---|
| Injector driver | command start/end angle or time, peak-and-hold current profile |
| Coil driver | dwell start, spark angle |
| Shut-off valve | safe isolation on fault |

## Scheduling flow (per cylinder, per cycle)
1. Decode CKP, resolve phase with CAM.
2. Look up from the calibration map: rail pressure target, SOI/EOI, spark, dwell for current (rpm, load).
3. Convert angles to timer events; compensate injector open/close delay and rail-pressure-dependent flow.
4. Arm coil dwell, fire injector, fire spark.
5. Evaluate L1-L4 supervisors; trim or trip.

See `results/figures/08_ecu_ckp_cam_timing.png` and `results/figures/07_injector_drive_waveform.png`.
