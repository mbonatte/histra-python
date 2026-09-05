# Bridge 3.1 Coarse: C# / Python difference root cause

Recorded 2026-09-05 from the user-supplied
`Bridge_3.1_Coarse.hrx` and `Bridge_3.1_Coarse.Results` pair.

## Finding

The premature Python termination at live-load step 42 was caused by a Python
continuation-policy mismatch, not by load assembly or the masonry
constitutive laws.

The HRX load function for analysis 23 contains the multiplier sequence
`0.0 -> 0.2 -> 5.0`. With target displacement `0.6000000238 cm`, the first
segment ends at relative control displacement `0.1200000048 cm`. Both C# and
Python cross that boundary at committed step 41.

At a load-function segment boundary, C# calls `UpdateK` only when the analysis
method name contains `Modified`. Analysis 23 uses
`StandardInitialInterpolatedLineSearch`, but Python previously called
`integrator.update_k(...)` unconditionally. That replaced the matrix retained
by the Standard solution algorithm immediately before the next ArcLength
predictor. Python then selected a different continuation branch at step 42,
grew the element displacement beyond the configured limit, and stopped after
only 41 of the 1,060 live-load steps.

Python now applies the same conditional refresh policy as C# in both committed-
step executors. Regression tests cover Standard and Modified method names.

## Direct state evidence before the correction

- Authored gravity step 1 matched the C# committed state to numerical storage
  precision: identical spring identities and phases, maximum interface
  displacement difference `3.92e-08 cm`, maximum Quad displacement difference
  `1.79e-08 cm`, and maximum spring-stress difference `7.87e-05`.
- Authored live-load step 41 still had identical spring phases. Maximum
  interface displacement difference was `6.08e-05 cm`, and the reaction
  difference was approximately `0.024 kN`.
- The first step-42 Python correction changed the accumulated load increment
  from the `+10` predictor to `-18.883`, while C# continued along the same
  positive response branch. This is the first material divergence.

## Verification after the correction

The focused authored rerun completed all stored rows:

| Metric | Corrected Python / C# result |
|---|---:|
| Dependency-chain steps | `1,065 / 1,065` |
| Live-load steps | `1,060 / 1,060` |
| Peak-load relative error | `0.0213%` |
| Normalized curve RMSE | `0.0708%` |
| Curve-area relative error | `0.0295%` |
| Initial-stiffness relative error | `0.00221%` |
| Peak-displacement error | `0.02795 mm` |
| Maximum pointwise reaction error | `3.31702 kN` at live step 686 |
| Maximum model-point error | `0.00980 mm` |

The complete response satisfies the branch-insensitive curve tolerances in the
Article release plan. The exact pointwise `0.1 kN` target is not met because
the authored Work criterion commits non-equilibrated states and small
floating-point/backend differences change unloading/reloading classifications
over the long path.

All `1,065` authored commits fail the independent active-DOF residual audit.
Consequently this run is C# compatibility evidence, not production-safe
equilibrium evidence. The strict run remains a separate mandatory gate.

## Spring-state interpretation

Gravity phase distributions are exact at all five steps. Live-load phase
counts first differ by one spring at step 1, return to exact agreement at
intermittent steps through step 216, and then accumulate differences mainly
between `Unload_c`/`Reload_c` and `Unload_t`/`Reload_t`. At step 1,060 there are
1,937 phase-identity differences, but there are zero rupture-identity
differences: the 136 tension-rupture and 55 compression-rupture springs are the
same physical springs in both results. Thus failure localization agrees; the
remaining mismatch is the reversible hysteretic branch label on an unsafe,
loosely converged authored path.

## Reproducibility

Inputs are pinned by the hashes recorded in
`BRIDGE_3.1_COARSE_CSHARP_RESULTS_AUDIT.md`. The corrected focused run used
HiStrA Python `1.0.0`, Python `3.12.3`, NumPy `2.5.2`, SciPy `1.18.1`, and
Numba `0.67.0` on 64-bit Linux. The full test suite passed with `576 passed,
5 skipped, 21 warnings`; the warning increase is explained by the existing
equilibrium and strategy warnings, not a new numerical warning class.
