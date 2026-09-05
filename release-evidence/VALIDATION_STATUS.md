# HiStrA Python 1.0.0 release-candidate status

Status: **BLOCKED — do not tag or retire raw benchmark assets**

Recorded on 2026-09-05 from branch `codex/v1-release`. The compact revision-3
diagnostic accompanies the solver and release-gate changes in this snapshot.

## Completed checks

- Full Linux Python 3.12 suite: `559 passed, 5 skipped, 21 warnings`.
  The nine warnings above the historical baseline are the new, intentional
  `SuboptimalSolverStrategyWarning` diagnostics.
- Wheel and sdist build completed, `twine check` passed, and the wheel imported
  from an isolated environment outside the source tree as version `1.0.0`.
- Artifact checksums are recorded in `dist/SHA256SUMS`.
  The rebuilt wheel SHA-256 is
  `ef333f33a356bea9b9e78938d359c904e74e4eb875c2de7c6799c36544166de8`;
  the sdist SHA-256 is
  `98ce53ddc6254bd6ddbd6065deea7d55d92048cbefc64a914b1e3211bdf66883`.
- All 14 Article models were executed in both `authored` and `strict` modes.
- Compact checkpoints, aggregate Article evidence, and the initial strategy
  matrix are preserved under `release-evidence/`.
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
- The source CSVs for Figures 9, 12, 13, 15, 17, 20, 22, 24, and 25 and Table 1
  have not been supplied, so article/experimental validation is fail-closed.
- The strategy matrix cannot yet make production recommendations for the full
  live-load path. The revised complete gravity matrix qualifies Standard
  Bisection and Standard Secant, with Bisection faster on the measured coarse
  model. Bisection also qualifies over the first five live-load increments,
  but the strict path still stops before the reference peak/range.
- Windows and the Python 3.13/3.14 CI matrix have not been executed on their
  target platforms.

## Required external evidence

Run the deterministic C# trace described in
`docs/benchmarks/article-models-release-gate.md` for
`Bridge_3.1_Coarse`, analysis `Vert`, steps 1 and 2. The trace must include
sparse K, B, X, residual, load factor, line-search values, control displacement,
and relevant spring identities/states. Also place the original article datasets
in `release-evidence/article-source-data/` using the documented CSV schema.

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
