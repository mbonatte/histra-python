# Ersino modal-analysis parity benchmark

## Inputs

- Model: `Ersino.hrx`
- C# result database: `Ersino.Results`
- Modal analysis: key `30`, name `Modal_-1`
- Active degrees of freedom: `14,252`
- Requested modes: `10`
- Stored C# mode-shape rows: `142,520`

## C# algorithm reproduced

The Python implementation follows the active C# execution path rather than
substituting a generic eigensolver:

1. restore or initialise the model state;
2. assemble the tangent stiffness matrix with `alfa = 1`;
3. integrate the Quad consistent mass matrix with the C# 6×6×6 rule;
4. run `Matrix.SubSpaceIteration2`, including its deterministic .NET
   `Random(0)` initial subspace and eigenvalue-change convergence test;
5. mass-normalise the modes;
6. calculate participation factors, effective masses, mass percentages,
   directional maxima and complete DOF mode shapes.

The requested HRX mass type is `Lumped`, but the active C# Quad routine ignores
that switch and integrates the consistent matrix. Python deliberately reports
both the requested and effective types and reproduces the effective C# matrix.

## Numerical comparison

| Mode | C# frequency [Hz] | Python frequency [Hz] | Relative error |
|---:|---:|---:|---:|
| 1 | 3.8184457214 | 3.8184457448 | 6.14e-09 |
| 2 | 4.7701457266 | 4.7701457666 | 8.40e-09 |
| 3 | 5.0543547533 | 5.0543547868 | 6.63e-09 |
| 4 | 6.0342187771 | 6.0342188601 | 1.38e-08 |
| 5 | 6.6696856866 | 6.6696857786 | 1.38e-08 |
| 6 | 6.8503087343 | 6.8503087855 | 7.47e-09 |
| 7 | 6.9993484729 | 6.9993485643 | 1.31e-08 |
| 8 | 8.6566424669 | 8.6566425457 | 9.11e-09 |
| 9 | 9.2394155830 | 9.2394157155 | 1.43e-08 |
| 10 | 10.2326334901 | 10.2326336046 | 1.12e-08 |

Maximum absolute relative frequency error: `1.4342e-08`.

Directional total mass in X:

- C#: `51.67654681724974`
- Python: `51.67654580028968`
- Relative error: `-1.9679e-08`

The minimum diagonal mass-weighted correlation between matching C# and Python
mode shapes is `0.9999999861`; all ten correlations are effectively one.

## Test commands

```console
HISTRA_MODAL_HRX=/path/Ersino.hrx \
HISTRA_MODAL_RESULTS=/path/Ersino.Results \
python -m pytest -q histra/tests/test_modal_analysis.py
```

```console
python -m histra.tools.validate_modal_results \
  Ersino.hrx Ersino.Results --analysis-key 30 \
  --output modal-validation.json
```

## Interpretation

The upper modes retain larger eigen-residuals because the original C# stopping
rule checks the normalized change in eigenvalues, not the eigen-residual. This
is intentional compatibility behaviour. Python exposes each residual so that a
future high-accuracy eigensolver mode can be added without confusing it with
strict C# parity.
