# HiStrA Python documentation

This documentation describes the supplied Python port, its relationship to the original C# solver, the current automated-test baseline, and the numerical validation performed with the supplied `model.hrx` and `model.Results` files.

**Audit date:** 2026-07-27  
**Runtime Python modules:** 51  
**Automated tests:** 96 passing  
**Reference data:** supplied HRX model plus C# SQLite result database

> [!IMPORTANT]
> The first nonlinear load step of analysis 1 agrees closely with the stored C# result, but the complete nonlinear analysis is not yet validated. Do not treat the Python solver as an engineering-equivalent replacement until the remaining constitutive coupling and restart-state issues in [ISSUES.md](ISSUES.md) are resolved.

## Documentation map

| Document | Purpose |
|---|---|
| [AUDIT_REPORT.md](AUDIT_REPORT.md) | What was checked, changed, and measured |
| [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) | Comparison with `model.Results` |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, ownership, and dependencies |
| [SOLVER_FLOW.md](SOLVER_FLOW.md) | Linear and nonlinear execution sequence |
| [FEATURE_STATUS.md](FEATURE_STATUS.md) | Supported, partial, and unsupported behavior |
| [ISSUES.md](ISSUES.md) | Current issues, separated from repaired defects |
| [REMEDIATION_PLAN.md](REMEDIATION_PLAN.md) | Recommended next implementation order |
| [TESTING_AND_VALIDATION.md](TESTING_AND_VALIDATION.md) | Test suite and engineering-validation plan |
| [MODULE_INDEX.md](MODULE_INDEX.md) | Per-module reference pages |
| [PORTING_NOTES.md](PORTING_NOTES.md) | C# translation conventions |
| [GLOSSARY.md](GLOSSARY.md) | Structural-analysis terms |

## Verified baseline

From the repository root:

```bash
PYTHONPATH=. python -m pytest -q
python -m compileall -q histra
```

Current result:

```text
96 passed
```

The tests include a real comparison of the first nonlinear step against the C# SQLite database.

## Typical use

```python
from histra.io.hr_loader import load_model
from histra.solver.solve import solve_static_nonlinear

model = load_model("model-output/model.hrx")
analysis = model.collections.analyses[1]
code, steps = solve_static_nonlinear(model, analysis, combination=1)

if code != 0:
    raise RuntimeError(f"Analysis failed with code {code}")
```

Only analyses with `InitialAnalysisKey < 0` currently start safely. An analysis that depends on a previous analysis is rejected until the complete committed C# database state can be restored.
