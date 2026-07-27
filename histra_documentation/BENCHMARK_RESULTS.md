# Benchmark results

## Supplied artifacts

| Artifact | Use in validation |
|---|---|
| `model.hrx` | Input model and serialized application state |
| `model.Results` | Authoritative C# SQLite results |
| `results.json` | Historical parser/assembly snapshot; not an independent solver result |

## Model inventory

The current loader reports:

| Item | Count/value |
|---|---:|
| Generalized DOFs | 2,142 |
| Quads | 306 |
| Interfaces | 555 |
| Nodes | 388 |
| NodeCs | 18 |
| Restraints | 14 |
| Initial-stiffness `K.nnz` | 42,252 |

The XML itself confirms 555 top-level keyed `Interface` entities.

## C# database coverage

The SQLite database contains, among other tables:

- `QuadStates` for analysis 1, steps 0 through 5;
- `InterfaceStates` for analysis 1, steps 0 through 5;
- `QuadStates` and `InterfaceStates` for analysis 22, steps 0 through 61;
- final `DynamicVectorsState` for analyses 1 and 22;
- final spring-history records in `SpringStates`.

## First-step comparison

The automated benchmark constructs the same first load interval as C# analysis 1 and compares Python global displacement with displacement reconstructed from C# `QuadStates`, step 1.

| Metric | Result |
|---|---:|
| Python exit code | 0 |
| Python committed steps | 1 |
| Python nonlinear iterations | 2 |
| Load factor | 0.2 |
| Python displacement-vector norm | `4.3901193906e-2` |
| C# displacement-vector norm | `4.3901191095e-2` |
| Relative vector difference | `2.2820198e-5` |
| Maximum absolute DOF difference | `2.2123213e-7` |
| Mean absolute DOF difference | `4.4611311e-9` |

Test thresholds are intentionally slightly looser:

```text
relative error < 5e-5
maximum absolute error < 3e-7
```

## Full-analysis result

The complete C# analysis 1 has five committed load steps. The Python run currently:

1. completes step 1;
2. enters step 2;
3. performs repeated nonlinear line-search trials;
4. does not complete within the bounded audit run.

A diagnostic run with deliberately small line-search/Newton limits terminates at step 2 with nonconvergence. This bounded run is diagnostic only and is not a replacement for the production settings.

## Interpretation

The first-step agreement validates an important but limited regime. It does **not** validate:

- later yielding and friction/contact evolution;
- `Quad.ComputeDN` normal-force coupling;
- full `SpringCoulomb03` history correspondence;
- automatic load stepping after nonlinear failure;
- chained analysis 22 restart and ArcLength history;
- final force, reaction, and energy agreement.
