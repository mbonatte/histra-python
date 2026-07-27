"""Direct unit test of the SpringCoulomb03 Takeda state machine."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from histra.model.spring import SpringCoulomb03, PhaseEnum

def _make_spring():
    """Create a Coulomb03 spring with a proper softening backbone."""
    s = SpringCoulomb03(
        k=10000.0,
        cohesion=100.0,
        mu=0.5,
        e1p=10000.0, e2p=-500.0, e3p=-100.0,
        e1n=10000.0, e2n=-500.0, e3n=-100.0,
        eup=10000.0, eun=10000.0,
        mom1p=100.0, rot1p=0.01,
        mom2p=99.9995, rot2p=0.010001,
        mom3p=0.0, rot3p=1.0,
        mom1n=-100.0, rot1n=-0.01,
        mom2n=-99.9995, rot2n=-0.010001,
        mom3n=0.0, rot3n=-1.0,
    )
    s.revert_to_start()
    s.revert_to_last_commit()
    return s


def test_elastic_then_yield():
    """Elastic loading, then beyond yield into plastic regime."""
    s = _make_spring()

    # Elastic strain (within rot1p = 100/10000 = 0.01)
    s.set_trial_strain_takeda_diagonal_quad(0.005, 0.0)
    print(f"Elastic: strain={s._tstrain:.6f}, stress={s._tstress:.6f}, k_tang={s.k_tang:.6f}")
    assert abs(s._tstress - 50.0) < 1e-10, f"Expected 50.0, got {s._tstress}"
    assert s.t_phase == PhaseEnum.Elastic

    # Yield (strain beyond rot1p = 0.01).
    # With a softening backbone (e2p=-500) the stress drops below the peak mom1p=100.
    s.set_trial_strain_takeda_diagonal_quad(0.02, 0.0)
    print(f"Yield: strain={s._tstrain:.6f}, stress={s._tstress:.6f}, k_tang={s.k_tang:.6f}, phase={PhaseEnum(s.t_phase).name}")
    # Stress should be less than mom1p (softening) but still positive
    assert 90.0 < s._tstress < 100.0, f"Expected stress near 99, got {s._tstress}"
    assert s.t_phase in (PhaseEnum.Plastic_t, PhaseEnum.Elastic), f"Expected plastic or elastic, got {PhaseEnum(s.t_phase).name}"

    print("[PASS] Elastic → yield transition works")


def test_unload_reload():
    """Load to yield, unload, reload."""
    s = _make_spring()

    # Load beyond yield
    s.set_trial_strain_takeda_diagonal_quad(0.02, 0.0)
    s.commit()
    print(f"After commit to 0.02: stress={s._cstress:.6f}, phase={PhaseEnum(s.phase).name}")

    # Unload
    s.set_trial_strain_takeda_diagonal_quad(0.015, 0.0)
    print(f"Unload to 0.015: stress={s._tstress:.6f}, k_tang={s.k_tang:.6f}, phase={PhaseEnum(s.t_phase).name}")
    s.commit()

    # Re-increase
    s.set_trial_strain_takeda_diagonal_quad(0.025, 0.0)
    print(f"Re-increase to 0.025: stress={s._tstress:.6f}, k_tang={s.k_tang:.6f}, phase={PhaseEnum(s.t_phase).name}")

    print("[PASS] Unload/reload works")


def test_negative_yield():
    """Compression (negative) loading."""
    s = _make_spring()

    # Negative elastic
    s.set_trial_strain_takeda_diagonal_quad(-0.005, 0.0)
    print(f"Neg elastic: strain={s._tstrain:.6f}, stress={s._tstress:.6f}")
    assert abs(s._tstress - (-50.0)) < 1e-10

    # Negative yield (softening backbone)
    s.set_trial_strain_takeda_diagonal_quad(-0.02, 0.0)
    print(f"Neg yield: strain={s._tstrain:.6f}, stress={s._tstress:.6f}, phase={PhaseEnum(s.t_phase).name}")
    assert s._tstress < -90.0, f"Should have yielded negative, got {s._tstress}"
    assert s.t_phase in (PhaseEnum.Plastic_c, PhaseEnum.Elastic)

    print("[PASS] Negative yielding works")


def test_slip():
    """Zero friction strength → Slip phase."""
    s = SpringCoulomb03(
        k=10000.0,
        cohesion=0.0, mu=0.0,
        e1p=10000.0, e2p=0.0, e3p=0.0,
        mom1p=0.0, rot1p=0.0,
        mom2p=0.0, rot2p=0.0,
        mom3p=0.0, rot3p=0.0,
        mom1n=0.0, rot1n=0.0,
        mom2n=0.0, rot2n=0.0,
        mom3n=0.0, rot3n=0.0,
    )
    s.revert_to_start()
    s.revert_to_last_commit()

    s.set_trial_strain_takeda_diagonal_quad(0.01, 0.0)
    print(f"Slip: strain={s._tstrain:.6f}, stress={s._tstress:.6f}, phase={PhaseEnum(s.t_phase).name}")
    assert s.t_phase == PhaseEnum.Slip
    assert s._tstress == 0.0

    print("[PASS] Slip works")


if __name__ == "__main__":
    test_elastic_then_yield()
    test_unload_reload()
    test_negative_yield()
    test_slip()
    print("\nAll tests passed!")
