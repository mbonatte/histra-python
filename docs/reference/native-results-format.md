# Native simulation results (schema 2.0.0)

`ResultsWriter` exports a summary JSON and compressed NumPy dataset per analysis.
HDF5 is optional; requesting it without `h5py` produces NPZ with a warning.
The schema version is independent of the package version.

```python
from histra import AnalysisSession, SimulationResults, load_model

session = AnalysisSession(load_model("bridge.hrx"))
session.run_to("LiveLoad_1")
files = session.export_session("results", "bridge")
readers = SimulationResults.load_session("results/bridge.session.json")
try:
    case = readers["LiveLoad_1"]
    displacement_mm, total_force_kN = case.get_pushover_curve()
    corners_cm = case.get_quad_displacement_field(step=-1)
    springs = case.get_interface_springs(int(case.mesh_interface_keys[0]))
finally:
    for case in readers.values():
        case.close()
```

## Units and curve semantics

All mesh coordinates, thicknesses, lengths, global displacement translations,
and projected translations are **cm**. Rotations in `fields/U` are radians;
that vector contains assembled generalized DOFs, not shared-node translations.
Interface resultants are kN and interface moments are kN·cm, in each interface's
local reference frame. Exported spring stress is MPa. Raw runtime state arrays
retain internal solver conventions; their force columns are kN, even where
internal variable names say “stress”. Spring stress is `10 * force / area_cm2`.

The summary declares these units under `metadata.units`. Dense datasets also
contain `metadata/schema_version` and JSON-encoded `metadata/units` scalars.
`steps/displacement` stays in cm. Summary curves contain both
`displacement_cm` and `displacement_mm`, and metrics contain both `d_max_cm` /
`d_max_mm` and `d_at_f_max_cm` / `d_at_f_max_mm`.

`pushover_axis` selects the largest absolute change from the initial reaction,
with ties preferring Z, X, then Y. If every change is at most 1e-4 kN,
`pushover_axis` is `resultant` and the force is the absolute reaction magnitude.

- `curve.total_force_kN` is the selected reaction change, or resultant fallback.
- `curve.reference_force_kN` is the absolute selected-axis reaction before
  baseline subtraction, or the absolute resultant for the fallback.
- `curve.load_factor` is the independent dimensionless solver load factor.
- `curve.force_kN` remains an alias for `total_force_kN`; `f_max_kN` uses it.

Control displacement remains the solver's recorded control value. It is not
rebased at each stage. Reaction changes are rebased at the first output state.
Only the initial state and committed steps enter the exported histories;
failed trial steps remain represented in execution outcome/status metrics.

Available elastic/dissipated energy values are exposed in summary curves in
kN·cm, with `null` for unavailable states (including initial snapshots).
Dense energy series are included only when every output state has a value.
An absent initial energy must not be interpreted as zero.

## Topology and deformation

Topology arrays use ascending entity-key order. Dynamic interface arrays and
spring spans use the same interface order, regardless of runtime record order.
The shared-node mesh contains Quad-connected nodes. Auxiliary contact endpoints
are described separately by `mesh/interface_node_keys` and
`mesh/interface_node_xyz` `(N_interfaces, 2, 3)`.

Quad metadata includes material keys, four thicknesses and six face interface
keys. `mesh/quad_interface_keys` has shape `(N_quads, 6)` with `-1` for an empty
face and the first key for an active face. A face may contain **multiple**
partial-edge contacts; use the lossless CSR arrays
`mesh/quad_face_interface_offsets` `(6*N_quads+1,)` and
`mesh/quad_face_interface_keys` for general topology. Flatten faces in Quad
order, then native face order 0..5. C# `DrawCurvaPressioni` considers opposite
faces (0,2), (1,3), (4,5), only when each face has exactly one interface, and
also applies its displayed-element group filter.

Interface metadata includes endpoint keys, length, material key, reference e1
and e3, reference origin, nrow, ncol, actual transverse fibre count and the
restraint flag. `mesh/interface_nspring` is the **actual primary transverse
fibre count**. The model's internal `interface.nspring` is a legacy alias for
`ncol`; using it as a fibre count would truncate the grid. No model field is
changed by export.

`fields/node_displacements` contains the existing shared-node average.
`fields/quad_displacements` `(N_steps, N_quads, 4, 3)` preserves independent
corner translations using the existing C#-parity projection, including the
seventh Quad DOF. It is available even if shared-node projection is disabled.

## Stage-end constitutive state

`AnalysisSession.run` copies export topology and spring state at the analysis
boundary. Exporting a predecessor after running another stage or changing
interface materials uses that predecessor's snapshot. This adds retained
array storage per execution, without changing constitutive integration.

`springs/transverse_offsets` and `springs/sliding_offsets` are uint32 prefix
sums with `N_interfaces+1` entries. Each span slices the corresponding
`force`, `stress`, `phase`, `area` (cm²) and `stress_valid` arrays. A zero-area
sliding spring retains its force, with zero stress as a placeholder and
`stress_valid = 0`; consumers must mask that stress. Transverse values follow primary fibre
row-major order. Sliding values follow in-plane, out-of-plane 0, out-of-plane 1
slots when present. Aliased spring objects occupy repeated component slots;
the raw runtime Coulomb array still deduplicates them. These are **committed
stage-end snapshots**, not per-step spring histories.

Standalone executions without a captured export snapshot use the supplied
model's current runtime. Export these before advancing that model. Inactive
runtimes have no constitutive snapshot arrays; readers must check key presence.

## Portable sessions and compatibility

`export_session` also creates `<bundle>.session.json` with schema version, units,
model filename/hash and every exported analysis's relative summary/fields path.
It copies the source HRX beside the manifest and refuses to overwrite a different
model with the same filename. A summary-only case has `curve_only: true` and a
null fields reference; baseline stages are indexed like every other stage.
The returned Python mapping of analysis names to created paths is preserved.
Rerunning an analysis exports its most recent execution.

Single-analysis manifests use the source model's basename; callers distributing
that pair separately should include the source HRX beside it. NPZ data can be
read without HRX or pickle. Optional application-specific metadata remains the
caller's responsibility, including any paths it embeds.

`SimulationResults.load` retains legacy schema 1 summary/array access and sibling
file discovery. Version 2 readers honor declared field references and reject
missing files or unsupported summary schema versions. Legacy `_mm` summary
values are returned as stored; old schema 1 exports affected by the unit bug
must be re-exported for corrected values. New topology helpers raise `KeyError`
when their arrays are absent in older files.

The external bridge aggregate, existing bridge bundles, viewer adapters and
viewer HTTP endpoints are application artifacts. This schema does not rewrite
those artifacts or synthesize missing Standard analyses. Re-export the desired
analyses and update the viewer to consume the session index and explicit units.
