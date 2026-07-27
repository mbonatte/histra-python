# Validation

## Current automated result

```bash
PYTHONPATH=. python -m pytest -q
```

Result after the final archive audit:

```text
96 passed
```

The suite now includes the original focused C#-alignment checks, corrected legacy tests, supplied-model parsing, restart-key behavior, virgin-state initialization, and a first-step comparison with the C# SQLite database.

## Numerical benchmark

For analysis 1, step 1 at load factor 0.2:

- Python exit code: 0;
- nonlinear iterations: 2;
- relative displacement-vector difference against C# `QuadStates`: about `2.282e-5`;
- maximum absolute DOF difference: about `2.212e-7`.

## New mistranslation found

The Python solver reset global vectors but did not reproduce C# `CommonOperations.SetInitial`. Because the HRX contains saved solved local state, the first increment was being added to old quad/interface/spring deformation.

The revised code now resets supported local/constitutive state for analyses with `InitialAnalysisKey < 0`.

## Remaining numerical gap

The complete five-step analysis 1 does not yet reproduce the C# run. The leading known difference is `Quad.UpdateDomain`: C# calls `ComputeDN` and passes normal-force change, material, volume, and initial stress to `SpringCoulomb03`; Python still passes zero/empty placeholders.

Analyses that restart from a prior analysis are rejected until complete SQLite state restoration is implemented. This blocks end-to-end analysis-22 ArcLength validation.
