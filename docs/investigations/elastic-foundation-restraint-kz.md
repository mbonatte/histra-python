# Elastic vertical foundation restraints (`K2` / subgrade modulus `Kz`)

## Scope

This note records the C# convention for an elastic vertical foundation
restraint, the Python implementation, and the evidence used to qualify it.

Supported case:

- a line `Restraint` whose local `K2` is positive (`force / length`);
- every other local direction (`K1`, `K3`, `Kr1`, `Kr2`, `Kr3`) is fixed or free;
- the restraint is attached to one Quad foundation face and has no custom
  geotechnical `MaterialKey`;
- the serialized local frame is orthonormal, aligned with the generated
  interface frame. `e2` may be vertical or horizontal.

Fully fixed restraints are unchanged. Free directions allocate massless DOFs;
they do not carry support stiffness and can introduce mechanisms. Elastic
tangential or rotational directions, and an elastic restraint combined with a
geotechnical material, are rejected explicitly.

For finalized HRX models Python treats the numerical K fields and frame as
authoritative. Native `OpenModelOperations.ReadSerialized` loads those fields,
but `ModelManager.PrepareModel` invokes `PreliminaryOperations` when unlocked or
missing afferences. That invokes `Restraint.Init`, whose `SetRestraintK` can
overwrite numerical values using the behavior flags. A locked native model with
afferences follows a different preparation branch. Python intentionally does not
rewrite HRX stiffnesses from those flags; native behavior requires case-specific
verification. C# source: `UnityServiceClasses/OpenModelOperations.cs`,
`SolverRuntime/ModelManager.cs`, and `Objects/Restraint.cs`.

## C# source trace

### Storage and numerical meaning

- `Objects/Restraint.cs` stores `K[6]` in the restraint local reference system.
  `SetRestraintK` maps the UI behaviour enum to:
  - `Fixed -> -1`;
  - `Free -> 0`;
  - `Elastic` is converted back to `Fixed` by the setter, after which the
    caller writes the numerical stiffness.
- `Objects/GeometryRestraint.cs` exposes the same `K1..K3`, `Kr1..Kr3` fields.
  Setting `U2mechBehaviourType = Elastic` stores `K2 = 0` and changes the
  behaviour back to `Fixed`; `BridgeMesher` then writes the actual `K2`.
- `K1..K3` carry `ForcePerLen`; `Kr1..Kr3` carry `RotationalStiffness`.

### Subgrade modulus conversion

`ModelManagement.Mesher/BridgeMesher.cs`, `generateMasonryFoundation`, writes

```text
K2 = Kz * WidthBottom * (bottom strip segment length)
```

where `Kz` is the subgrade reaction modulus in `force / length^3`, the width is
the out-of-plane foundation strip breadth, and the segment length is along the
bridge axis. The product is the tributary foundation area, so the stored `K2`
is a line support stiffness in `force / length`.

The C# source contains two consecutive assignments to `K2` in this block:

```text
K2 = Kz / num6 * Bf * Wf;
K2 = Kz * num5;          // num5 = WidthBottom * segment length
```

The second assignment wins. Therefore only the tributary-area formula is
observable in the HRX; the first expression is dead code in the supplied
release.

The local axes of the generated restraint are set by `RestraintMesher`:

- `e1` along the foundation line;
- `e2` equal to the parent Quad face normal (vertical for a bottom face);
- `e3 = e1 x e2`.

Therefore the subgrade spring is local direction 2 (`U2`).

### Local DOFs and interface relationship

- `Restraint.ComputeAff(gdl)` attaches an independent global DOF only for
  directions with `K[i] >= 0`. Fixed directions have no restraint DOF.
- `Restraint.ComputeInterfaceAfference` maps local restraint directions into
  the interface's constrained generalized DOFs:
  - `U1 -> interface DOF 6` (in-plane sliding);
  - `U2 -> interface DOF 0` (normal/transverse);
  - `U3 -> interface DOFs 8 and 9` (out-of-plane);
  - `R1 -> interface DOF 4`;
  - `R2 -> interface DOFs 8 and 9` with `+/- L/2`;
  - `R3 -> interface DOF 1`.
- For a restraint without a geotechnical material,
  `SpringOperations.SetInterfaceTrasvSpring` writes the rigid placeholder
  `K = -1`. The interface fibres therefore carry only the Quad-side contact
  stiffness. The restraint support spring is a separate stiffness on the
  restraint DOF, in series with the interface.

### Assembly and a native tangent gap

- `SolverRuntime/ModelManager.ComputeAff` visits Quads first, then Restraints,
  then Interfaces. Python follows that order when elastic restraint DOFs exist.
- `Restraint.GetResistingForce` scatters `-K[i] * U[i]` into the residual, so
  the converged equilibrium includes the support spring.
- **`Restraint.AssembleK(LinearSystem)` is empty in the supplied C# source.**
  The native tangent therefore omits the elastic restraint diagonal; the
  final equilibrium can still be correct, but Newton uses an approximate
  tangent. Python assembles the diagonal explicitly. This is a deliberate,
  documented difference: it does not change the equilibrium equation, but it
  changes the iteration path. Contact branch selection, stopping tolerances,
  convergence failures and path-dependent final states can therefore differ.

