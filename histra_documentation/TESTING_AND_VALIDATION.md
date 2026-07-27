# Testing and Validation

## Final status

- Compile: passed.
- Import: passed.
- Test suite: 113 passed, 1 skipped.
- Full benchmark: completed independently, five steps, 34.45 seconds.

The skipped test is the long full-analysis acceptance assertion, enabled only with `HISTRA_RUN_FULL_BENCHMARK=1`. It remains skipped by default because steps 2–5 are known not to meet parity and because it is much slower than the focused suite.

## Focused coverage added

- Quad `ComputeDN`, current stress, and volume.
- Interface normal increment into all Coulomb groups.
- Coulomb03 trial/commit/revert.
- Complete solver snapshot roundtrip.
- Failed Newton iteration rollback.
- Failed ALS substep rollback.
- Signed unloading discretization.
- Typed C# SQLite global/quad/interface/spring readers.
- Every stored C# step and load factor.
- Virgin initialization.
- Complete chained/final restart.
- First C# reference step.
- Optional full-analysis result comparison.

## Commands

From the directory containing `histra/`:

```bash
python -m compileall -q histra
python -c "import histra; print('import ok')"
python -m pytest -q
python -m histra.tools.benchmark_csharp_sqlite \
  --hrx histra/model-output/model.hrx \
  --results histra/model-output/model.Results \
  --analysis 1 --combination 1 \
  --output histra_benchmark_metrics.json
```
