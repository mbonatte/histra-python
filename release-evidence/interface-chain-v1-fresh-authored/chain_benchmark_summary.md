# Interface Material Chain Benchmark (Gate C)

**Gate C Release Status**: FAIL (NOT RELEASE-READY)
**Date**: 2026-09-09 23:17:35 UTC

## Summary by Mode

| Mode | Status | Time (s) | Vert Steps | Scour Steps | Live Steps | Unsafe Steps | Unmanaged Objects |
|---|---|---:|---:|---:|---:|---:|---:|
| authored | **FAIL** | 26.20 | 5 | 5 | 38 | 48 | 0 |

## Stage Details

| Mode | Stage | Outcome | Committed / Expected | Unsafe | Response | Stage Status |
|---|---|---|---:|---:|---|---|
| authored | Vert | completed | 5/5 | 5 | dR=3.815e-06 kN; du=4.657e-08 mm; pass=True | FAIL |
| authored | scour_1 | completed | 5/5 | 5 | dR=2.670e-05 kN; du=9.313e-08 mm; pass=True | FAIL |
| authored | LiveLoad_1 | completed_at_configured_displacement_limit | 38/38 | 38 | curve RMSE=2.688e-04; pass=True | FAIL |
