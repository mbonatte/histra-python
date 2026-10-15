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

The 2026-10-14 full suite passes **757 tests and 1,418 subtests**, with 14 skips. The compiled numerical backend remains in use. Small commits separate orientation, ultimate displacement, kinematics, local stiffness, force reconstruction, diagonal geometry, controller and output changes. See the [native construction and update audit](dhir-native-construction-and-update-audit.md) for whole-model binary comparisons and direct original routine fixtures.

## Limits and remaining branches

- Fresh native construction supplies 2,344 quads and 6,228 interfaces. After reapplying material 146 to 148 foundations, all 77,080 spring identities and the tested common definition fields match exactly, as do local mappings, initial global stiffness and Vert loads. Twenty imposed-input update/commit frames also match every spring U/F/tangent/phase and global resisting force/tangent. These routine checks do not qualify independently converged analyses.
- Zero-friction Coulomb masonry now selects the native Hysteretic diagonal, including asymmetric strengths and ultimate-strain/fracture-energy construction. Eight original-assembly cases cover rectangular/tapered geometry, ordinary/weak compression, 112 cyclic commits and rejected-trial reverts. Definitions and phases are exact; cyclic force/tangent/energy comparisons use rtol=1e-12 and atol=1e-12. Compiled coverage includes fresh preparation, a solver step, snapshots, reset, disabled springs, material changes and history-preserving rebuilds. A matching full C# structural-chain run for this branch remains separate validation.
- Purely elastic transverse flexural laws now select `SpringLinearElastic`, including mixed elastic/hysteretic series construction. Five original-assembly factory cases cover nine cyclic commits each, scalar and compiled forces/tangents, exact phase and definition metadata. Production tests cover preparation, rebuilds and nonlinear-to-elastic material mutation with zero unmanaged elements. The compiled elastic update preserves the native incremental force calculation without hysteretic unloading phases. Broader structural validation of this branch remains separate from Dhir qualification.
- Line-restraint flexural and sliding selection now uses the restraint axis, with the two Single normalizations in the original constructor and ReferenceSystem.Set. Twelve original-assembly cases cover distinct/oblique axes, nonlinear and mixed elastic laws; checked axes, law fields and curve selections match exactly. Scalar and batched transverse preparation share this rule. Native constructor tests also correct the vertical SlidingPlasticStiffnessRatioVer attribute and sliding U_r=1e20 / IsDuctilityFixed=false. A fresh Dhir construction check after these changes still matches all 77,080 tested spring definitions following the material-146 foundation reset.
- Polygon and node overloads of `Interface.SetSpring` differ. Source tracing confirms that the supported Quad-Quad builders accept only four-vertex contacts and do not enter the polygon constructor. Polygon construction for other element families remains outside the supported Quad/line-Restraint domain; see the contact audit below.
- `NR=False` now has direct original-assembly routine coverage (see below). The Dhir Newton workflow does not independently exercise this branch.
- Complete native pushover private spring histories and global displacement vectors are not saved at every step. Missing and NULL measurements remain unavailable, not inferred matches.

Tiny arithmetic differences can affect force-sign-dependent phase transitions. Numeric tolerance alone therefore does not establish phase parity. The strict gate retained exact phase comparisons throughout the successful Dhir comparison. See [Dhir progress](dhir-full-chain-native-parity-progress.md) for the latest completed run and output replay.


## Additional branch validation, 2026-10-15

Commits `1169a0f` and `19e9412` add zero-friction hysteretic diagonals and native
restraint-axis/material-constructor corrections. The full suite passes 771
tests and 1,470 subtests, with 14 skips. A fresh Dhir model with foundation
material 146 still matches all 77,080 checked native spring definitions and
the tested geometry fields exactly. No native computational objects are reused
in Python.

[Compact branch evidence](../../release-evidence/dhir/2026-10-15-masonry-branches.json)
records fixture hashes, coverage and limitations. These checks do not repeat the
complete Dhir nonlinear chain and do not replace a full native structural-chain
reference for the new zero-friction branch. Subsequent NR=False and polygon
call-path checks are recorded below. Omitted material-property defaults still
need separate native coverage.

## Linear normal-force branch, 2026-10-15

The original `Interface.ComputeFlexdef`, `Interface.ComputeDN(A, false)` and
`Quad.ComputeDN(..., false)` are invoked by
`tools/csharp-diagnostics/Invoke-LinearNormalForceOracle.ps1`. The committed
`csharp_linear_normal_force_2026_1_1.json` fixture records original assembly
provenance and doubles as binary bit patterns. Nine cases cover free interfaces,
each restraint side, empty afference rows, repeated global DOFs, cancellation,
repeated edge registrations, missing interfaces and unrelated-parent area.

Python now evaluates this formerly rejected branch using compiled kernels,
the current global correction and the current local stiffness. It preserves
C# projection and reduction order, including `force - increment` cancellation.
Tests compare all checked local flexural corrections, interface normal increments,
Quad increments and stresses exactly. Dense-runtime coverage deliberately leaves
object spring forces stale to verify that authoritative trial/committed buffers
are used. Input validation rejects missing displacement data, invalid DOFs and
invalid local stiffness dimensions. Existing Newton evaluation is unchanged.

The full suite passes 773 tests and 1,479 subtests, with 14 skips. These routine
fixtures qualify this calculation branch; they do not establish end-to-end
linear-analysis parity or extend the prior full-chain Dhir qualification.

## Polygon call-path audit, 2026-10-15

Checking the overloaded spring factory alone suggested an additional masonry
construction branch. Following its callers narrows the scope: original
`InterfaceOperations.GIQuadQuadParallel` (line 648), `GIQuadQuadSerial`
(line 808), and `GIQuadQuadIteration` (line 968) require a positive intersection
and exactly four output vertices before building an interface. They use the
node-based builder. The separate builder at line 1983 dispatches lists longer
than four vertices to `BuildInterfacePoligonal`; that does not make arbitrary
polygon contacts part of the supported Quad-Quad path. Its triangulated spring
factory must not be substituted for the original Quad-Quad admission rule.

`Invoke-QuadContactIntersectionOracle.ps1` invokes the original
`UtilityLibrary.Matematics.Operations.FindIntersectionBetweenQuadrilaters`
with the recorded node tolerance. Four fixtures cover partial rectangles,
containing and crossing diamonds, and corner overlap. Python matches the native
admitted/rejected outcome in all four cases and the exact vertex sets for both
admitted contacts. Native intersection itself returns an empty list for the
crossing-diamond and corner-overlap fixtures, despite geometric overlap. These
are observed original routine outcomes, not evidence of general-purpose polygon
clipping correctness. No new geometry rule is introduced into Python.

These selected fixtures and caller inspection do not qualify every skew contact,
Triangle.NET polygon triangulation, or unsupported Solid/Vertex element paths.

After both additions, the full suite passes 774 tests and 1,483 subtests,
with 14 skips. No full nonlinear chain was rerun in this branch audit.
