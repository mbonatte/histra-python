# Bridge 3.1 Coarse C# Results audit

Recorded 2026-09-05 from the user-supplied C# output. This is compact
provenance for the raw database; it is not a replacement for the raw input.

| Input | Bytes | SHA-256 |
|---|---:|---|
| `Bridge_3.1_Coarse.Results` | 787,779,584 | `0209e01970d5a80881c71697b03e5bb4494c844c9a3539c0bd8d8c805d2992f6` |
| `Bridge_3.1_Coarse.hrx` | 10,308,324 | `5de23f68978d5465afc87e13b5db0fad76e3e587df8a8cce65becd18419b3a43` |

The database is SQLite and contains 19 tables. The parity harness can consume:

- `ReactionSumStates`: committed reaction/resultant rows.
- `DisplModelPoints`: committed model-point translations and rotations.
- `QuadStates`, `InterfaceStates`, `DynamicVectorsState`, and
  `SpringStatesTmp`: public-step global/element/spring snapshots.
- `SpringStates`: complete terminal spring/restart state.

Its committed analysis ranges are analysis 1, steps 0--5; analysis 22, steps
0--40; and analysis 23, steps 0--1060. `SpringStates` is complete only for the
terminal step of each analysis; `SpringStatesTmp` has public-step snapshots.

There are no tables or columns for per-Newton sparse stiffness `K`, right-hand
side `B`, correction `X`, residual before/after solve, load factor,
line-search bracket/eta, or solver backend/version. Consequently the database
is authoritative evidence for committed-state parity and spring localization,
but cannot recreate the deterministic C# iteration trace required to justify a
native-solver waiver. The release gate must remain fail-closed if a discrepancy
can only be explained by a backend difference.
