# Nonlinear convergence and equilibrium safety

## Why the wall result was accepted

The original C# solver applies exactly one convergence test selected by
`AdapticConvergenceCriteria`. For `Work`, its source code evaluates:

```text
0.5 * abs(last_displacement_correction dot current_residual) <= tolerance
```

This is an incremental-work test, not a force-equilibrium test. If the latest
Newton/line-search correction becomes small or nearly orthogonal to the
residual, their scalar product can be small while the residual itself remains
large.

That is precisely what happened at `wall_6_rows_run`, `LiveLoad_1`, step 1:

```text
selected Work error             = 0.004716  <= 0.005 (accepted)
active-DOF residual L2 norm     = 32.078
applied live load               = 107.978 kN
expected ReactionSum R3         = -220.223161 kN
actual ReactionSum R3           = -312.352361 kN
global vertical balance error   = -92.129200 kN
```

The small Work value says only that the last correction performed little
incremental work against the residual. It does not say that the structure is
in equilibrium. The large support reaction is therefore not valid capacity.

## Available HiStrA criteria and units

HiStrA models in this repository use kN and cm. The C# implementation uses
absolute, unnormalised measures:

| `.HRX` value | C# expression | Value represented by `ConvergenceTolerance` |
|---|---|---|
| `ForceMoment` | `L2(residual)` | A mixed norm containing translational forces (kN), rotational moments (kN·cm), and DMEM generalized-force components. It is not dimensionally a single pure force unit. |
| `DispRotation` | `L2(last correction)` | A mixed norm containing translations (cm), rotations (radians), and DMEM internal generalized displacements. |
| `Work` | `0.5 * abs(correction dot residual)` | Incremental work in kN·cm; `1 kN·cm = 10 J`. |

`RelativeWork` exists in the serialized C# enum, but the C#
`EquiSolnAlgo` factory has no branch that constructs a test for it. It is not
a usable fourth criterion. Python now rejects it explicitly instead of
silently interpreting it as another criterion.

The C# `Analysis` object also serializes fields named
`ConvergenceToleranceForce`, `ConvergenceToleranceMoment`,
`ConvergenceToleranceDisplacement`, `ConvergenceToleranceRotation`, and
`WorkReference`. They are exposed by parts of the UI, but the actual static
solver factory shown in the supplied C# source does not pass those values to
the convergence tests. It passes only the one scalar `ConvergenceTolerance`.
Therefore, a value such as `0.005` is not a percentage and is not automatically
scaled by the applied load.

## Python's independent equilibrium audit

Python keeps the selected C# convergence test so reference comparisons remain
possible, but it no longer treats that test alone as proof of engineering
equilibrium. Before every candidate step is committed, it independently checks:

1. global force balance in X, Y, and Z, in kN;
2. the full active generalized residual L2 norm, even when the selected test is
   `Work` or `DispRotation`.

The expected reaction is calculated from the reaction at the beginning of the
analysis plus the physical analysis-load resultant multiplied by the load
factor increment. This works for chained scour/live analyses because the
predecessor reaction is retained as the baseline.

The default global-force limit is:

```text
0.001 kN + 1e-5 * max(||actual reaction||, ||expected reaction||, 1 kN)
```

The default independent residual limit is the `.HRX`
`ConvergenceTolerance`. Both values can be overridden explicitly.

Every checked step contains:

- `equilibrium_ok`;
- `equilibrium_force_ok` and `equilibrium_residual_ok`;
- expected reactions and X/Y/Z force-balance errors in kN;
- absolute and relative force limits;
- residual L2/max values and the residual limit.

### Warning mode (default, C# comparison)

```python
code, steps = solve_static_nonlinear(model, analysis)
```

The first unsafe step raises `UnsafeEquilibriumWarning`; every unsafe step is
also logged and marked in its result dictionary. The numerical path is not
changed. Such a step must not be used for engineering interpretation even
though its legacy status remains committed for C# parity.

The low-level solver and `AnalysisSession` use warning mode by default because
they are also used for exact C# regression work. The production-oriented
`run_python_solver_job` API defaults to strict/error mode and will not project
an unsafe analysis as a successful backend result.

### Strict mode (recommended for engineering runs)

```python
code, steps = solve_static_nonlinear(
    model,
    analysis,
    equilibrium_policy="error",
)
```

or for a chain:

```python
session = AnalysisSession(model, equilibrium_policy="error")
```

Strict mode restores the complete pre-step state, does not commit the unsafe
candidate, and returns exit code `-12`. The analysis outcome is classified as
nonconverged. This is the recommended mode for capacity calculations.

## Scenario-based strategy guidance

No method is universally fastest or most robust. A configuration qualifies for
recommendation only after it (1) reaches safe equilibrium, (2) preserves the
accepted response, and (3) completes the relevant reference range. Runtime and
factorization count break ties only among qualifying configurations.

| Scenario | Starting configuration | Required verification |
|---|---|---|
| Gravity or seating, `LoadControl` | `ForceMoment` with `StandardBisectionLineSearch` is the measured starting point for the coarse Article model. | The five-step gravity matrix completed safely; requalify on the representative mesh. |
| Monotonic live-load pushover, `ArcLength` | `ForceMoment`; start the model-specific matrix with `StandardBisectionLineSearch`. | It is the only qualifier over the measured first five coarse-model increments; the full peak/range gate remains mandatory. |
| Displacement-controlled near-collapse | `ForceMoment` with strict equilibrium; retain cutbacks and the authored displacement controller. | Covers the reference peak/displacement range without an unsafe commit. |
| P-Delta | Start from the non-P-Delta qualifying strategy, then test `EachStep` and `EachIteration` as distinct scenarios. | Equilibrium, response preservation, and expected geometric-stiffness update frequency. |
| C# path reproduction | Preserve the complete authored configuration and use warning mode. | Treat unsafe rows as compatibility evidence only, never production capacity. |

`Work` and `DispRotation` are supported compatibility criteria. Because either
can pass while the force residual is too large, the advisor emits
`HISTRA-STRATEGY-001`; use strict equilibrium for production. An ArcLength stage
using a modified tangent receives `HISTRA-STRATEGY-002`, reflecting observed
stall/slower behavior on current nonlinear live-load cases. `HISTRA-STRATEGY-003`
marks a ForceMoment ArcLength method that is not the currently measured
Standard Bisection starting point. Both are prompts for a model-specific full-
range benchmark, not claims that one method wins for every model.

```python
from histra import AnalysisSession, inspect_solver_strategy

report = inspect_solver_strategy(model, ["Vert", "LiveLoad"])
session = AnalysisSession(
    model,
    equilibrium_policy="error",
    strategy_policy="warn",  # use "off" only for controlled comparisons
    on_log=print,
)
```

Warnings are emitted once per analysis/configuration, contain a stable code and
the selected configuration, and never mutate the HRX. The reproducible strategy
benchmark matrix and measured results are release artifacts; until that matrix
passes, the table above is qualified guidance rather than a release claim.
