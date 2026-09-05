# HiStrA Python 1.0.0 release-candidate status

Status: **BLOCKED — do not tag or retire raw benchmark assets**

Recorded on 2026-09-05 from branch `codex/v1-release`. The compact revision-3
diagnostic accompanies the solver and release-gate changes in this snapshot.

## Completed checks

- Full Linux Python 3.12 suite: `573 passed, 5 skipped, 21 warnings`.
  The nine warnings above the historical baseline are the new, intentional
  `SuboptimalSolverStrategyWarning` diagnostics.
- Wheel and sdist build completed at `db1401a`, `twine check` passed, and the
  wheel imported from an isolated environment outside the source tree as
  version `1.0.0`.
- Artifact checksums are recorded in `dist/SHA256SUMS`.
  The rebuilt wheel SHA-256 is
  `09cdc5f5cc26efe901aeb2104d6a1fc2727b8ccb0debc66175f67400387a023d`;
  the sdist SHA-256 is
  `158a7faa25f8c589230ebc3f6a000b97e040280f6241ef85b683eb96d21873bc`.
- All 14 Article models were executed in both `authored` and `strict` modes.
- Compact checkpoints, aggregate Article evidence, and the initial strategy
  matrix are preserved under `release-evidence/`.
- The supplied original workbook export and plotting notebook now validate every
  required Article figure series directly, with the published Table 1
  capacities anchored to the supplied paper. Their input hashes and exact
  figure-series mapping are recorded by harness revision 4 in
  `article-models/article_source_data_validation_revision4.json`.
- The supplied `Bridge_3.1_Coarse.Results`/`.hrx` pair has been schema-audited;
  it is adequate committed-state and spring-state parity evidence.
- Harness revision 4 repeats the strict `Bridge_3.1_Coarse` diagnostic with the
  validated source-data gate: all five gravity and eight live-load commits are
  safe, but only 13/1,065 stored C# steps are covered. The 0.695 mm overlap has
  80.6407 kN maximum reaction error, 24.6% peak-load error, and 16.0% normalized
  curve RMSE; terminal spring-phase distributions also differ. This remains a
  hard physical/numerical failure, not a source-data failure.
- The complete five-increment P-Delta gravity matrix has zero unsafe commits
  for every measured `EachStep` and `EachIteration` candidate. All candidates
  preserve the selected Standard Bisection baseline response; the authored
  Modified Regula-Falsi `EachStep` run was fastest in this single measurement.

## Mandatory gate failures

- Article authored mode: 0/14 models passed. Python covered 6,060 of 7,277
  stored C# steps, but all 6,060 committed Python steps failed the independent
  force-equilibrium audit.
- Article strict mode: 0/14 models passed. Only 4 of 7,277 reference steps were
  committed; the remaining models stopped before their first safe commit.
- The authored Zhang 3.4 run covered 179/179 rows, but all 179 commits were
  unsafe and its maximum reaction difference was 60.5843 kN.
- The strategy matrix cannot yet make production recommendations for the full
  live-load path. The revised complete gravity matrix qualifies Standard
  Bisection and Standard Secant, with Bisection faster on the measured coarse
  model. Bisection also qualifies over the first five live-load increments,
  but the strict path still stops before the reference peak/range.
- Windows and the Python 3.13/3.14 CI matrix have not been executed on their
  target platforms.

## Required external evidence

The supplied C# `.Results`/`.hrx` pair does not contain the per-Newton sparse
K, B, X, residual, load-factor, or line-search values needed for the
deterministic C# trace described in
`docs/benchmarks/article-models-release-gate.md`. It cannot be reconstructed
from these files. No backend waiver may be issued while that evidence is absent;
the committed-state discrepancy must instead be fixed directly in Python or an
instrumented C# trace must become available.

No tolerance waiver can replace this evidence. Tagging `v1.0.0`, publishing,
and deleting the 36 GB raw Article suite remain prohibited until every release
gate passes.

## Continued numerical investigation

- Corrected concrete ArcLength line searches to use the combined correction
  stored in `LS.X` after `ArcLength.Update`, matching the supplied C# call
  sequence. LoadControl is unchanged because its raw and combined corrections
  are identical.
- Added an explicit production-safe endpoint projection while retaining the C#
  projection as the compatibility default.
- Corrected opt-in ArcLength cutbacks so Standard methods retain the current-
  tangent policy instead of silently becoming Modified methods.
- The revised strict `Bridge_3.1_Coarse` run now safely completes all five
  gravity steps and eight live-load steps (13/1,065 overall), then reaches a
  divergent ArcLength branch. This is progress over the previous zero-step
  strict result, but remains a hard release failure.
- Curve metrics now interpolate by physical displacement and fail when the
  Python curve does not cover the reference range; step-number pairing is no
  longer used for branch-insensitive acceptance.
- The revision-3 diagnostic covers only 0.695 mm of the 30.015 mm C# live-load
  displacement range. Over that overlap its peak-load error is 24.6% and its
  normalized curve RMSE is 16.0%, so the remaining difference is physical,
  not a reporting artefact.
- Capability preflight and the direct solver paths now reject unknown
  ArcLength-procedure, modal-procedure, modal-convergence, and mass-matrix enum
  values instead of falling through to a different supported algorithm.
- Nonlinear factories now match complete C# method names rather than accepting
  arbitrary names containing a supported line-search suffix. The HRX inventory
  also rejects Vertex, InterfaceMF, and NodeBC alongside the other non-V1
  computational domains.
- HRX analysis metadata now preserves C# `TypeLoadDistribution`,
  `ForceImposed`, and `ForceControl` values. Static `Modal`, `Triangular`,
  `Adaptive`, and `ShearFloor` distributions are rejected at preflight rather
  than silently being assembled as an ordinary force/load-combination run.
- The scalar (unmanaged) Quad fallback now invokes the same C# fixed and
  stress-interpolated shear-energy callback as the compiled Quad runtime.
- A fresh revision-3 all-model strict run was stopped recoverably after roughly
  32 minutes without a fourth checkpoint. The three completed checkpoints all
  have zero unsafe commits but fail coverage: 3.1 coarse reached 13/1,065,
  3.1 multiring 9/91, and 3.2 1/338. The partial-run record is preserved under
  `release-evidence/article-models-revision3-strict/`; it is not an aggregate
  pass and the unfinished workers contribute no evidence.
