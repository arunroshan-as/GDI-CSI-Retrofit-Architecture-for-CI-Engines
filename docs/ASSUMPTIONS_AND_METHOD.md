# Assumptions and Method

## What is computed
* Cylinder volume from slider-crank kinematics.
* Motored pressure: polytropic, n = 1.34.
* Fired pressure and heat release: single-zone first-law model with Wiebe burn functions (retrofit) and a double-Wiebe premixed/diffusion burn (diesel), 12 % heat loss.
* Injector mass flow: compressible orifice (choked / sub-critical) for a hydrogen-like gas.
* SOI: found by backward integration of injected mass.

## What is assumed (parametric, not computed from physics)
* Diesel BTE map: `37.5 % * f(load) * g(speed)`.
* Retrofit BTE: diesel BTE multiplied by a relative-gain surface of about 15-21 % (mean 19.5 %). **This surface encodes the efficiency target; it is not a prediction.**
* NOx: thermal term peaking near lambda 1.4 plus a load-dependent stratification floor; diesel NOx a linear surface. CO, HC, PM are placeholder values.
* Torque gain at low speed from boosted lean operation (+10 % at 1000 rpm).
* Fuel is represented as hydrogen-equivalent energy (120 MJ/kg, 3.5 MJ per kg air at lambda 1). Blend composition is not modelled.
* Injector effective area 2.4 mm2, opening delay 0.18 ms, closing delay 0.12 ms, coil dwell 2.2 ms.
* Safety-envelope boundaries and COV curves in figure 16 are illustrative.

## Known limitations
* No heat-transfer correlation, no NOx kinetics, no CFD, no wall wetting or jet penetration model.
* Emissions are not tested against a regulatory cycle; the 9-mode cycle is illustrative.
* Literature on hydrogen direct-injection engines reports peak efficiencies in the low-to-mid 40 % range; the 45 % peak here sits at the optimistic end and should be treated as a target.

Replace every parametric surface with measured data as soon as test-cell results exist.
