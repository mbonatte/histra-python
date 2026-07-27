# Remaining Limitations

1. Steps 2–5 of analysis 1 do not reproduce the C# committed displacement vectors within 1e-4 relative error.
2. The exact first differing Newton/line-search trial is unavailable because the database stores no iteration history.
3. The audit environment cannot run the original C# native UMFPACK stack for side-by-side iteration tracing.
4. Intermediate restart is not lossless because `SpringStatesTmp` omits required history.
5. Only the benchmark's self-weight load path is validated. Other concentrated, distributed, pressure, vehicle, seismic, and template/Psi load object families require explicit ports.
6. P-Delta is not implemented and intentionally raises when requested.
7. ArcLength exists but is not accepted against a C# database in this package.
8. Modal and dynamic analyses are outside the corrected benchmark path.
9. Interface serialized resultants are postprocessed fields and are not currently reproduced as database output.
10. The Python project reads C# results but does not yet write a complete C#-compatible `.Results` database.
