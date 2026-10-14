# Current feature status

Release status: **v1.4.2** (2026-10-13).

This maintenance release improves C# 2026.1.1 geometry, spring definitions,
nonlinear contracts and modal inverse iteration. Fresh Dhir Vert comparisons
cover 77,080 springs at all 10 committed steps with zero spring-phase differences.
Dhir Vert now passes every available numeric state field at initial state and all ten commits, including exactly matching reaction vectors at every step. See [the current Vert audit](investigations/dhir-vert-native-parity.md) and [the changelog](../CHANGELOG.md).

Post-release source corrections on 2026-10-14 match native power/arctangent rounding, float32 spring-distance square roots and native line-load integration. The remaining Vert reaction difference is resolved. The second analysis, TLM_Constant_UDL, passes its initial-state gate but differs at the first commit; pushover remains gated behind it. The instrumented C# GUI rerun exactly reproduces all saved Vert/constant-load fields and confirms a stale spring-U rollback defect, quantitatively explaining all 36 logged transverse offsets. Why Python converges on the full increment before that rollback remains open. See [the constant-load investigation](investigations/dhir-constant-load-rollback.md).

The V1 Article/interface-chain evidence is historical qualification of its
recorded source and environment, not a new v1.4.2 rerun of those models.

## Supported

| Area | Current boundary |
|---|---|
| HRX loading | Supported for committed benchmark models |
| Locked models | Supported when required computational objects are present |
| Unlocked preprocessing | Validated masonry four-node Quad and fixed line-Restraint subset, including C# directional sliding-law selection |
| Quad–Quad contacts | Full-edge and collinear partial-edge contacts, including partition/T-junction overlaps |
| Springs | Masonry diagonal, transverse hysteretic, in-plane and out-of-plane Coulomb paths used by the benchmarks |
| Static integration | LoadControl, ArcLength and ArcLengthLinear paths, with explicit C# `ArcLength1` corrector behavior |
| Chained analyses | In-memory HRX dependency execution through `AnalysisSession` |
| Interface material changes | Supported between committed analyses with committed-state transfer |
| C# results database | Readable as a numerical reference and restart source for supported schemas |
| Performance backend | Compiled policy and runtime-rebuild fail-closed coverage are implemented; complete hot-path performance qualification remains a release gate |
| Modal eigenanalysis | C#-compatible Quad mass matrix, SubspaceIterations, InverseIterations, modal quantities and shapes |

## Important limitations

- The [independent review](release/v1-independent-review.md) remains in progress;
  Article strict qualification, strict interface-chain convergence, and full
  strategy/performance evidence remain open. The former interface-chain false
  PASS and compiled lifecycle fallback are corrected, but are not release
  evidence by themselves.
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
