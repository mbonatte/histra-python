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

