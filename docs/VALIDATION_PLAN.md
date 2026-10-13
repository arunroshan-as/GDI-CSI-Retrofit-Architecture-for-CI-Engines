# Validation Plan

| Stage | Purpose | Replaces |
|---|---|---|
| 1. Injector bench | flow vs pressure, opening/closing delay, minimum pulse | assumed CdA, delays |
| 2. Single-cylinder test cell | BTE, NOx, CO, HC, PM, COV, pressure traces over a speed-load grid | parametric BTE/NOx maps |
| 3. SOI / spark sweeps | optimum timings, pre-ignition boundary | rule-based timing maps |
| 4. Multi-cylinder engine | torque curve, transient behaviour, cycle emissions | performance curves |
| 5. ECU HIL / vehicle | safety layers, fault handling, durability | interface-level assumptions |

Success criteria for the targets in this repository: map-average efficiency gain of 17-22 % vs the diesel baseline at equal torque, cycle NOx reduced by an order of magnitude, COV(IMEP) below 3 % across the lean window, no pre-ignition events across the calibrated envelope.
