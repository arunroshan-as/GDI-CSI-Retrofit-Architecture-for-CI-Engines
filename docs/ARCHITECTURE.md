# Retrofit Architecture

## What changes and what is retained

| Retained from donor CI engine | Replaced / added |
|---|---|
| Block, crankshaft, connecting rods, bearings | **Cylinder head** (GDI-CSI head, CR ~16:1) |
| Turbocharger and exhaust path | **Gas injectors** (gaseous, CRDi-type, H2 + HPF compatible) |
| Cooling and lubrication circuits | **Gas common rail**, regulator, check valve, shut-off valves |
| Intake manifold (with charge-restriction means at light load) | **Iridium H2-compatible spark plugs and coils** |
| Mounts, drive-line | **Retrofit ECU** and wiring harness, H2 leak sensing |

## Why a replacement head
Direct gaseous injection needs an injector boss, a spark-plug boss with a protected electrode, quench geometry and a compression-ratio change that cannot be retro-machined into most diesel heads. A purpose-built head also fixes injector-to-plug spacing, which sets mixing time before ignition.

## Why CSI
Hydrogen auto-ignition at diesel compression ratios is unreliable at lean conditions; pure compression ignition is hard to control. Spark assistance gives a defined ignition event synchronised to the CKP signal, and a lower compression ratio than the diesel donor keeps the end-of-compression temperature away from pre-ignition.

## Cycle
Intake (lean, boosted) -> compression with late gas injection -> spark -> fast lean burn -> exhaust. Timing values are in [`INJECTION_STRATEGY.md`](INJECTION_STRATEGY.md).

## Out of scope here
Fuel composition, storage-vessel design, materials selection per component and production calibration are intentionally not disclosed.
