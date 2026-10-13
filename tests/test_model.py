"""Sanity tests for the GDI-CSI reduced-order model (physics and consistency checks)."""
import numpy as np
import pytest
import model as m


def test_volume_at_tdc_and_bdc():
    cr = 16.0
    vc = m.ENG.vd_cyl / (cr - 1)
    assert m.cyl_volume(0.0, cr) == pytest.approx(vc, rel=1e-9)
    assert m.cyl_volume(180.0, cr) == pytest.approx(vc + m.ENG.vd_cyl, rel=1e-9)


def test_displacement():
    assert m.ENG.vd_tot * 1e3 == pytest.approx(5.64, abs=0.01)


def test_choked_flow_scales_with_rail_pressure():
    low = m.gas_mdot(60e5, 10e5)
    high = m.gas_mdot(120e5, 10e5)
    assert high / low == pytest.approx(2.0, rel=1e-6)


def test_flow_drops_when_unchoked_and_stops_at_equal_pressure():
    assert m.gas_mdot(80e5, 70e5) < m.gas_mdot(80e5, 20e5)
    assert m.gas_mdot(80e5, 80e5) == pytest.approx(0.0, abs=1e-12)


def test_motored_pressure_peaks_at_tdc():
    th = np.linspace(-60, 60, 241)
    p = m.motored_pressure(th, 1.7e5, 16.0)
    assert abs(th[np.argmax(p)]) < 0.6


def test_single_zone_energy_release_raises_pressure():
    q = 2500.0
    th, p, V, xb, dQ = m.single_zone(16.0, 1.7e5, lambda t: m.wiebe(t, -3, 26), q)
    pm = m.motored_pressure(th, 1.7e5, 16.0)
    assert p.max() > pm.max() * 1.3
    assert xb[-1] > 0.99


@pytest.mark.parametrize("n", [800, 1400, 2400])
@pytest.mark.parametrize("l", [0.1, 0.5, 1.0])
def test_operating_point_consistency(n, l):
    r = m.operating_point(n, l)
    assert r["soi_flow_degBTDC"] > r["eoi_flow_degBTDC"] > 0
    assert r["eoi_flow_degBTDC"] - r["spark_degBTDC"] == pytest.approx(5.0)
    assert 60 <= r["rail_bar"] <= 100
    assert r["lambda_"] > 1.9
    assert r["energising_ms"] >= m.MIN_PULSE * 1e3
    assert r["cmd_start_degBTDC"] > r["soi_flow_degBTDC"]


def test_torque_and_power_targets():
    n = np.array(m.N_GRID, dtype=float)
    assert np.all(m.torque_retro(n) > m.torque_diesel(n))
    assert m.power_kw(m.torque_diesel(2400), 2400) == pytest.approx(128.2, abs=0.5)


def test_efficiency_gain_inside_target_band_on_cycle():
    c = m.cycle_summary()
    assert 17.0 <= c["bte_gain"] <= 22.0
    assert c["nox_retro"] < c["nox_diesel"] * 0.2


def test_peak_bte_is_physically_bounded():
    n, l = np.meshgrid(m.N_GRID, np.linspace(0.1, 1, 10))
    assert m.bte_retro(n, l).max() < 47.0
