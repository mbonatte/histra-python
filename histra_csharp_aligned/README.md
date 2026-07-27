# HiStrA Python — C#-aligned solver revision

This directory is a corrected copy of the supplied Python translation, revised by comparing the solver-critical paths with the supplied original C# code.

The comparison was intentionally limited to the components needed to investigate the reported issues:

- sparse linear system behavior;
- stiffness and residual assembly;
- load control and rollback;
- Newton-Raphson and Newton with line search;
- Regula Falsi, Secant, Bisection, and Initial Interpolated searches;
- convergence tests;
- arc-length integration;
- nonlinear analysis step control and ALS;
- load-function parsing;
- restraints/global generalized DOFs;
- load-combination coefficients relevant to the existing Python loader.

## Main documents

- [C# comparison](CSHARP_COMPARISON.md)
- [Bugs found in the original C#](ORIGINAL_CSHARP_BUGS.md)
- [Python changes](CHANGES.md)
- [Validation notes](VALIDATION.md)

## Validation

```bash
python -m compileall -q histra
pytest -q
```

At packaging time:

- all Python modules compiled;
- package imports succeeded;
- 96 automated tests passed.
- The supplied analysis-1 first load step matches the C# SQLite displacement state to approximately `2.282e-5` relative error.

The complete five-step nonlinear path is not yet equivalent; see `VALIDATION.md` and the main documentation `ISSUES.md`.

## Important unsupported features

The original C# application has subsystems that are not present in this Python snapshot. The revised code now fails explicitly instead of silently producing misleading results for:

- P-Delta load generation;
- load-combination `Psi` coefficients that require `LoadTemplateItem.Psi0/Psi1/Psi2`;
- full reaction/model-point graph extraction.
