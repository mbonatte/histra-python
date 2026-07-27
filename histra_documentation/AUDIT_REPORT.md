# Final audit report

## Scope

The audit used all supplied material:

- the complete Python package;
- the focused original C# source tree;
- existing unit and integration tests;
- `model-output/model.hrx`;
- `model-output/model.Results`;
- `model-output/results.json`.

The review concentrated on the translated runtime rather than the complete desktop C# application.

## Test-suite findings

The initial full collection could not run because `run_solver_test.py` executed at import time and used a Windows-only path. After excluding that side effect, the baseline was:

```text
82 passed, 11 failed, 4 warnings
```

The 11 failures were test defects rather than newly demonstrated runtime defects:

- eight used the wrong model-fixture path;
- one expected the obsolete Regula-Falsi fallback for Initial Interpolated search;
- two called the superseded convergence-test API.

Additional quality problems were repaired:

- four pytest tests returned `True` instead of returning normally;
- a loader test swallowed every exception and therefore could not fail;
- the manual solver runner was collected as a test.

After correction and addition of benchmark/restart tests:

```text
96 passed in approximately 11 seconds
```

## Source correction discovered during benchmark execution

The HRX file contains solved element-local displacement and spring state. The original C# calls `CommonOperations.SetInitial` when `InitialAnalysisKey < 0`, resetting the model to a virgin state before analysis.

The Python solver initialized global `u` and `v` to zero but left the saved local element state untouched. Its first increment was consequently added to old solved deformations. This caused an immediate residual increase from about 71 to about 46,726 during diagnostic execution.

The corrected Python path now:

- parses `InitialAnalysisKey` and `InitialCombinationAnalysisKey`;
- stores the source HRX path on `Model`;
- resets supported quad/interface/spring state for a virgin analysis;
- rejects chained analyses explicitly rather than silently starting from the wrong state.

## Reference-data quality

`results.json` is not an independent nonlinear benchmark. Its displacement vector matches the displacement state serialized in the HRX, and two metadata values are stale:

- JSON interface count: 556; actual top-level HRX interfaces: 555;
- JSON stiffness nonzeros: 29,192; current assembly: 42,252.

The SQLite `model.Results` database is therefore used as the authoritative C# result source.

## Numerical conclusion

For analysis 1, step 1 (`load factor = 0.2`):

- Python converges in two nonlinear iterations;
- relative global-displacement difference versus C# reconstructed quad state is approximately `2.282e-5`;
- maximum absolute DOF difference is approximately `2.212e-7`.

This is strong evidence that initialization, load assembly, the active generalized-DOF system, and the primarily elastic first-step response are substantially aligned.

The complete five-step analysis still does not complete on the C# reference path. With default search limits, execution reaches step 2 but spends excessive time in nonlinear line-search trials. With intentionally reduced iteration limits, step 2 fails convergence. The incomplete `Quad.ComputeDN` normal-force/material coupling is the most important known mechanical difference.

## Files changed by this audit

Runtime:

- `histra/model/load.py`
- `histra/model/model.py`
- `histra/io/hr_loader.py`
- `histra/solver/solve.py`

Tests/configuration:

- `pytest.ini`
- `histra/tests/run_solver_test.py`
- `histra/tests/test_sample.py`
- `histra/tests/test_spring_hysteretic.py`
- `histra/tests/test_coulomb03_state_machine.py`
- `histra/tests/test_benchmark_alignment.py`
- `histra/tests/unit/test_solver.py`
- `histra/tests/unit/test_types.py`

Documentation was revised to distinguish repaired translation defects from current limitations.
