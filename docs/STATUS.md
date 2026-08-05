# Current feature status

Last reviewed: 2026-08-05

## Supported

| Area | Current boundary |
|---|---|
| HRX loading | Supported for committed benchmark models |
| Locked models | Supported when required computational objects are present |
| Unlocked preprocessing | Validated masonry four-node Quad and fixed line-Restraint subset |
| Quad–Quad contacts | Full-edge and collinear partial-edge contacts, including partition/T-junction overlaps |
| Springs | Masonry diagonal, transverse hysteretic, in-plane and out-of-plane Coulomb paths used by the benchmarks |
| Static integration | LoadControl and ArcLength paths used by committed benchmarks |
| Chained analyses | In-memory HRX dependency execution through `AnalysisSession` |
| Interface material changes | Supported between committed analyses with committed-state transfer |
| C# results database | Readable as a numerical reference and restart source for supported schemas |
| Performance backend | Numba-compiled paths with scalar diagnostic fallback |
| Modal eigenanalysis | C#-compatible Quad mass matrix, SubspaceIterations, InverseIterations, modal quantities and shapes |

## Important limitations

- The translated preprocessor is not the complete desktop preprocessor.
  Unsupported element types and topologies fail explicitly.
- Interface material mutation is implemented at committed analysis boundaries,
  not as arbitrary stage changes inside an individual load step.
- Numerical equivalence claims are benchmark-specific.
- Some C# result databases omit information needed to independently validate
  every multiplier or continue from every terminal state.
- The first run on a new platform may include Numba compilation time.
- `python -m histra` inspects/assembles the HRX; it does not execute the full
  standalone nonlinear workflow.
- Modal mass for future Vertex, Solid, Frame and Fiber domain entities is not
  yet ported; populated unsupported collections fail explicitly.

## Source of truth

For behavior, use the Python implementation and tests. For user workflow, use
the maintained guides. Treat files under `docs/archive/` as historical context
only.
