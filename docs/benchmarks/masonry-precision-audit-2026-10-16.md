# Masonry precision-boundary audit, C# 2026.1.1

This pass follows types and expression order through the supported masonry
pipeline, including inputs that did not yet fail a global benchmark. It extends
the [construction and update audit](masonry-source-audit-2026-10-14.md).
It is ongoing; an inventory match or a passing isolated routine does not prove
every independently converged structural history matches.

## Rules and evidence

Preserve C# `Single` storage, arithmetic rounding after each Single operation,
and promotion to `Double` at the actual consumer. Do not convert complete
constitutive routines to Single: their state and calculations are Double.
Maintain scalar and compiled implementations together. Native routine tests
retain their exact comparisons; global numerical-library tolerances require
separate complete-history and stopping validation.

The original Framework assemblies are called using Windows PowerShell 5.1.
The oracle scripts record assembly hashes. Python solves start from geometry;
native saved interfaces and histories are comparison data only. Step zero is
excluded from committed counts.

| Boundary / original source | Python consumer and tests | Finding / status |
| --- | --- | --- |
| `AdvancedOptionsDefault`: `ToleranceNode`, `TolerancePlane` Single; `InterfaceImax` Double | `hr_loader`, `prepare_model`; `test_csharp_geometry_setting_precision` | Preserve storage for HRX and programmatic inputs. Original property values captured in a native fixture. Fractional-tolerance topology needs broader structural coverage. |
| `Operations`, XNA `Vector3`, `Quad.SetGeometry`, contact/fibre construction | `quad_geometry`, `quad_faces`, `intrinsic_coordinates`, `csharp_fibre_geometry`; existing native geometry/contact/intrinsic tests | Single vectors and ordered reductions retained. Native contact admission is distinct from a generic polygon clipper. Linux-only Sin tolerance remains limited to the specified geometry test. |
| `SpringOperations.SetInterfaceTrasvSpring`, `Operations.Area` | scalar/batched `spring_assignment`; `test_csharp_polygon_area` | Corrected restraint cell area to native Single projection/shoelace. 93 original polygons. |
| `MasonryMaterial`, `ConstitutiveLawOperations`, orthotropic interface selection | `material_selection`, spring construction; native moduli/default/blend/restraint tests | Existing native-backed checks cover property conversion, Single axis alignment, ordered blending and elastic/nonlinear law dispatch. This is not coverage of every possible material curve. |
| `LoadTemplateManager.GetCoefficient` | `load_assembly`; `test_csharp_load_coefficients` | Corrected intermediate Single products including secondary coefficients. 540 original cases across all 26 supported primary coefficient types. |
| `GenerateLoadsForceAnalysis`, `Quad.ComputeNodalForce` | `load_assembly`, `quad_loads`; native direction/line-load tests and `test_masonry_reference_models` | Self-weight direction multiplication rounds before promotion. 448 fresh original load-vector entries cover fractional coefficients, oblique directions, static and modal loads. |
| Modal load direction and directional mass inputs | `load_assembly`; wall modal and fresh-load fixtures | Native modal direction is (1,1,1); line loads carry all specified directional mass factors. Corrected prior missing horizontal mass. |
| `Quad.ComputeLocalMassfromSelfWeight`, `ComputeLocalMass` | `mass_matrix`; `test_modal_analysis` | Node coordinates, normals, thickness, centre and axes stored Single then promoted. Length/cos/sin and integration remain Double. Mass integration tests retain documented floating-point tolerances. |
| `SpringHysteretic`, `SpringCoulomb03`, elastic spring updates | scalar springs and `hysteretic_batch`; native cyclic/update/commit/energy fixtures | Core state is Double. Display-only Single plasticity/ductility getters are not grounds for rounding core history. Independent wall phase/history differences remain open. |
| Interface local stiffness, forces, normal-force cache and global assembly | scalar elements and compiled assembly; native interface-stiffness/normal-force/local-displacement fixtures | Preserve ordered reductions, projection increments and force-minus-increment cancellation. Initial wall K and first native linear solve matched exactly in the preceding wall audit. |
| `LineSearch.NewLineSearch`: tolerance / min/max eta Single | `_new_line_search`; native analysis-setting fixture and existing search traces | Corrected factory promotion; direct search defaults retain their native Double values. |
| `Analysis.MaxArcLengthRay` Single; `ArcLength.Commit` | `arc_length`; native analysis-setting fixture | Default C# mode caps squared state by the native field directly. Explicit stable mode retains its alternative squared-radius cap. |
| `LoadReductionRatioToStopValue` Single | `nonlinear_step`; native setting and adjacent-double boundary tests | Strict comparison uses promoted Single threshold. |
| `StaticNonLinearAnalysis.Execute`: `CheckSecantStiffness` / Single `SecantStiffnessRatio` | `secant_stiffness`, called before integrator commit | Found parsed-but-unused setting. Implemented source branch, first graph-column slope, negative/softening/recovery and UpdateK fallback propagation. Tests are source-derived; an independent native whole-Execute fixture for this setting remains outstanding. |
| `ModalValues.Set`, `Pseudovectors.ComputeUmax` | `modal`; four native wall modal fixtures | Modal UMax is stored Single, eigenvectors remain Double. Corrected native `UMaxX/Y/Z` column spelling and require every available native field to be present. |

## Inventory and remaining work

`tools/csharp-diagnostics/inventory_precision_boundaries.py` inventories numeric
declarations/casts with line numbers and source hashes across SolverRuntime,
MatrixManager, model objects, relevant model-management helpers and utility
mathematics. Run it with `--source-root` pointing at the decompilation and
`--output` in the ignored diagnostic directory. Its candidates include
unsupported and display paths; the tool deliberately produces no pass verdict.
Implicit promotions and overloaded operators still require source review.

The inventory, including model-load regeneration, contains 317 files and 14,690 candidate lines. Those
numbers describe the search surface, not completed manual review.

The remaining audit includes P-Delta load regeneration, less-used supported
input branches and fractional-tolerance contact outcomes. Source inspection
has already identified a P-Delta direction discrepancy requiring a native
regression: `ModelLoadOperations.ComputePDeltaLoads` uses template `Dir(quad)`
for line loads, while Python's scalar and compiled-plan builders substitute the
analysis direction when `IsSeismic` is true. Its displacement subtraction also
needs checking against `Quad.DisplacementsCurrent` before changing formulas.
Dynamic/Adaptic and
non-masonry properties stay outside this task. Fields such as
`ReduceRayArcLength` must not be implemented solely because they exist in the
model: a numerical consumer must first be established in the original code.

The four wall references do not currently establish full internal-history
parity for the isotropic and zero-friction cases. Preserve raw phase/history
differences in the [wall comparison report](masonry-wall-native-parity-2026-10-15.md).
The Article model gate remains unavailable on this computer. Current package
artifacts predate these fixes and need rebuilding before release qualification.

## Regression after merging the GitHub refactor

The incoming commits `92bb7c4` and `e5ef0f6` were merged with the pending
analysis-control precision changes. Eight fresh wall chains were then rerun
with native UMFPACK, AMD ordering and two refinement steps: Vert has 10 commits
and Reversal has 32 in each chain. Excluding the repeated Vert chains and step
zero gives 296 unique commits and 100,640 spring records. Every available
table/field comparison report is identical to the preceding wall audit,
including raw differences, branch mismatches and unavailable fields. Native
Results hashes remain unchanged. This verifies no regression on those inputs;
it does not waive the previously reported internal-history differences.

Local diagnostic evidence is stored in
`four-wall-precision-merged-static-comparison/comparison.json` under the
comparison directory, separate from the original saved results.
