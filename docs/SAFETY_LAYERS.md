# Layered Safety Architecture

| Layer | Function |
|---|---|
| L0 Hardware | check valve, quench geometry, H2 leak detection, solenoid shut-off, pressure relief |
| L1 Plausibility | sensor range and rationality, rail P/T limits, safe shut-off on fault |
| L2 Timing scheduler | CKP/CAM-synchronised SOI/EOI/spark from maps, injector ballistics compensation |
| L3 Combustion limits | pre-ignition guard, COV monitor, bounded SOI and spark trims |
| L4 Supervisory | lambda/load governor, derate, fuel-quality handling |

Operating-envelope boundaries in `results/figures/16_safety_envelope_and_stability.png` are illustrative and must be replaced with measured limits.
