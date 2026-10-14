# Masonry source audit against C# 2026.1.1

The Dhir reference now matches every available committed output through pushover step 58, with subsequent exact output replay. This does not qualify every masonry input branch. This audit checks construction and numerical operations proactively, in addition to the per-committed-step comparison. Native fixtures invoke original assemblies; scripts in `tools/csharp-diagnostics` record the tested routines and inputs. No C# reference histories are injected into Python solves.

| Area | Original implementation checked | Native-backed coverage and corrections |
| --- | --- | --- |
| Flexural orientation | `Interface.PropOrthotropyParameter`, `ConstitutiveLawOperations` | Float32 axis alignment, primary/secondary curve selection and ordered blending |
| Sliding and out-of-plane orientation | Node overload of `Interface.SetSpring` | Elastic/Coulomb blending; second Quad side's vertical out-of-plane law selection |
| Transverse construction and ultimate displacement | `SetQuadTrasvSpring`, `SetUltimateDisplacement` | 19 native cases with 13 commits each, including mixed elastic directions and different side laws |
| Diagonal construction | `Quad.SetDiagonalQuad`, `GetDiagonalStiffness`, `GetVolume` | Actual masonry flexural runtime class, weak compression case, rectangular and tapered skew geometry, Single average thickness, source integration and volume operation order |
| Local displacement update | `Quad.UpdateUElem`, interface afference accumulation | Add each projected correction directly to existing local displacement, in source order; scalar and compiled paths |
| Transverse normal-force cache | Spring force/increment getters, `Quad.ComputeDN` | Preserve `force - increment` cancellation instead of replacing it algebraically by committed force |
| Local stiffness | `Interface.ComputeK` | All entries of three blocks, fixed/free interfaces, uniform/nonuniform springs, alpha 0/0.37/1; ordered spring reduction and tangent interpolation |
| Local resisting force | `Interface.SetResistingForce` | All 12 components compared exactly in the stiffness fixture cases; compiled and scalar paths |
| Trial, commit and revert | Hysteretic and Coulomb routines; solver trace | Native routine fixtures and selected recorded histories; rollback and reopened-history defects are kept separate from intended constitutive behavior |
| Global outputs | New installed-run Dhir `.Results` and trace | Every available spring field and identity, local element output, reactions and model-point displacement at every compared state; step zero is not committed |

The latest 2026-10-14 full suite passes **757 tests and 1,418 subtests**, with 14 skips. The compiled numerical backend remains in use. Small commits separate orientation, ultimate displacement, kinematics, local stiffness, force reconstruction, diagonal geometry, controller and output changes. See the [native construction and update audit](dhir-native-construction-and-update-audit.md) for whole-model binary comparisons and direct original routine fixtures.

## Limits and remaining branches

- Fresh native construction supplies 2,344 quads and 6,228 interfaces. After reapplying material 146 to 148 foundations, all 77,080 spring identities and the tested common definition fields match exactly, as do local mappings, initial global stiffness and Vert loads. Twenty imposed-input update/commit frames also match every spring U/F/tangent/phase and global resisting force/tangent. These routine checks do not qualify independently converged analyses.
- Zero-friction Coulomb material settings select a Hysteretic shear law in C#. Python's diagonal dispatch and compiled support need separate implementation and native tests for that branch.
- Purely elastic transverse flexural laws select `SpringLinearElastic` in C#. Python's runtime-class dispatch requires separate coverage; mixed elastic/nonelastic directions are already covered.
- Restraint orientation uses the restraint's own reference axes in C#. The Python restraint law-selection paths require dedicated native orientation cases.
- Polygon and node overloads of `Interface.SetSpring` differ. Node-overload coverage must not be applied to the polygon branch without checking its construction path.
- `NR=False` normal-force evaluation is not covered by the selected Newton workflow.
- Complete native pushover private spring histories and global displacement vectors are not saved at every step. Missing and NULL measurements remain unavailable, not inferred matches.

Tiny arithmetic differences can affect force-sign-dependent phase transitions. Numeric tolerance alone therefore does not establish phase parity. The strict gate retained exact phase comparisons throughout the successful Dhir comparison. See [Dhir progress](dhir-full-chain-native-parity-progress.md) for the latest completed run and output replay.
