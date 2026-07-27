# Feature Support Status

| Feature | Status | Evidence/constraint |
|---|---|---|
| HRX parsing for supplied model | Supported | Full model loads and benchmark runs |
| LoadControl | Supported for selected path | Five committed steps execute |
| Modified Regula-Falsi | Implemented, parity incomplete | Step 1 exact; step 2 path differs |
| Work convergence | Supported | Per-step work errors recorded |
| Quad normal-force coupling | Supported | Focused tests and exact-state comparison |
| Interface Coulomb coupling | Supported | All 105 exact under C# inputs |
| Hysteretic springs | Supported for benchmark | All 2,349 exact under C# inputs |
| Complete trial rollback | Supported | Snapshot fingerprints and failed-path tests |
| Final C# database restart | Supported | 126 DOFs and 2,454 springs restored losslessly |
| Intermediate database restart | Explicitly unsupported | Compact rows omit constitutive history |
| Chained analysis initialization | Supported from complete final state | Strict reader/restorer |
| Self-weight/gravity | Supported for benchmark | Step 1 load response exact |
| Other applied-load object families | Unsupported | Raise/require implementation rather than assume zero |
| P-Delta | Unsupported | Benchmark declares `None` |
| ALS | Rollback infrastructure tested | Not used by benchmark |
| ArcLength | Partial | Basic code present; not validated against this DB |
| Modal/dynamic analyses | Unsupported/incomplete | Outside selected benchmark |
| Full C# step-by-step numerical parity | Not achieved | Steps 2–5 exceed displacement tolerance |
