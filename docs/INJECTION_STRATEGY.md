# Injection and Spark Strategy

All values are model-derived reference values ([`../data/gdi_csi_calibration_map.csv`](../data/gdi_csi_calibration_map.csv)).

## Envelope (generic 5.6 L HCV donor)

| Quantity | Min | Max |
|---|---|---|
| SOI (flow) [deg BTDC] | 13.7 | 38.2 |
| EOI (flow) [deg BTDC] | 9.0 | 16.7 |
| Spark [deg BTDC] | 4.0 | 11.7 |
| Rail pressure [bar] | 63 | 100 |
| Injection duration [ms] | 0.40 | 1.76 |
| H2-equivalent fuel [mg/cycle/cyl] | 3.4 | 24.4 |
| Lambda | 1.98 | 6.49 |

## Rules
1. Spark advance: `4 + 5*(rpm-800)/1600 + 3*(1-load)` deg BTDC.
2. EOI = spark + 5 deg.
3. SOI solved by integrating compressible orifice mass flow backwards from EOI; effective flow area 2.4 mm2, T0 = 310 K.
4. Rail pressure `60 + 30*load + 10*(rpm-800)/1600` bar, clipped to the envelope.
5. Lambda `lambda_full * load^-0.45`, capped at 6, with `lambda_full` between about 2.0 and 2.25 across speed.
6. ECU command timing = flow timing shifted by injector delays (open 0.18 ms, close 0.12 ms, assumed). Minimum energising time 0.25 ms.
7. Coil dwell 2.2 ms (assumed).

## Known limiting conditions
* **Light-load fuel quantity** (3-4 mg/cycle) gives 0.4 ms pulses - close to the minimum controllable pulse. Injector turn-down is a validation item.
* **High-speed full load**: SOI moves to ~38 deg BTDC; early injection raises pre-ignition risk and must be checked against the safety envelope.
* **Full-load NOx** is highest where lambda is lowest.
