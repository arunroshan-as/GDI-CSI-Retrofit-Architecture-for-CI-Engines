"""
GDI-CSI retrofit reduced-order model (preliminary, simulation-based).

Scope
-----
Generic heavy-commercial-vehicle CI engine converted to Gaseous Direct Injection
with Compression- and Spark-assisted Ignition (GDI-CSI), running on
hydrogen + HERRSCHER Proprietary Fuel Blend (HPF).

IMPORTANT
---------
* Every number produced here is a MODEL OUTPUT or a stated ASSUMPTION.
  Nothing in this repository is bench data.
* Fuel is represented on a hydrogen-equivalent *energy* basis. Blend composition
  is intentionally not modelled or disclosed.
* In-cylinder pressure traces come from a single-zone first-law model.
  Efficiency / emission maps are parametric (semi-empirical) surfaces whose
  shape and magnitude are set from published H2-DI ranges and are meant to be
  REPLACED by measured data once test-cell results exist.
"""
from dataclasses import dataclass
import numpy as np

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
R_AIR = 287.0            # J/kg/K
LHV_H2 = 120e6           # J/kg  (hydrogen-equivalent energy basis)
E_STOICH_PER_AIR = 3.5e6 # J per kg air at lambda = 1 (hydrogen-equivalent)
LHV_DIESEL = 42.5e6      # J/kg
E_STOICH_DIESEL = 2.93e6 # J per kg air at lambda = 1 (diesel, AFR 14.5)


@dataclass
class Engine:
    """Generic 6-cylinder, 5.64 L HCV-class turbo-diesel donor (assumed)."""
    bore: float = 0.102
    stroke: float = 0.115
    conrod: float = 0.190
    ncyl: int = 6
    cr_diesel: float = 17.5
    cr_retro: float = 16.0
    ivc_deg: float = -140.0  # IVC, deg ATDC-compression (40 deg after BDC)

    @property
    def vd_cyl(self):
        return np.pi / 4 * self.bore ** 2 * self.stroke

    @property
    def vd_tot(self):
        return self.vd_cyl * self.ncyl


ENG = Engine()


# ----------------------------------------------------------------------------
# Kinematics / thermodynamics
# ----------------------------------------------------------------------------
def cyl_volume(theta_deg, cr, eng=ENG):
    """Instantaneous cylinder volume [m3]; theta=0 at firing TDC."""
    th = np.radians(theta_deg)
    a = eng.stroke / 2
    R = eng.conrod / a
    vc = eng.vd_cyl / (cr - 1)
    return vc + eng.vd_cyl / 2 * (R + 1 - np.cos(th) - np.sqrt(R ** 2 - np.sin(th) ** 2))


def motored_pressure(theta_deg, p_ivc, cr, n_poly=1.34, eng=ENG):
    v_ivc = cyl_volume(eng.ivc_deg, cr, eng)
    return p_ivc * (v_ivc / cyl_volume(theta_deg, cr, eng)) ** n_poly


def wiebe(theta, soc, dur, a=6.9, m=2.0):
    x = np.zeros_like(theta, dtype=float)
    k = theta > soc
    x[k] = 1 - np.exp(-a * ((theta[k] - soc) / dur) ** (m + 1))
    return x


def single_zone(cr, p_ivc, xb_func, q_total, loss_frac=0.12, eng=ENG,
                th_end=130.0, dth=0.25):
    """First-law single-zone model. Returns theta, p, V, xb, dQ/dtheta."""
    th = np.arange(eng.ivc_deg, th_end + dth, dth)
    V = cyl_volume(th, cr, eng)
    dV = np.gradient(V, th)
    xb = xb_func(th)
    dQ = q_total * (1 - loss_frac) * np.gradient(xb, th)
    p = np.zeros_like(th)
    p[0] = p_ivc
    for i in range(len(th) - 1):
        g = 1.34 - 0.06 * xb[i]
        p[i + 1] = p[i] + ((g - 1) / V[i] * dQ[i] - g * p[i] / V[i] * dV[i]) * dth
    return th, p, V, xb, dQ


def imep_gross(th, p, V):
    return np.trapezoid(p, V) / (V.max() - V.min())


# ----------------------------------------------------------------------------
# Injector (gaseous, solenoid / peak-and-hold class, assumed)
# ----------------------------------------------------------------------------
CD_A = 2.4e-6        # m2 effective flow area (Cd*A), assumed
T_OPEN = 0.18e-3     # s, command-to-flow opening delay (assumed)
T_CLOSE = 0.12e-3    # s, command-end-to-flow-end closing delay (assumed)
MIN_PULSE = 0.25e-3  # s, minimum controllable energising time (assumed)


