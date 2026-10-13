# Dhir Vert: native C# parity validation

Validated for v1.4.2, including the spring-history corrections following v1.4.1.

## Scope and construction

Reference: HiStrA Bridges 2026.1.1 Dhir HRX and Results. This audit covers Vert only. Python recreates geometry, all interfaces, springs and local-to-global mappings from the structural inputs. It applies material 146 (`Soil_Foundation_ONLY_V75_X024`) to all 148 foundation interfaces before Vert. C# computational objects remain comparison references only.

Step 0 is initial, never committed. Both implementations have 10 committed Vert steps. All 77,080 spring identities match: 56,052 transverse, 6,228 shear, 12,456 out-of-plane and 2,344 diagonal.

## Source corrections

- Native Quad face projection, contact containment, node/plane tolerances and Vector3 normalization.
- Native local spring cells and projected fibre stiffness.
- Native float32 ray–plane sliding distances and masonry modulus arithmetic.
- Compiled polygon-strip bisection for shear-DOF coordinates with the original 0.001 stopping tolerance.
- Hysteretic yield-coordinate initialization (`Fy/K`) for scalar and lazy proxy springs.
- Committed Coulomb unloading memory in compiled interface/Quad rows, including snapshot and object synchronization.
- Literal Interface.SetSpring post-ultimate curve reassignment: the selected ultimate displacement also selects its originating curve family, followed by reinitialization. Preserved the preceding E2n/E3n values when the source changes to Parabolic.

Native regression fixtures call original DLL methods. The interface construction oracle calls CombinationSpring, SetUltimateDisplacement and initialize using the literal Interface.SetSpring selection protocol. The final suite passes: **722 tests, 23 skipped, 670 subtests**.

## Every committed spring state

| Step | Maximum spring-force difference (kN) | Maximum spring-displacement difference | Phase differences |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 2.66094526e-08 | 2.1704413e-11 | 0 |
| 2 | 5.1677576e-08 | 3.68619186e-11 | 0 |
| 3 | 7.88400625e-08 | 5.47125785e-11 | 0 |
| 4 | 1.21955108e-07 | 6.94328386e-11 | 0 |
| 5 | 2.05141998e-07 | 9.03080575e-11 | 0 |
| 6 | 3.07127452e-07 | 1.10558836e-10 | 0 |
| 7 | 3.78937415e-07 | 1.36807602e-10 | 0 |
| 8 | 4.5638183e-07 | 1.88115837e-10 | 0 |
| 9 | 5.17635456e-07 | 2.37187246e-10 | 0 |
| 10 | 6.09430238e-07 | 3.00451587e-10 | 0 |

**Every available numeric spring field passes the unchanged comparison thresholds**, including final SpringStates yield coordinates, extrema, unloading phases, contact history and tangent metadata. Interface displacements/forces/moments, Quad states, restraint/model-node displacements, global energy sums, and model-point displacements pass at each available step. One aggregate horizontal reaction field remains outside its unchanged cutoff at step 9. The final saved global displacement vector passes as well.

Final maximum global displacement difference: 1.43e-10. Final maximum reaction-component difference: 2.38e-7 kN. Spring response and all categorical phase/history fields agree; floating-point values are not bit-identical.

## Remaining aggregate reaction difference

Step 9 R1 is 7.152557373046875e-7 kN in Python versus 2.8014183044433594e-6 kN in C#, a 2.086162567138672e-6 kN difference near zero. This exceeds the current 1e-6 absolute cutoff; it is explicitly retained as an open numerical difference. Reconstructing the source formula from each implementation’s saved interface resultants reproduces its recorded reaction exactly. The summation path matches; the difference comes from the slightly different resultants entering float32 projection/cancellation. Native calls also verified all first-six rigid mapping coefficients in 330 cases exactly. The threshold is not relaxed.

## Evidence limits

- Detailed SpringStates and DynamicVectorsState are saved only at final Vert step 10; earlier steps have SpringStatesTmp and the other available state tables. The audit does not invent missing C# histories.
- C# E/Ed/Eel per-spring database columns are NULL for all 77,080 final rows (confirmed directly by SQL). These are unavailable measurements, not zero energies or passing numeric comparisons. Global energy sums are compared separately.
- This validates this Dhir Vert reference in explicit C# compatibility mode. It does not qualify other models, later load stages, modal analysis or independent strict equilibrium. Python retains the separate equilibrium diagnostic.
- Neither thresholds nor existing regression assertions were relaxed. A midpoint interpolation test now uses an exact original-C# oracle instead of an algebraic midpoint assumption.

Original HRX and Results hashes remained unchanged. Raw paired arrays and unfiltered diagnostics are preserved; the numeric summary explicitly separates SQL NULL fields:

`C:\Users\mbonatte\Downloads\_Organized_Downloads\Software\dnSpy-net-win64\histra\python-comparison-2026-10-13\dhir-vert-native-final-history\comparison-numeric-fields.json`

`C:\Users\mbonatte\Downloads\_Organized_Downloads\Software\dnSpy-net-win64\histra\python-comparison-2026-10-13\dhir-vert-native-final-history\static\every-step`
