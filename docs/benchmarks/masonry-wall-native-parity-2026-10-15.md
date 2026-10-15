# Four masonry walls: native comparison, 2026-10-15

The four fresh wall inputs now have user-generated HiStrA 2026.1.1 references.
Python rebuilds each computational model from the original unrun HRX; native
HRB metadata and Results are read-only references. Every case has 10 committed
Vert steps and 32 reversal steps in each of two combinations: 296 unique static
commits and 100,640 spring records. Step zero is excluded from those counts.

## Modal line-load correction

The first comparison exposed missing modal direction and mass-factor handling
in Python's direct line-load generator. Original
`ModelLoadOperations.GenerateLoadsForceAnalysis` forces modal direction to
`(1,1,1)` for HiStrA. `Quad.ComputeLineLoad` then calls
`LoadTemplateManager.ComputeMassNodalForce`, multiplying each component by its
load condition's Single `MassInDirX/Y/Z` factor before integration.

The previous Python path used the static load direction and omitted those
factors. On these inputs, its total X/Y mass was 0.00913726 instead of the
native 0.07032429, materially changing frequencies. The corrected path matches
all 224 target load entries exported by the original routines across two mass
factor settings and four analyses, including ordinary static loads. Portable
tests also cover both saved values of IsSeismic.

All eight modal comparisons now reproduce the saved mode count. C# itself
stopped at the iteration limit before all six requested modes:

| Case | Virgin modes | Modes after reversal |
|---|---:|---:|
| Isotropic | 4 | 5 |
| Orthotropic | 4 | 4 |
| Elastic transverse | 4 | 5 |
| Zero friction | 4 | 4 |

Maximum relative frequency difference is 2.90e-14; minimum shape MAC is
0.9999999999999998. All three total directional masses match exactly.
Native values and shapes, with input/Results hashes, are recorded in
`histra/tests/fixtures/masonry-wall-modal-2026.1.1.json`. Tests solve from fresh
Python geometry, including Vert and reversal before the chained modal case.
Original routine bit-equality tests retain their existing strict assertions.

## Static comparison remains open

Orthotropic and elastic-transverse cases match all checked numeric and phase
outputs exactly in the first audit. Isotropic and zero-friction cases have
near-roundoff force/displacement differences but also different phase and
private history fields; those are not waived as a parity pass. Some private
diagonal history differences are large despite negligible current force.

The actual compiled initial stiffness matrix matches a fresh original C#
assembly exactly on the isotropic case. Replaying Python's first displacement
increment through original `updateDomain`, `GetResistingForce`, and `Commit`
matches U, F and phase exactly for all 340 springs. Both differ from the UI's
saved first-step values in 13 spring displacements/forces, by at most 1.04e-25
displacement and 4.14e-22 kN. This isolates that first difference upstream of
the constitutive update; it does not yet explain all later histories.

The first audit also identifies identical duplicate DynamicVectorsState rows
at reversal combination 1 step 32; they must be checked for identical values
before comparing that vector. Native NULL spring energies and absent private
histories at intermediate steps are unavailable measurements, not passes.

The reviewed v1.6.0 packages predate this correction. They must be rebuilt
before they can include it. The remote Article-model regression remains open.
