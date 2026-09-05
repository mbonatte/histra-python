# Article Models: Python vs C# verification

Warning tolerances are unchanged: force absolute `1e-3`, force relative `1e-5`, active-residual L2 `1e-4`.

| Mode | Model | Steps | Unsafe | Max reaction error (kN) | Max model-point error (mm) | C# parity |
|---|---|---:|---:|---:|---:|---|
| strict | Bridge_3.1_Coarse | 13/1065 | 0 | 80.6407 | 0.593964 | NOT RELEASE-READY |

`strict` uses ForceMoment with Standard Bisection on every nonlinear stage, uses consistent ArcLength line-search projections, and tightens, never loosens, the HRX convergence tolerance to the unchanged audit limit.

## Article source data

PASS
