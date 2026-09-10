# Interface Material Chain Benchmark (Gate C)

**Gate C Release Status**: FAIL (NOT RELEASE-READY)
**Date**: 2026-09-09 23:20:13 UTC

## Summary by Mode

| Mode | Status | Time (s) | Vert Steps | Scour Steps | Live Steps | Unsafe Steps | Unmanaged Objects |
|---|---|---:|---:|---:|---:|---:|---:|
| strict | **FAIL** | 15.15 | 5 | 1 | 0 | 0 | 0 |

## Stage Details

| Mode | Stage | Outcome | Committed / Expected | Unsafe | Response | Stage Status |
|---|---|---|---:|---:|---|---|
| strict | Vert | completed | 5/5 | 0 | n/a (strict predecessor stages are checked for completion and safe equilibrium; C# authored rows are not a comparable response path) | PASS |
| strict | scour_1 | nonconverged | 1/5 | 0 | n/a (strict predecessor stages are checked for completion and safe equilibrium; C# authored rows are not a comparable response path) | FAIL |
| strict | LiveLoad_1 | failed | 0/38 | 0 | n/a (each finite curve requires at least two displacement/load rows) | FAIL |
