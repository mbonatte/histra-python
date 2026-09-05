# HiStrA Python 1.0.0 release-candidate status

Status: **BLOCKED — do not tag or retire raw benchmark assets**

Recorded on 2026-09-05 from branch `codex/v1-release` at commit `7b704b7`,
plus the report-formatting change that accompanies this evidence snapshot.

## Completed checks

- Full Linux Python 3.12 suite: `539 passed, 5 skipped, 21 warnings`.
  The nine warnings above the historical baseline are the new, intentional
  `SuboptimalSolverStrategyWarning` diagnostics.
- Wheel and sdist build completed, `twine check` passed, and the wheel imported
  from an isolated environment outside the source tree as version `1.0.0`.
- Artifact checksums are recorded in `dist/SHA256SUMS`.
- All 14 Article models were executed in both `authored` and `strict` modes.
- Compact checkpoints, aggregate Article evidence, and the initial strategy
  matrix are preserved under `release-evidence/`.

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
  gravity/live-load path. Standard Regula-Falsi with ForceMoment safely solves
  the first coarse-gravity increment, then diverges at the next increment.
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
