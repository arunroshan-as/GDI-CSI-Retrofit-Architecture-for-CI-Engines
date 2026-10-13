"""Generate all figures, CSV data and summary.json for the GDI-CSI repo.
Run:  python src/generate_results.py
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
import model as m

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "results", "figures")
DAT = os.path.join(ROOT, "data")
os.makedirs(FIG, exist_ok=True)
os.makedirs(DAT, exist_ok=True)

NAVY, GOLD, GREY, RED, TEAL = "#0B1D3A", "#B8912F", "#8A93A3", "#B23A48", "#1F7A8C"
plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 170, "font.size": 9.5,
    "axes.edgecolor": NAVY, "axes.labelcolor": NAVY, "axes.titleweight": "bold",
    "axes.titlecolor": NAVY, "axes.grid": True, "grid.alpha": .25,
    "xtick.color": NAVY, "ytick.color": NAVY, "legend.frameon": False,
})
WM = "Simulation-based preliminary result - not bench data"


def save(fig, name, wm=True):
    if wm:
        fig.text(0.995, 0.005, WM, ha="right", va="bottom", fontsize=6.5, color=GREY, style="italic")
    fig.savefig(os.path.join(FIG, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Calibration table
# ---------------------------------------------------------------------------
LOADS = [0.1, 0.25, 0.5, 0.75, 1.0]
rows = [m.operating_point(n, l) for n in m.N_GRID for l in LOADS]
cal = pd.DataFrame(rows)
cal.round(3).to_csv(os.path.join(DAT, "gdi_csi_calibration_map.csv"), index=False)

# fine grids for maps
NG = np.linspace(800, 2400, 33)
LG = np.linspace(0.1, 1.0, 28)
NN, LL = np.meshgrid(NG, LG)
fine = pd.DataFrame([m.operating_point(n, l) for l in LG for n in NG])
SOI = fine.soi_flow_degBTDC.values.reshape(NN.shape)
EOI = fine.eoi_flow_degBTDC.values.reshape(NN.shape)
SPK = fine.spark_degBTDC.values.reshape(NN.shape)
RAIL = fine.rail_bar.values.reshape(NN.shape)
LAM = fine.lambda_.values.reshape(NN.shape)
IVC = fine.ivc_pressure_bar.values.reshape(NN.shape)
DUR = fine.flow_dur_ms.values.reshape(NN.shape)
BD, BR, GN = m.bte_diesel(NN, LL), m.bte_retro(NN, LL), m.rel_gain(NN, LL) * 100

# performance curves
nn = np.linspace(800, 2400, 81)
Td, Tr = m.torque_diesel(nn), m.torque_retro(nn)
Pd, Pr = m.power_kw(Td, nn), m.power_kw(Tr, nn)
pd.DataFrame(dict(rpm=nn, torque_diesel_Nm=Td, torque_retro_Nm=Tr, power_diesel_kW=Pd,
                  power_retro_kW=Pr)).round(2).to_csv(os.path.join(DAT, "performance_curves.csv"), index=False)

# ---------------------------------------------------------------------------
# Fig 01 - architecture: baseline vs retrofit
# ---------------------------------------------------------------------------
def box(ax, x, y, w, h, txt, fc="#EEF1F6", ec=NAVY, tc=NAVY, fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, c=NAVY):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, color=c, lw=1.2))


fig, ax = plt.subplots(figsize=(11.5, 6.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 6.6); ax.axis("off")
ax.text(0.1, 6.35, "A  Donor CI engine (as delivered)", fontsize=11, fontweight="bold", color=NAVY)
xs = [0.1, 2.5, 4.9, 7.3]
for x, t in zip(xs, ["Diesel tank\n+ filter", "High-pressure\npump", "Diesel common\nrail", "Diesel injector\n(CRDi)"]):
    box(ax, x, 4.6, 2.0, 1.1, t)
for i in range(3):
    arrow(ax, xs[i] + 2.0, 5.15, xs[i + 1], 5.15)
box(ax, 9.7, 4.6, 2.2, 1.1, "Diesel head\nCR 17.5:1\nglow plug / none", fc="#E3E6EB")
arrow(ax, 9.3, 5.15, 9.7, 5.15)
ax.text(0.1, 3.95, "B  GDI-CSI retrofit (this work)", fontsize=11, fontweight="bold", color=GOLD)
g = "#FBF3DC"
bx = [0.1, 2.5, 4.9, 7.3]
for x, t in zip(bx, ["H2 + HPF storage\n(rated vessels)", "Pressure regulation\n+ check valve", "Gas common\nrail (regulated)", "GDI injector\n(gaseous CRDi-type)"]):
    box(ax, x, 2.35, 2.0, 1.1, t, fc=g, ec=GOLD, bold=True)
for i in range(3):
    arrow(ax, bx[i] + 2.0, 2.9, bx[i + 1], 2.9, c=GOLD)
box(ax, 9.7, 2.35, 2.2, 1.1, "New retrofit head\nCR ~16:1, GDI-CSI\nquench geometry", fc=g, ec=GOLD, bold=True)
arrow(ax, 9.3, 2.9, 9.7, 2.9, c=GOLD)
box(ax, 9.7, 0.85, 2.2, 1.0, "Iridium H2 plug\n+ coil (CSI)", fc=g, ec=GOLD, bold=True)
arrow(ax, 10.8, 1.85, 10.8, 2.35, c=GOLD)
box(ax, 3.6, 0.35, 4.6, 1.2, "Retrofit ECU\ninjector driver  |  coil driver\nsafety layers L0-L4", fc=NAVY, ec=NAVY, tc="white", bold=True)
box(ax, 0.1, 0.35, 3.0, 1.2, "CKP (60-2) + CAM,\nMAP / IAT, rail P/T,\nH2 leak, knock, lambda", fc="#EEF1F6")
arrow(ax, 3.1, 0.95, 3.6, 0.95)
arrow(ax, 8.2, 1.25, 9.7, 1.3, c=GOLD)
arrow(ax, 8.2, 1.45, 8.2, 2.35, c=GOLD)
ax.text(8.5, 0.35, "Gold = new / replaced. Block, crank train,\nturbo and exhaust retained.", fontsize=8, color=GREY)
ax.set_title("Retrofit architecture - CI engine to GDI-CSI hydrogen + proprietary-fuel operation", loc="left")
save(fig, "01_retrofit_architecture.png")

# ---------------------------------------------------------------------------
# Fig 02 - head cross-section schematic
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 6.2))
ax.set_xlim(-6, 6); ax.set_ylim(-1, 11); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((-5, 0), 10, 4.2, fc="#D9DEE6", ec=NAVY))            # head
ax.add_patch(Rectangle((-4.0, -0.0), 8, 0.0, fc="none"))
ax.add_patch(Rectangle((-4.0, -1), 8, 1.6, fc="#C9CFD9", ec=NAVY))         # piston crown
ax.add_patch(Rectangle((-2.2, -0.2), 4.4, 0.8, fc="white", ec=NAVY))       # bowl
# injector (offset, angled)
ax.add_patch(Rectangle((-2.6, 0.5), 1.0, 8.8, angle=8, fc=GOLD, ec=NAVY, alpha=.9))
ax.text(-3.3, 9.7, "GDI injector\n(gaseous CRDi-type)", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
# spark plug angled
ax.add_patch(Rectangle((1.6, 0.4), 0.9, 8.4, angle=-14, fc="#F6F0DF", ec=NAVY))
ax.text(3.3, 9.5, "Iridium H2\nspark plug", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
# jet plume
for a in np.linspace(-0.4, 0.4, 5):
    ax.annotate("", xy=(-1.5 + 3.4 * a, -0.15), xytext=(-2.1, 0.55),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.1))
ax.text(-4.1, 1.3, "H2 + HPF jet", color=TEAL, fontsize=8.5)
ax.plot([0.6], [0.4], marker="*", ms=14, color=RED)
ax.text(0.9, -0.55, "spark kernel", color=RED, fontsize=8.5)
ax.text(0, 2.2, "Replacement head - CR ~16:1", ha="center", fontsize=9, color=NAVY)
ax.text(0, -0.9, "Piston with re-profiled bowl", ha="center", fontsize=8, color=NAVY)
ax.set_title("Head layout concept (schematic)", loc="left")
save(fig, "02_head_layout_schematic.png")

# ---------------------------------------------------------------------------
# Fig 03 - pressure & HRR (single-zone) at 1400 rpm / 100 %
# ---------------------------------------------------------------------------
n0 = 1400
opr = m.operating_point(n0, 1.0)
cr_r, cr_d = m.ENG.cr_retro, m.ENG.cr_diesel
q_r = opr["bmep_bar"] * 1e5 * m.ENG.vd_cyl / (opr["bte_retro_pct"] / 100)
sa, soc_r = opr["spark_degBTDC"], opr["soc_degATDC"]
dur_r = opr["ca10_90_deg"] / 0.445
th, p_r, V_r, xb_r, dQ_r = m.single_zone(cr_r, opr["ivc_pressure_bar"] * 1e5,
                                          lambda t: m.wiebe(t, soc_r, dur_r, m=2.0), q_r * 0.98)
# diesel at same absolute torque
q_d = opr["bmep_bar"] * 1e5 * m.ENG.vd_cyl / (opr["bte_diesel_pct"] / 100)
m_air_d = 1.55 * q_d / m.E_STOICH_DIESEL
p_ivc_d = m_air_d * m.R_AIR * 335 / m.cyl_volume(m.ENG.ivc_deg, cr_d)
soc_d = -3.0
th_d, p_d, V_d, xb_d, dQ_d = m.single_zone(
    cr_d, p_ivc_d,
    lambda t: 0.30 * m.wiebe(t, soc_d, 12, a=6.9, m=1.0) + 0.70 * m.wiebe(t, soc_d + 2, 48, a=6.9, m=1.2),
    q_d * 0.98)
p_mot = m.motored_pressure(th, opr["ivc_pressure_bar"] * 1e5, cr_r)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True, gridspec_kw=dict(height_ratios=[2, 1.2]))
a1.plot(th, p_d / 1e5, color=GREY, lw=2, label=f"Baseline diesel (CR {cr_d}, lambda~1.55)")
a1.plot(th, p_r / 1e5, color=GOLD, lw=2.2, label=f"GDI-CSI retrofit (CR {cr_r}, lambda {opr['lambda_']:.2f})")
a1.plot(th, p_mot / 1e5, color=NAVY, lw=1, ls="--", label="Motored (retrofit)")
a1.axvspan(-opr["soi_flow_degBTDC"], -opr["eoi_flow_degBTDC"], color=TEAL, alpha=.18, label="H2+HPF injection window")
a1.axvline(-sa, color=RED, ls=":", lw=1.4, label=f"Spark {sa:.1f} deg BTDC")
a1.set_ylabel("Cylinder pressure [bar]"); a1.set_xlim(-60, 100); a1.set_ylim(0, None)
a1.set_title(f"Cylinder pressure and heat-release comparison - {n0} rpm, {opr['bmep_bar']:.1f} bar BMEP (full diesel torque)", loc="left")
a1.legend(loc="upper right", fontsize=8)
a2.plot(th, dQ_d / np.max(dQ_d) * np.max(dQ_d) / (q_d * 0.88) * 100, color=GREY, lw=2, label="Diesel")
a2.plot(th, dQ_r / (q_r * 0.88) * 100, color=GOLD, lw=2.2, label="GDI-CSI")
a2.axvline(-sa, color=RED, ls=":", lw=1.4)
a2.set_ylabel("Net HRR [% / deg]"); a2.set_xlabel("Crank angle [deg ATDC]"); a2.legend(fontsize=8)
save(fig, "03_pressure_and_heat_release.png")
pk = dict(peak_p_diesel=float(p_d.max() / 1e5), peak_p_retro=float(p_r.max() / 1e5),
          peak_p_theta_retro=float(th[np.argmax(p_r)]), peak_p_theta_diesel=float(th[np.argmax(p_d)]),
          maxdpdtheta_retro=float(np.max(np.gradient(p_r, th)) / 1e5),
          maxdpdtheta_diesel=float(np.max(np.gradient(p_d, th)) / 1e5))

# ---------------------------------------------------------------------------
# Fig 04 - 720 deg timing diagram (events) at 1500 rpm / 75 %
# ---------------------------------------------------------------------------
o4 = m.operating_point(1500, 0.75)
fig, ax = plt.subplots(figsize=(11, 5.4))
ax.set_xlim(-360, 360); ax.set_ylim(0, 8)
strokes = [(-360, -180, "1st: INTAKE", "#EAF2F4"), (-180, 0, "2nd: COMPRESSION", "#FBF3DC"),
           (0, 180, "3rd: POWER", "#F8E6E8"), (180, 360, "4th: EXHAUST", "#ECECEF")]
for a, b, t, c in strokes:
    ax.axvspan(a, b, color=c, alpha=.9)
    ax.text((a + b) / 2, 7.5, t, ha="center", fontweight="bold", color=NAVY)
ax.axvline(0, color=NAVY, lw=1.5)
ax.text(2, 0.15, "firing TDC", fontsize=8, color=NAVY)
rowy = {"valves": 6.3, "inj": 5.2, "spark": 4.1, "burn": 3.0, "p": 1.0}
ax.barh(rowy["valves"] + .15, 140, left=-360 + 5, height=.35, color=TEAL, alpha=.8)
ax.barh(rowy["valves"] - .25, 150, left=200, height=.35, color=GREY, alpha=.9)
ax.text(-285, rowy["valves"] + .5, "Intake valve open", fontsize=8, color=TEAL)
ax.text(215, rowy["valves"] - .75, "Exhaust valve open", fontsize=8, color=GREY)
ax.barh(rowy["inj"], o4["soi_flow_degBTDC"] - o4["eoi_flow_degBTDC"], left=-o4["soi_flow_degBTDC"], height=.6, color=GOLD)
ax.annotate(f"Gas injection\nSOI {o4['soi_flow_degBTDC']:.1f}  EOI {o4['eoi_flow_degBTDC']:.1f} deg BTDC",
            xy=(-o4["soi_flow_degBTDC"], rowy["inj"]), xytext=(60, rowy["inj"] + .05), fontsize=8.5, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY))
ax.annotate(f"Spark (CSI) {o4['spark_degBTDC']:.1f} deg BTDC", xy=(-o4["spark_degBTDC"], rowy["spark"]),
            xytext=(60, rowy["spark"]), fontsize=8.5, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
ax.plot([-o4["spark_degBTDC"]], [rowy["spark"]], marker="*", ms=14, color=RED)
ax.barh(rowy["spark"], o4["dwell_start_degBTDC"] - o4["spark_degBTDC"], left=-o4["dwell_start_degBTDC"], height=.25, color=RED, alpha=.4)
ax.barh(rowy["burn"], o4["ca10_90_deg"] / .445, left=o4["soc_degATDC"], height=.5, color="#D98C5F")
ax.text(60, rowy["burn"], f"Combustion (CA10-90 ~{o4['ca10_90_deg']:.0f} deg)", va="center", fontsize=8.5, color=NAVY)
thh = np.linspace(-360, 360, 1441)
thf = np.where(thh >= -180, thh, np.nan)
pm = np.where(thh < -140, 1.0, m.motored_pressure(np.clip(thh, -140, 140), o4["ivc_pressure_bar"] * 1e5, m.ENG.cr_retro) / 1e5)
pm = np.where(thh > 140, np.nan, pm)
ax.plot(thh, 1.0 + pm / pm[~np.isnan(pm)].max() * 1.6, color=NAVY, lw=1.4)
ax.text(-355, 1.15, "Motored pressure (relative)", fontsize=8, color=NAVY)

ins = ax.inset_axes([0.035, 0.30, 0.31, 0.33])
ins.set_xlim(-45, 35); ins.set_ylim(0, 4); ins.set_yticks([]); ins.tick_params(labelsize=7)
ins.barh(3.2, o4["soi_flow_degBTDC"] - o4["eoi_flow_degBTDC"], left=-o4["soi_flow_degBTDC"], height=.6, color=GOLD)
ins.barh(2.2, o4["dwell_start_degBTDC"] - o4["spark_degBTDC"], left=-o4["dwell_start_degBTDC"], height=.3, color=RED, alpha=.4)
ins.plot([-o4["spark_degBTDC"]], [2.2], marker="*", ms=11, color=RED)
ins.barh(1.2, o4["ca10_90_deg"] / .445, left=o4["soc_degATDC"], height=.5, color="#D98C5F")
ins.axvline(0, color=NAVY, lw=1)
ins.text(-44, 3.55, "zoom: injection", fontsize=7, color=NAVY); ins.text(-44, 2.55, "dwell + spark", fontsize=7, color=RED)
ins.text(-44, 1.5, "burn", fontsize=7, color="#A0522D"); ins.set_title("Zoom (-45..+35 deg)", fontsize=7.5, loc="left"); ins.grid(False)
ax.set_yticks([]); ax.set_xticks(np.arange(-360, 361, 60)); ax.set_xlabel("Crank angle [deg] (0 = firing TDC)")
ax.set_title("4-stroke timeline: injection in the late-compression window, then spark assistance - 1500 rpm, 75 % load", loc="left")
ax.grid(False)
save(fig, "04_timing_diagram_720deg.png")

# ---------------------------------------------------------------------------
# Fig 05 - timing maps
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(2, 2, figsize=(11, 8))
for ax, Z, t, cm, lv in [(axs[0, 0], SOI, "Start of injection, SOI [deg BTDC]", "YlOrBr", 14),
                          (axs[0, 1], EOI, "End of injection, EOI [deg BTDC]", "YlGnBu", 12),
                          (axs[1, 0], SPK, "Spark timing [deg BTDC]", "Reds", 12),
                          (axs[1, 1], RAIL, "Gas rail pressure [bar]", "Blues", 12)]:
    cs = ax.contourf(NN, LL * 100, Z, levels=lv, cmap=cm)
    c2 = ax.contour(NN, LL * 100, Z, levels=8, colors=NAVY, linewidths=.5)
    ax.clabel(c2, fmt="%.0f", fontsize=7)
    fig.colorbar(cs, ax=ax)
    ax.set_title(t, loc="left"); ax.set_xlabel("Engine speed [rpm]"); ax.set_ylabel("Load [% of diesel torque]")
fig.suptitle("GDI-CSI reference calibration maps (simulation-derived starting values)", x=.01, ha="left", fontweight="bold", color=NAVY)
fig.tight_layout()
save(fig, "05_timing_and_rail_maps.png")

# ---------------------------------------------------------------------------
# Fig 06 - injection duration / mass / choking
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
for n in [1000, 1600, 2400]:
    sub = cal[cal.rpm == n]
    axs[0].plot(sub.load_pct, sub.fuel_mg_cyc_cyl, marker="o", label=f"{n} rpm")
    axs[1].plot(sub.load_pct, sub.flow_dur_ms, marker="o", label=f"{n} rpm")
    axs[2].plot(sub.load_pct, sub.flow_dur_deg, marker="o", label=f"{n} rpm")
axs[0].set_title("H2-equivalent fuel per cycle per cylinder", loc="left"); axs[0].set_ylabel("mg / cycle")
axs[1].set_title("Injection duration", loc="left"); axs[1].set_ylabel("ms"); axs[1].axhline(m.MIN_PULSE * 1e3, color=RED, ls=":", label="min. pulse")
axs[2].set_title("Injection duration (crank angle)", loc="left"); axs[2].set_ylabel("deg CA")
for a in axs:
    a.set_xlabel("Load [% of diesel torque]"); a.legend(fontsize=8)
save(fig, "06_injection_quantity_and_duration.png")

# ---------------------------------------------------------------------------
# Fig 07 - injector drive waveform + ballistic response
# ---------------------------------------------------------------------------
o7 = m.operating_point(1500, 0.75)
et = o7["energising_ms"]
t = np.linspace(-0.3, et + 0.9, 2000)
i_cmd = np.zeros_like(t)
tp = 0.45
i_cmd[(t >= 0) & (t < tp)] = 14.0
i_cmd[(t >= tp) & (t <= et)] = 6.0
i_cmd = np.where((t > et) & (t < et + 0.15), 6.0 * (1 - (t - et) / 0.15), i_cmd)
needle = np.zeros_like(t)
for k, tk in enumerate(t):
    if tk < m.T_OPEN * 1e3:
        needle[k] = 0
    elif tk < (m.T_OPEN * 1e3 + 0.12):
        needle[k] = (tk - m.T_OPEN * 1e3) / 0.12
    elif tk < et + m.T_CLOSE * 1e3:
        needle[k] = 1
    elif tk < et + m.T_CLOSE * 1e3 + 0.10:
        needle[k] = 1 - (tk - et - m.T_CLOSE * 1e3) / 0.10
fig, axs = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
axs[0].plot(t, i_cmd, color=NAVY, lw=2); axs[0].set_ylabel("Coil current [A]")
axs[0].set_title(f"Injector drive (peak-and-hold) - 1500 rpm, 75 % load, energising {et:.2f} ms", loc="left")
axs[1].plot(t, needle, color=GOLD, lw=2); axs[1].set_ylabel("Needle lift [norm.]")
axs[2].plot(t, needle * (o7["fuel_mg_cyc_cyl"] / o7["flow_dur_ms"]), color=TEAL, lw=2)
axs[2].set_ylabel("Mass flow [mg/ms]"); axs[2].set_xlabel("Time from command start [ms]")
for a in axs:
    a.axvline(0, color=GREY, ls=":"); a.axvline(et, color=GREY, ls=":")
save(fig, "07_injector_drive_waveform.png")

# ---------------------------------------------------------------------------
# Fig 08 - ECU timing (CKP 60-2, CAM, injector, coil)
# ---------------------------------------------------------------------------
o8 = m.operating_point(1500, 0.75)
fig, ax = plt.subplots(figsize=(11.5, 4.8))
x = np.linspace(0, 720, 7201); xs = x - 360
ck = np.zeros_like(x)
for a in np.arange(-360, 360, 6.0):
    ph = (a + 90) % 360          # gap occupies 0..12 deg after the reference position (illustrative)
    if ph >= 12:
        ck[(xs >= a) & (xs < a + 3)] = 1
ax.step(xs, ck * .8 + 6.4, color=NAVY, lw=.9, where="post")
ax.text(-358, 7.35, "CKP: 60-2 wheel (6 deg pitch, 2-tooth gap each rev; gap position illustrative)", fontsize=8.5, color=NAVY)
cam = (xs < 0).astype(float)
ax.step(xs, cam * .8 + 5.0, color=TEAL, lw=1.4, where="post")
ax.text(-358, 5.95, "CAM phase signal (disambiguates compression vs exhaust TDC)", fontsize=8.5, color=TEAL)
inj = ((xs >= -o8["cmd_start_degBTDC"]) & (xs <= -o8["cmd_end_degBTDC"])).astype(float)
ax.step(xs, inj * .8 + 3.6, color=GOLD, lw=2, where="post")
ax.text(-358, 4.55, f"Injector command (start {o8['cmd_start_degBTDC']:.1f}, end {o8['cmd_end_degBTDC']:.1f} deg BTDC)", fontsize=8.5, color=GOLD)
dw = ((xs >= -o8["dwell_start_degBTDC"]) & (xs <= -o8["spark_degBTDC"])).astype(float)
ax.step(xs, dw * .8 + 2.2, color=RED, lw=2, where="post")
ax.plot([-o8["spark_degBTDC"]], [3.1], marker="*", ms=13, color=RED)
ax.text(-358, 3.15, f"Coil dwell {o8['dwell_ms']} ms from {o8['dwell_start_degBTDC']:.1f} deg BTDC; spark {o8['spark_degBTDC']:.1f} deg BTDC", fontsize=8.5, color=RED)
ax.axvline(0, color=NAVY, lw=1.2); ax.axvline(-360, color=GREY, lw=.8, ls=":"); ax.axvline(360, color=GREY, lw=.8, ls=":")
ax.set_xlim(-360, 360); ax.set_ylim(1.7, 7.9); ax.set_yticks([])
ax.set_xlabel("Crank angle [deg] (0 = firing TDC of cylinder 1)")
ax.set_title("ECU interface timing: CKP/CAM synchronisation -> injector and coil scheduling (illustrative, 1500 rpm / 75 %)", loc="left")
ax.grid(False)
save(fig, "08_ecu_ckp_cam_timing.png")

# ---------------------------------------------------------------------------
# Fig 09 - torque / power
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.plot(nn, Td, color=GREY, lw=2, label="Torque - diesel baseline")
ax.plot(nn, Tr, color=GOLD, lw=2.4, label="Torque - GDI-CSI retrofit")
ax.set_ylabel("Torque [Nm]"); ax.set_xlabel("Engine speed [rpm]")
ax2 = ax.twinx(); ax2.grid(False)
ax2.plot(nn, Pd, color=GREY, lw=1.6, ls="--", label="Power - diesel baseline")
ax2.plot(nn, Pr, color=GOLD, lw=1.8, ls="--", label="Power - GDI-CSI retrofit")
ax2.set_ylabel("Power [kW]")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="lower center", ncol=2, fontsize=8)
ax.set_title("Full-load torque and power: low-rpm torque gain from boosted lean DI operation", loc="left")
ax.set_ylim(300, 700)
save(fig, "09_torque_power_curves.png")
ipk = np.argmax(Tr)

# ---------------------------------------------------------------------------
# Fig 10 - BTE vs load
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
ll = np.linspace(0.1, 1.0, 60)
for n, c in [(1000, TEAL), (1500, GOLD), (2000, RED)]:
    axs[0].plot(ll * 100, m.bte_diesel(n, ll), color=c, ls="--", lw=1.4)
    axs[0].plot(ll * 100, m.bte_retro(n, ll), color=c, lw=2.2, label=f"{n} rpm")
    axs[1].plot(ll * 100, m.rel_gain(n, ll) * 100, color=c, lw=2.2, label=f"{n} rpm")
axs[0].set_title("Brake thermal efficiency (dashed = diesel, solid = GDI-CSI)", loc="left")
axs[0].set_ylabel("BTE [%]"); axs[0].legend()
axs[1].axhspan(17, 22, color=GOLD, alpha=.15, label="17-22 % target band")
axs[1].set_title("Relative efficiency gain vs diesel at equal torque", loc="left"); axs[1].set_ylabel("gain [%]"); axs[1].legend()
for a in axs:
    a.set_xlabel("Load [% of diesel torque]")
save(fig, "10_bte_vs_load.png")

# ---------------------------------------------------------------------------
# Fig 11 - BTE maps
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
for ax, Z, t, cm in [(axs[0], BD, "Diesel BTE [%]", "Greys"), (axs[1], BR, "GDI-CSI BTE [%]", "YlOrBr"),
                      (axs[2], GN, "Relative gain [%]", "YlGn")]:
    cs = ax.contourf(NN, LL * 100, Z, levels=14, cmap=cm)
    c2 = ax.contour(NN, LL * 100, Z, levels=8, colors=NAVY, linewidths=.5)
    ax.clabel(c2, fmt="%.1f", fontsize=7); fig.colorbar(cs, ax=ax)
    ax.set_title(t, loc="left"); ax.set_xlabel("Engine speed [rpm]"); ax.set_ylabel("Load [% of diesel torque]")
fig.tight_layout()
save(fig, "11_bte_maps.png")

# ---------------------------------------------------------------------------
# Fig 12 - lambda strategy
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.6))
cs = axs[0].contourf(NN, LL * 100, LAM, levels=14, cmap="viridis")
c2 = axs[0].contour(NN, LL * 100, LAM, levels=[2.5, 3, 4, 5, 6], colors="white", linewidths=.7); axs[0].clabel(c2, fmt="%.1f", fontsize=7)
fig.colorbar(cs, ax=axs[0], label="lambda")
axs[0].set_title("Lean-burn lambda strategy", loc="left"); axs[0].set_xlabel("Engine speed [rpm]"); axs[0].set_ylabel("Load [%]")
cs = axs[1].contourf(NN, LL * 100, IVC, levels=14, cmap="magma")
fig.colorbar(cs, ax=axs[1], label="IVC pressure [bar abs]")
axs[1].set_title("Required charge pressure at IVC (floor = intake restriction)", loc="left"); axs[1].set_xlabel("Engine speed [rpm]")
save(fig, "12_lambda_strategy.png")

# ---------------------------------------------------------------------------
# Fig 13 - NOx vs lambda, SOI trade-off
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
lam = np.linspace(1.2, 6.0, 200)
axs[0].semilogy(lam, m.nox_retro(1500, 0.75, lam), color=GOLD, lw=2.4)
axs[0].axvspan(2.0, 2.4, color=RED, alpha=.12); axs[0].text(2.05, 8, "full-load\nband", fontsize=8, color=RED)
axs[0].axvspan(2.4, 6.0, color=TEAL, alpha=.08); axs[0].text(3.2, 8, "part-load lean band", fontsize=8, color=TEAL)
axs[0].set_xlabel("lambda"); axs[0].set_ylabel("NOx [g/kWh]"); axs[0].set_title("NOx vs lambda", loc="left")
dsoi = np.linspace(-12, 12, 100)  # deg relative to calibrated SOI (+ = earlier)
bte_soi = 100 * (1 - 0.00042 * (dsoi + 0) ** 2) * 1.0
nox_soi = (0.44) * (1 + 0.02 * (-dsoi)) ** 1  # retard (negative) -> more stratified -> more NOx
nox_soi = 0.44 * (1 + 0.035 * np.clip(-dsoi, 0, None)) * (1 + 0.012 * np.clip(dsoi, 0, None))
axs[1].plot(dsoi, bte_soi, color=NAVY, lw=2.2); axs[1].set_ylabel("BTE [% of calibrated optimum]")
axs[1].set_title("SOI sweep: BTE and NOx", loc="left"); axs[1].set_xlabel("SOI shift vs. calibrated [deg] (+ = earlier)")
b = axs[1].twinx(); b.grid(False); b.plot(dsoi, nox_soi, color=RED, lw=2); b.set_ylabel("Cycle NOx [g/kWh]", color=RED)
axs[1].axvspan(-4, 4, color=GOLD, alpha=.15)
axs[1].text(-3.8, 94.3, "calibration\nwindow +/-4 deg", fontsize=8)
axs[1].axvspan(8, 12, color=RED, alpha=.08); axs[1].text(8.3, 94.3, "pre-ignition\nrisk", fontsize=8, color=RED)
cyc = m.cycle_summary()
axs[2].scatter(m.bte_retro(*np.meshgrid([1000, 1500, 2000], [0.25, 0.5, 0.75, 1.0])).ravel(),
               m.nox_retro(*np.meshgrid([1000, 1500, 2000], [0.25, 0.5, 0.75, 1.0])).ravel(), c=GOLD, s=40, edgecolor=NAVY, label="GDI-CSI modes")
axs[2].scatter(m.bte_diesel(*np.meshgrid([1000, 1500, 2000], [0.25, 0.5, 0.75, 1.0])).ravel(),
               m.nox_diesel(*np.meshgrid([1000, 1500, 2000], [0.25, 0.5, 0.75, 1.0])).ravel(), c=GREY, s=40, edgecolor=NAVY, label="Diesel modes")
axs[2].set_yscale("log"); axs[2].set_xlabel("BTE [%]"); axs[2].set_ylabel("NOx [g/kWh]"); axs[2].legend()
axs[2].set_title("BTE - NOx plane (12 modes)", loc="left"); fig.subplots_adjust(wspace=0.5)
save(fig, "13_nox_lambda_soi_tradeoff.png")

# ---------------------------------------------------------------------------
# Fig 14 - emissions, cycle-weighted (+ BS-VI reference lines for NOx)
# ---------------------------------------------------------------------------
em = dict(NOx=(cyc["nox_diesel"], cyc["nox_retro"]), CO=(1.0, 0.18), HC=(0.20, 0.04), PM=(0.040, 0.004))
fig, axs = plt.subplots(1, 4, figsize=(13, 4))
lim = dict(NOx=0.46, CO=4.0, HC=0.16, PM=0.01)
for ax, (k, (dv, rv)) in zip(axs, em.items()):
    ax.bar(["Diesel", "GDI-CSI"], [dv, rv], color=[GREY, GOLD], edgecolor=NAVY)
    ax.axhline(lim[k], color=RED, ls="--", lw=1)
    ax.text(0.5, lim[k], " BS-VI WHSC limit", color=RED, fontsize=7.5, va="bottom", ha="center")
    ax.set_title(f"{k} [g/kWh]", loc="left")
    for i, v in enumerate([dv, rv]):
        ax.text(i, v, f"{v:.3g}", ha="center", va="bottom", fontsize=8)
fig.suptitle("Cycle-weighted emissions (9-mode illustrative cycle) - model estimate; CO/HC/PM are placeholders to be replaced by measurements", x=.01, ha="left", fontsize=10, fontweight="bold", color=NAVY)
save(fig, "14_emissions_comparison.png")

# ---------------------------------------------------------------------------
# Fig 15 - energy balance
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.6))
cats = ["Brake work", "Coolant / wall", "Exhaust enthalpy", "Friction + other"]
dsl, rtr = [m.BTE_PEAK_DIESEL, 23.0, 31.5, 8.0], [float(m.bte_retro(1400, .85)), 19.0, 28.5, 0]
rtr[3] = 100 - sum(rtr[:3])
dsl[3] = 100 - sum(dsl[:3])
cols = [GOLD, TEAL, GREY, "#C7CCD6"]
for j, (name, vals) in enumerate([("Diesel", dsl), ("GDI-CSI", rtr)]):
    bot = 0
    for v, c, cn in zip(vals, cols, cats):
        ax.bar(name, v, bottom=bot, color=c, edgecolor="white", label=cn if j == 0 else None)
        ax.text(j, bot + v / 2, f"{v:.1f}", ha="center", va="center", fontsize=9, color=NAVY)
        bot += v
ax.set_ylabel("% of fuel energy"); ax.legend(loc="center left", bbox_to_anchor=(1, .5))
ax.set_title("Energy balance at best-efficiency point (model split)", loc="left")
save(fig, "15_energy_balance.png")

# ---------------------------------------------------------------------------
# Fig 16 - safety envelope + combustion stability
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
crs = np.linspace(12, 19, 50)
lam_min = 1.5 + 0.10 * (crs - 12)
axs[0].fill_between(crs, 1.0, lam_min, color=RED, alpha=.18, label="pre-ignition / flashback risk")
axs[0].fill_between(crs, 6.5, 8, color=GREY, alpha=.2, label="misfire / lean limit")
axs[0].plot(crs, lam_min, color=RED); axs[0].axhline(6.5, color=GREY)
axs[0].scatter([16.0], [2.1], color=GOLD, s=90, edgecolor=NAVY, zorder=5, label="GDI-CSI full-load point")
axs[0].scatter([16.0], [6.0], color=GOLD, s=90, edgecolor=NAVY, zorder=5, marker="s", label="GDI-CSI light-load point")
axs[0].set_xlabel("Compression ratio"); axs[0].set_ylabel("lambda"); axs[0].set_ylim(1, 8); axs[0].legend(fontsize=7.5, loc="upper right")
axs[0].set_title("Operating envelope (illustrative boundaries)", loc="left")
lam = np.linspace(1.6, 7.5, 200)
cov = 1.4 + 0.25 * np.exp((lam - 5.8) * 1.6) + 0.6 * np.exp(-(lam - 1.6) * 2.5)
axs[1].plot(lam, cov, color=NAVY, lw=2.2); axs[1].axhline(3, color=RED, ls="--"); axs[1].text(1.7, 3.1, "3 % guideline", color=RED, fontsize=8)
axs[1].axvspan(2.0, 6.0, color=GOLD, alpha=.12)
axs[1].set_ylim(0, 8); axs[1].set_xlabel("lambda"); axs[1].set_ylabel("COV of IMEP [%]"); axs[1].set_title("Combustion stability (modelled)", loc="left")
sp = np.linspace(-6, 10, 100)
cov_s = 1.6 + 0.045 * (sp - 2) ** 2
axs[2].plot(sp, cov_s, color=NAVY, lw=2.2); axs[2].axhline(3, color=RED, ls="--")
axs[2].set_xlabel("Spark shift vs. reference [deg] (+ = advance)"); axs[2].set_ylabel("COV of IMEP [%]")
axs[2].set_title("Spark timing sensitivity at lambda 2.5", loc="left")
save(fig, "16_safety_envelope_and_stability.png")

# ---------------------------------------------------------------------------
# Fig 17 - sensitivity: CR and rail pressure
# ---------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
crs = np.linspace(13, 18, 60)
bte_cr = 100 * (1 - 0.0011 * (crs - 16.2) ** 2 - 0.0016 * np.clip(16.5 - crs, 0, None) * 2)
axs[0].plot(crs, bte_cr - bte_cr.max() + 45.0, color=GOLD, lw=2.4)
axs[0].axvline(16, color=NAVY, ls=":"); axs[0].text(16.05, 43.9, "baseline retrofit CR", fontsize=8)
axs[0].set_xlabel("Compression ratio"); axs[0].set_ylabel("Peak BTE [%] (relative sensitivity)")
axs[0].set_title("Compression-ratio sensitivity", loc="left")
pr = np.linspace(40, 140, 80) * 1e5
pcyl = float(m.motored_pressure(-20, 1.76e5, 16.0))
mdot = m.gas_mdot(pr, pcyl)
axs[1].plot(pr / 1e5, 23.64e-6 / mdot * 1e3, color=NAVY, lw=2.4)
axs[1].axvspan(60, 100, color=GOLD, alpha=.15); axs[1].set_xlabel("Rail pressure [bar]"); axs[1].set_ylabel("Injection duration at full load [ms]")
axs[1].set_title("Rail-pressure sensitivity (cylinder pressure at 20 deg BTDC)", loc="left")
save(fig, "17_sensitivity_cr_rail.png")

# ---------------------------------------------------------------------------
# Fig 18 - safety layer stack
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
layers = [("L4  Supervisory", "lambda / load governor, derate, fuel-quality & blend-flag handling", NAVY, "white"),
          ("L3  Combustion limits", "knock / pre-ignition guard, COV monitor, spark & SOI trim bounds", "#2B4570", "white"),
          ("L2  Timing scheduler", "CKP/CAM-synchronised SOI/EOI + spark/dwell from maps; injector ballistics comp.", GOLD, "white"),
          ("L1  Plausibility & limp-home", "sensor range / rationality, rail P/T limits, safe shut-off on fault", "#E7D7A8", NAVY),
          ("L0  Hardware protection", "check valve, quench geometry, H2 leak detection, solenoid shut-off, pressure relief", "#EEF1F6", NAVY)]
for i, (a, b, c, tc) in enumerate(layers):
    y = 5 - i * 1.0
    ax.add_patch(FancyBboxPatch((0.2, y - .45), 9.6, .9, boxstyle="round,pad=0.02,rounding_size=0.1", fc=c, ec=NAVY))
    ax.text(.5, y, a, va="center", fontweight="bold", color=tc, fontsize=10.5)
    ax.text(3.3, y, b, va="center", color=tc, fontsize=8.8)
ax.set_title("Layered control and safety architecture (interface level)", loc="left")
save(fig, "18_safety_layer_stack.png", wm=False)

# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------
full_ret = cal[(cal.load_pct == 100)]
summary = dict(
    engine=dict(displacement_L=m.ENG.vd_tot * 1e3, cylinders=m.ENG.ncyl, bore_mm=m.ENG.bore * 1e3,
                stroke_mm=m.ENG.stroke * 1e3, cr_diesel=m.ENG.cr_diesel, cr_retro=m.ENG.cr_retro),
    torque_diesel_peak=float(Td.max()), torque_retro_peak=float(Tr.max()), torque_retro_peak_rpm=float(nn[ipk]),
    torque_gain_peak_pct=float((Tr.max() / Td.max() - 1) * 100),
    torque_gain_at_1000=float((m.torque_retro(1000) / m.torque_diesel(1000) - 1) * 100),
    power_diesel_rated=float(Pd[-1]), power_retro_rated=float(Pr[-1]),
    power_gain_rated_pct=float((Pr[-1] / Pd[-1] - 1) * 100),
    bte_peak_diesel=float(BD.max()), bte_peak_retro=float(BR.max()),
    gain_min=float(GN.min()), gain_max=float(GN.max()), gain_mean=float(GN.mean()),
    cycle=cyc, pk=pk,
    soi_range=[float(cal.soi_flow_degBTDC.min()), float(cal.soi_flow_degBTDC.max())],
    eoi_range=[float(cal.eoi_flow_degBTDC.min()), float(cal.eoi_flow_degBTDC.max())],
    spark_range=[float(cal.spark_degBTDC.min()), float(cal.spark_degBTDC.max())],
    rail_range=[float(cal.rail_bar.min()), float(cal.rail_bar.max())],
    lambda_range=[float(cal.lambda_.min()), float(cal.lambda_.max())],
    dur_ms_range=[float(cal.flow_dur_ms.min()), float(cal.flow_dur_ms.max())],
    fuel_mg_range=[float(cal.fuel_mg_cyc_cyl.min()), float(cal.fuel_mg_cyc_cyl.max())],
    full_load_nox_range=[float(full_ret.nox_retro_gkWh.min()), float(full_ret.nox_retro_gkWh.max())],
)
with open(os.path.join(DAT, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
