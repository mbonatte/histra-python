# Feature status

| Area | Status | Evidence/notes |
|---|---|---|
| HRX core parser | Implemented | Supplied model loads: 2,142 DOFs, 306 quads, 555 interfaces |
| Analysis restart-key parsing | Implemented | `InitialAnalysisKey` and combination key retained |
| Virgin analysis initialization | Implemented for supported entities | Matches C# `SetInitial` subset for quads/interfaces/springs |
| Prior-analysis restart | Unsupported safely | Raises until full SQLite history restore is implemented |
| Load-function items | Implemented | Separate C# entities joined and sorted |
| Sparse stiffness assembly | Implemented | Supplied model assembles to 42,252 nonzeros |
| Linear sparse solving | Implemented with validation | Nonfinite/rank failures converted to errors |
| LoadControl | Partially validated | First C# reference step matches closely; full path does not |
| Standard/Modified Newton | Implemented | Tangent/initial stiffness choice preserved |
| Regula Falsi | Implemented, later-path validation pending | Focused tests pass; full reference step 2 unresolved |
| Secant/Bisection/Initial Interpolated | Implemented, limited validation | Unit-level behavior only |
| ArcLength | C#-aligned structure, not end-to-end validated | Analysis 22 requires restart state first |
| ALS | Implemented structurally, benchmark pending | Rollback/subincrement tests exist; no full yielding reference |
| Force/disp/work convergence | Implemented | Absolute C# criteria |
| Quad mechanics | Partial | Missing C# `ComputeDN`/normal-force coupling |
| Interface mechanics | Implemented, benchmark incomplete | First-step local state is close to C# |
| Hysteretic spring | Unit-tested | XML, envelope, trial/commit/revert tests |
| Coulomb03 spring | Unit-tested, system coupling incomplete | State-machine tests pass; quad normal coupling missing |
| Self-weight | Implemented | Used by analysis 1 benchmark |
| Other load actions | Incomplete | Requires broader C# load subsystem |
| Psi coefficients | Explicitly unsupported | Raises instead of silently eliminating load |
| P-Delta | Explicitly unsupported | Required C# subsystem absent |
| SQLite quad-state reader | Implemented | Used in first-step C# benchmark |
| Global dynamic-vector reader | Implemented | Reads final/specified `U,V` from SQLite |
| Complete restart-state reader | Not implemented | Interface and spring history still needed |
| CLI inspection | Implemented | Parser/assembly snapshot, not nonlinear solve |
| Automated tests | Implemented | 96 passing |
| Engineering equivalence | Not established | Only first nonlinear step presently agrees |
