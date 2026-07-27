# Testing and validation

## Current automated baseline

Run from the extracted repository root:

```bash
PYTHONPATH=. python -m pytest -q
```

Audited result:

```text
96 passed in 10.49s
```

The collection is controlled by `pytest.ini`; manual scripts are not imported as tests.

## What the suite covers

- XML/model parsing and compatibility imports;
- points, afference, matrices/vectors, and linear-system behavior;
- elastic, hysteretic, multilinear, Coulomb, and Coulomb03 spring behavior;
- quad/interface construction and selected mechanics;
- solver factories, convergence criteria, rollback, load control, line search, and ArcLength components;
- C#-alignment regression checks;
- supplied-model inventory and restart-key parsing;
- first nonlinear load step against C# `model.Results`.

## C# benchmark assertion

`test_benchmark_alignment.py` runs analysis 1 over its first load interval and checks:

```text
relative displacement error < 5e-5
maximum absolute DOF error < 3e-7
```

Observed values are approximately `2.282e-5` and `2.212e-7`.

## Checks that are still missing

1. Step-by-step equality for all five analysis-1 steps.
2. Complete `SpringCoulomb03` history comparison at selected quads.
3. Restart from analysis 1 into analysis 22.
4. ArcLength force-displacement path through all 61 stored steps.
5. Global reactions and graph output.
6. Energy comparison.
7. P-Delta and non-self-weight loads.
8. Matrix-entry comparison, not only shape/nonzero count.

## Recommended reference harness

For each accepted C# step, store/compare:

- global `U` and `V` from `DynamicVectorsState` when available;
- every quad/interface local `U`;
- selected spring `U`, `F`, tangent, phase, extrema, and energy;
- external/reference load and residual;
- Newton correction, eta, and convergence criterion;
- tangent matrix checksums or selected rows;
- committed load factor and pseudo-time.

A mismatch should be localized at the first differing iteration rather than diagnosed only from final displacement.

## CI commands

```bash
python -m compileall -q histra
PYTHONPATH=. python -m pytest -q
```

Optional static tools should be added after the current large direct-port modules have a defined formatting/type policy.