### Subdivision trap in the native mesher

`RestraintMesher.addRestraint` copies the parent `GeometryLineRestraint.K`
array unchanged to each generated line segment:

```text
restraint.K = res.K.Clone();
```

When one geometry line restraint spans several Quad columns, the native mesher
creates one `Restraint` per contact but gives each child the full parent `K2`.
That multiplies the subgrade stiffness by the number of Quad columns. The
serialized HRX is the authoritative solver input, so the viewer generator now
writes each child with its own tributary area:

```text
K2_child = Kz * B * L_child
```

The geometry parent still carries `K2_parent = Kz * B * L_parent`; the child
sum equals the parent value. No solver-side rescaling is performed: Python uses
the per-restraint `K2` written in the HRX exactly once. Native C# remeshing
copies the parent stiffness again and can undo this serialized correction;
inspect or correct child stiffnesses after native remeshing.

## Python implementation

### Preprocessing

- `histra/preprocessing/restraint_support.py` classifies each restraint and
  rejects unsupported stiffness patterns with a precise error.
- `assign_restraint_dofs` appends one global DOF per active restraint
  direction after all Quad DOFs and records it in `Restraint.solver_gdls`.
  Fully fixed models therefore keep their previous `GDL` exactly.
- `_assign_interface_afference` ports the C# direction mapping, including the
  axis-alignment signs from the interface and restraint reference systems.
- The generated interface normal points toward its parent Quad, as in C#
  `Interface.Set`; the restraint's own serialized normal may point in either
  direction. A sign maps its normal DOF to the interface.
- `Interface` stiffness and spring construction are unchanged: the interface
  fibres still carry the Quad-side contact stiffness. The `K2` diagonal is
  added once to the global matrix on the restraint DOF by
  `assemble_global_k`.
- The residual adds `-K2 * U2`, and `update_domain` accumulates the restraint
  local displacement in the same way as the interface state. Solver snapshots
  and rollback include the restraint displacement list.

### Solver boundaries

- Fixed restraint directions have no independent restraint DOF and are coupled
  through constrained-interface springs. Active normal and free directions
  have independent DOFs; only positive `K2` adds support stiffness.
- `RestraintStates` export writes the native `U1..U6` values from
  `Restraint.u`.
- Modal analysis with elastic/free restraint DOFs uses a full sparse
  shift-invert eigenproblem with semidefinite mass and checks the full-system
  residual. The support DOFs are reconstructed in the resulting mode shapes.
  This is mathematically equivalent to static condensation when the support
  block is invertible; native C# modal parity remains unverified.

## Evidence

Focused tests: `histra/tests/test_elastic_restraint_support.py`.
`histra/tests/test_foundation_side_restraints.py` also checks all four vertical
faces, fixed and positive `K2`, sign reversals, free DOFs and their condensed
response. Two inclined-side geometry records come from a finalized HRX; they
are serialized frame comparisons, not native C# force or displacement traces.

The reference wall has a 100 cm x 20 cm foundation, so `K2 = Kz * 2000 cm^2`.
The prepared interface has the expected `Nrow`, `Ncol` and `Nrow * Ncol`
transverse fibres. Its fibre sum equals the interface `K[0][0]`; the assembled
support diagonal equals `interface K[0][0] + K2` exactly once.

A `Vert` analysis on the wall gives:

| `K2` (kN/cm) | final control displacement (cm) | `K2 * U2` (kN) |
|---:|---:|---:|
| 10 | 6.952980 | -68.960000 |
| 1,000 | 0.125940 | -68.960000 |
| 1,000,000 | 0.057049 | -68.960000 |
| fully fixed | 0.056980 | n/a |

For this single-support wall, the displacement increment relative to the fixed
case is approximately the applied vertical load divided by `K2`, and the support
reaction is independent of `K2`. This checks the series response for this case;
it does not establish general multi-support or nonlinear C# parity.

## Remaining parity gap

No runnable full C# model solve with a positive `K2` and a corresponding
`.Results` database is available in this workspace. The convention is therefore
verified against the C# source path, not against a native numerical trace.

The known native difference is the empty `Restraint.AssembleK`: C# equilibrium
includes `K2 * U2`, but its tangent omits that diagonal. Python assembles it.
For identical states and an exactly converged root the equilibrium equation is
the same, but nonlinear path-dependent results may differ. A future C# reference
run must compare equilibrium, response history, and branch outcomes.

The generator correction also means HRX files produced by the old native
mesher with duplicated child `K2` values are **not** silently rescaled. Such a
file must be regenerated or its child stiffnesses corrected before comparison.

Native `.Results` restart for a model with elastic restraint DOFs is rejected:
although C# also allocates these DOFs, the restart does not yet restore and
validate their local restraint state and native global mapping. In-memory
`AnalysisSession` chaining preserves support displacement.