def gas_mdot(p0, p, cd_a=CD_A, t0=310.0, gam=1.41, r_gas=4124.0):
    """Compressible orifice flow, choked/sub-critical, hydrogen-like gas [kg/s]."""
    pr = np.minimum(p / p0, 1.0)
    crit = (2 / (gam + 1)) ** (gam / (gam - 1))
    ch = np.sqrt(gam / (r_gas * t0)) * (2 / (gam + 1)) ** ((gam + 1) / (2 * (gam - 1)))
    sub = np.sqrt(2 * gam / ((gam - 1) * r_gas * t0) *
                  np.maximum(pr ** (2 / gam) - pr ** ((gam + 1) / gam), 0))
    return cd_a * p0 * np.where(pr <= crit, ch, sub)


# ----------------------------------------------------------------------------
# Baseline diesel and retrofit performance targets
# ----------------------------------------------------------------------------
N_GRID = np.array([800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400])
T_DIESEL = np.array([430, 480, 525, 555, 560, 555, 540, 525, 510.0])
BTE_PEAK_DIESEL = 37.5  # %


def torque_diesel(n):
    return np.interp(n, N_GRID, T_DIESEL)


def gain_torque(n):
    return 0.02 + 0.085 * np.exp(-((np.asarray(n) - 1100) / 600) ** 2)


def torque_retro(n):
    return torque_diesel(n) * (1 + gain_torque(n))


def power_kw(T, n):
    return T * 2 * np.pi * np.asarray(n) / 60 / 1e3


def bmep_bar(T, eng=ENG):
    return 4 * np.pi * T / eng.vd_tot / 1e5


def _fl(l):
    l = np.asarray(l, dtype=float)
    return l / (l + 0.12) * (1 - 0.10 * np.maximum(0, (l - 0.85) / 0.15))


_FL_MAX = float(np.max(_fl(np.linspace(0.05, 1.0, 400))))


def bte_diesel(n, l):
    n = np.asarray(n, dtype=float)
    fn = 1 - 0.08 * ((n - 1500) / 900) ** 2
    return BTE_PEAK_DIESEL * _fl(l) / _FL_MAX * fn


def rel_gain(n, l):
    """Relative BTE improvement of GDI-CSI over diesel at equal absolute torque.
    Functional form is an assumption (target scenario), see docs/ASSUMPTIONS.md."""
    n = np.asarray(n, dtype=float)
    l = np.asarray(l, dtype=float)
    g = (0.180
         + 0.035 * np.exp(-((l - 0.6) / 0.4) ** 2) * np.exp(-((n - 1400) / 800) ** 2)
         - 0.030 * np.clip((n - 2000) / 400, 0, 1) * np.clip((l - 0.8) / 0.2, 0, 1)
         - 0.020 * np.exp(-l / 0.12))
    return g


def bte_retro(n, l):
    return bte_diesel(n, l) * (1 + rel_gain(n, l))


# ----------------------------------------------------------------------------
# Strategy maps (lambda, rail pressure, spark, injection timing)
# ----------------------------------------------------------------------------
LAMBDA_MAX = 6.0


def lambda_target(n, l):
    lam_full = 2.1 + 0.15 * (n - 1500) / 900
    return np.minimum(lam_full * (1.0 / np.maximum(l, 0.05)) ** 0.45, LAMBDA_MAX)


def rail_pressure_bar(n, l):
    return np.clip(60 + 30 * l + 10 * (n - 800) / 1600, 60, 100)


def spark_advance_deg(n, l):
    return 4.0 + 5.0 * (n - 800) / 1600 + 3.0 * (1 - l)


def ca1090_deg(n, lam):
    return 9 + 2.0 * (lam - 2.1) + 1.5 * n / 1000


def nox_diesel(n, l):
    return 4.8 + 2.4 * l + 0.5 * (n - 1500) / 900


def nox_retro(n, l, lam=None, soi_dev_deg=0.0):
    """g/kWh. Thermal peak near lambda~1.4 plus a stratification floor."""
    if lam is None:
        lam = lambda_target(n, l)
    thermal = 18.0 * np.exp(-((np.log(lam / 1.4)) / 0.25) ** 2)
    floor = (0.06 + 0.22 * l) * (1 + 0.02 * soi_dev_deg)
    return thermal + floor


