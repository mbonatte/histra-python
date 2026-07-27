# HiStrA Python solver integration package

This package contains the translated Python solver, the original C# source, tests, documentation, and two numerical benchmark datasets.

## Benchmarks

- `model-output/model.hrx` / `model.Results`: analysis 1, `Vert`, five-step LoadControl reference.
- `model-live/model.hrx` / `model.Results`: analysis 22, `LiveLoad_1`, ArcLength analysis chained from the completed `Vert` state.

The Live Load benchmark now reproduces all 87 committed C# steps within `1e-4` relative global-displacement error and reaches the same maximum-displacement terminal event at attempted step 88.

See `histra_documentation/LIVE_LOAD_INTEGRATION.md` for commands, measured errors, compatibility behavior, and limitations.
## Standalone unrun-HRX workflow

From the parent directory containing the `histra/` folder, run:

```bash
python run_vert_live.py /path/to/model.HRX --output-dir python-results
```

This runs `Vert` and then the chained Live Load analysis entirely in Python,
without a `.Results` database. It exports global node `ux`, `uy`, `uz` and
explicit total/incremental reaction vectors. See `../STANDALONE_QUICKSTART.md`
or `histra_documentation/STANDALONE_VERT_LIVE.md`.


## Raw HRX preprocessing

Unlocked masonry Quad/fixed-Restraint HRXs are now prepared automatically in
Python. The translated `ModelManager.PrepareModel` stage creates global DOFs,
Quad diagonal springs, Quad–Quad and Quad–Restraint interfaces, transverse and
sliding springs, and afference matrices before the nonlinear analysis starts.
See `../RAW_HRX_PREPROCESSING.md` and
`histra_documentation/PREPROCESSING.md`.

## Performance

Compatible transverse hysteretic springs are now evaluated in a compiled Numba
batch, with compiled kinematic and residual-force maps and dense rollback state.
The supplied standalone benchmark completes in 13.10 seconds with a warm JIT
cache and 15.83 seconds with an empty cache on the audit environment, versus
267.46 seconds before this optimization. Numerical outputs and iteration counts
remain unchanged. See `../PERFORMANCE_PROFILE.md`.

## Exact raw-model preprocessing alignment

The 560-DOF benchmark exposed several path-sensitive C# preprocessing rules.
The current release ports them and restores the same 38-step Live Load trajectory
as the software-generated model. See `../PREPROCESSING_EXACTNESS_REPORT.md` and
`../PREPROCESSING_EXACTNESS_METRICS.json`.
