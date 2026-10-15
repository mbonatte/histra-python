# Current feature status

Published release: **v1.5.0** (2026-10-14). **v1.6.0 is being prepared locally**;
see [its preparation record](release/v1.6.0-preparation.md). The
[critical review response](release/v1.6.0-critical-review-response.md) records
accepted findings, source-backed disagreements and the remaining Article gate.
Current reviewed artifacts and platform verification supersede the earlier
preparation build; broader native wall/modal outputs still await reference runs.

The released package has been rerun from fresh Dhir geometry through Vert,
constant load and the final committed pushover step. Every available measured
field matches C# 2026.1.1 exactly for this configuration, including all committed
iteration counts. See [the full-chain benchmark](benchmarks/dhir-full-chain-native-parity-progress.md).

The current snapshot optimization preserves every checked field in both full
static references at source ed8a104. One sequential profiled Newton-step pair
measures an 8.50% runtime reduction; see [the performance report](benchmarks/newton-snapshot-reuse-performance.md).
Original C# residual assembly and convergence routines explain the independent
equilibrium warnings in five selected states. The native norm-selector fix has
direct bit-exact routine coverage; see [the investigation](investigations/dhir-equilibrium-diagnostics.md).
Faster library configurations are separate global-response experiments and do
not weaken the routine tests or independent equilibrium policy.

Post-release changes cover native elastic transverse and zero-friction diagonal
springs, compiled lifecycle coverage, and restraint-axis/material selection.
Linear normal-force evaluation (`NR=False`) and omitted masonry constitutive
attributes also have native routine coverage. Static tangent factorization
uses the native initial-stiffness fallback within the current Newton call.
Modal mass assembly preserves C# Single gravity and masonry weight. The existing
Dhir reference validates all 20 virgin modes with small remaining arithmetic
differences; see [the modal benchmark](benchmarks/dhir-modal-native-parity.md) and
[the remaining masonry audit](benchmarks/masonry-source-audit-2026-10-14.md).

The horizontal out-of-plane reference also matches every available checked
output through Vert step 20 and pushover step 501, stopping at the native
attempt-502 displacement limit. A fresh original-Dhir regression at 02f5f84
checks the latest static changes through all 88 commits. See the
[horizontal benchmark](benchmarks/dhir-horizontal-native-parity.md) for source
boundaries and unavailable measurements.

Historical Article/interface-chain evidence qualifies its recorded source and
environment; it is not a fresh v1.5.0 rerun of those models.

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