def operating_point(n, l, eng=ENG, dwell_ms=2.2):
    """Full calibration row for one (rpm, load fraction of diesel torque)."""
    T = l * torque_diesel(n)
    bmep = bmep_bar(T) * 1e5
    bte = float(bte_retro(n, l)) / 100
    q_f = bmep * eng.vd_cyl / bte                       # J / cycle / cyl
    m_f = q_f / LHV_H2                                  # kg H2-equivalent
    lam = float(lambda_target(n, l))
    m_air = lam * q_f / E_STOICH_PER_AIR
    v_ivc = cyl_volume(eng.ivc_deg, eng.cr_retro, eng)
    p_ivc_req = m_air * R_AIR * 335.0 / v_ivc
    p_ivc = max(p_ivc_req, 0.80e5)
    lam_act = p_ivc * v_ivc / (R_AIR * 335.0) / (q_f / E_STOICH_PER_AIR)
    p_rail = float(rail_pressure_bar(n, l)) * 1e5
    sa = float(spark_advance_deg(n, l))
    eoi = sa + 5.0                                       # deg BTDC (flow end)
    # integrate backwards from EOI until the required mass is delivered
    dth = 0.25
    th = eoi
    mass = 0.0
    sec_per_deg = 1.0 / (6.0 * n)
    while mass < m_f and th < 120:
        pc = motored_pressure(-th, p_ivc, eng.cr_retro, eng=eng)
        mass += gas_mdot(p_rail, pc) * dth * sec_per_deg
        th += dth
    soi = th
    flow_dur_ms = (soi - eoi) * sec_per_deg * 1e3
    et_ms = max(flow_dur_ms + (T_OPEN - T_CLOSE) * 1e3, MIN_PULSE * 1e3)
    cmd_start = soi + T_OPEN * 6 * n                     # deg BTDC (earlier)
    cmd_end = eoi + T_CLOSE * 6 * n
    p_cyl_soi = float(motored_pressure(-soi, p_ivc, eng.cr_retro, eng=eng))
    p_cyl_eoi = float(motored_pressure(-eoi, p_ivc, eng.cr_retro, eng=eng))
    dwell_start = sa + dwell_ms * 1e-3 * 6 * n
    soc = -sa + 0.4e-3 * 6 * n                           # deg ATDC (ign. delay 0.4 ms)
    return dict(
        rpm=n, load_pct=100 * l, torque_Nm=T, power_kW=float(power_kw(T, n)),
        bmep_bar=bmep / 1e5, lambda_=lam_act, ivc_pressure_bar=p_ivc / 1e5,
        rail_bar=p_rail / 1e5, fuel_mg_cyc_cyl=m_f * 1e6,
        soi_flow_degBTDC=soi, eoi_flow_degBTDC=eoi, flow_dur_deg=soi - eoi,
        flow_dur_ms=flow_dur_ms, cmd_start_degBTDC=cmd_start,
        cmd_end_degBTDC=cmd_end, energising_ms=et_ms,
        p_cyl_at_soi_bar=p_cyl_soi / 1e5, p_cyl_at_eoi_bar=p_cyl_eoi / 1e5,
        pressure_ratio_at_eoi=p_cyl_eoi / p_rail,
        spark_degBTDC=sa, dwell_start_degBTDC=dwell_start, dwell_ms=dwell_ms,
        soc_degATDC=soc, ca10_90_deg=float(ca1090_deg(n, lam_act)),
        bte_diesel_pct=float(bte_diesel(n, l)), bte_retro_pct=float(bte_retro(n, l)),
        bte_gain_pct=100 * float(rel_gain(n, l)),
        nox_diesel_gkWh=float(nox_diesel(n, l)),
        nox_retro_gkWh=float(nox_retro(n, l, lam_act)),
    )


# 9-mode illustrative weighting cycle (equal weights; NOT a certified cycle)
CYCLE = [(1000, .25), (1000, .50), (1500, .25), (1500, .50), (1500, .75),
         (2000, .25), (2000, .50), (2000, .75), (2000, 1.0)]


def cycle_summary():
    W = Qd = Qr = NOxd = NOxr = 0.0
    for n, l in CYCLE:
        P = float(power_kw(l * torque_diesel(n), n))
        W += P
        Qd += P / (float(bte_diesel(n, l)) / 100)
        Qr += P / (float(bte_retro(n, l)) / 100)
        NOxd += P * float(nox_diesel(n, l))
        NOxr += P * float(nox_retro(n, l))
    return dict(bte_diesel=100 * W / Qd, bte_retro=100 * W / Qr,
                bte_gain=100 * (Qd / Qr - 1),
                nox_diesel=NOxd / W, nox_retro=NOxr / W)
