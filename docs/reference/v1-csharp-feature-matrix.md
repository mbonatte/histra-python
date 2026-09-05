# C# to Python V1 feature matrix

Status is one of `verified`, `partial`, `missing`, `intentional C# defect`, or
`out of V1 scope`. “Verified” refers to the named tests; release acceptance also
requires the Article and platform gates.

| Feature | Status | C# authority | Python owner | Test/evidence |
|---|---|---|---|---|
| HRX masonry/Quad/Interface/load parsing | verified | `Objects.*`, serializer attributes | `histra/io/hr_loader.py` | `test_hr_loader.py`, `test_load_vector.py` |
| Unlocked preprocessing, six faces, afference | verified | `ModelManagement.ComputationalElementsOperations` | `histra/preprocessing` | `test_prepare_model.py`, contact/afference tests |
| Self-weight/load combinations | verified | `LoadOperations`, Quad gravity | `histra/solver/load_vector.py` | load-vector and self-weight tests |
| Dependency/restart/state transfer | verified | `Analysis.InitialAnalysisKey`, domain commit/revert | `histra/solver/session.py` | session, chain, restart tests |
| Interface material changes/mixed sides | verified | Interface `SetSpring` and material operations | `interface_material.py`, preprocessing selection | interface-material tests |
| Elastic/hardening/softening/exponential/parabolic envelopes | verified | `ConstitutiveLawHysteretic`, `SpringHysteretic` | `constitutive_laws.py`, `springs/hysteretic.py` | constitutive/envelope/batch tests |
| Linear/Coulomb/Cacovic domains | verified | `ConstitutiveLawOperations.SetShearConstitutiveLaw` | `constitutive_laws.py`, `coulomb03*` | constitutive and Coulomb tests |
| Fracture energy/ductility/contact area/orthotropy | verified | `ConstitutiveLawCoulomb` | preprocessing and Coulomb runtime | constitutive, material-selection, Coulomb tests |
| Initial/Takeda Coulomb reversal | verified | `SpringCoulomb03.setTrialStrain*` | `coulomb03_state.py`, batch kernels | scalar/batch hysteretic tests |
| `UnloadShear` Origin/Mixed selector | intentional C# defect | C# stores the material enum but Quad diagonal construction forces Takeda and combined Interface sliding forces Initial | `constitutive_laws.py`, `spring_assignment.py` | enum is validated; Python follows the same constructible Initial/Takeda paths instead of dispatching a different law |
| Static integrators and controllers | verified | `SolverRuntime.Integrator/StaticIntegrator.cs`, `UtilityLibrary.Tipi/IntegratorEnum.cs`, `ArcLengthProcedureEnum.cs` | `incremental_integrator.py`, `arc_length.py` | integrator/controller and unknown-procedure preflight tests |
| Newton and line-search methods | verified | `EquiSolnAlgo` factory | `solution_algorithm.py` | solution-algorithm tests |
| Initial-Interpolated through base factory | intentional C# defect | C# hidden `new` method/base dispatch | explicit compatibility behavior | dispatch regression test |
| ForceMoment/DispRotation/Work | verified | C# convergence-test factory | `convergence_test.py` | convergence and equilibrium tests |
| RelativeWork | intentional C# defect | enum exists; C# factory branch absent | `capabilities.py` | preflight rejection test |
| P-Delta EachStep/EachIteration | partial | C# incremental-integrator geometric update | `incremental_integrator.py` | unit parity passes; Article/Windows gate pending |
| Modal mass/eigensolution/projection | verified | `SolverRuntime/ModelManager.cs`, `Pseudovectors.cs`, `SubSpaceIteration2`; modal/mass enums in `UtilityLibrary.Tipi` | `mass_matrix.py`, `modal.py`, output projection | modal and batch comparison tests; unknown modal/mass enums fail before assembly |
| Dynamic nonlinear/response spectrum | out of V1 scope | dynamic analysis subsystem | capability preflight | precise rejection tests |
| Frame/Slab/Link/Joint and concrete/steel/fiber | out of V1 scope | desktop element/material subsystems | capability/input boundary | inventory only; no partial-result claim |

The authoritative release evidence is the versioned Article report, strategy
report, full test logs, and platform CI—not this inventory alone.
