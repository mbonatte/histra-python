# Dhir Vert: native C# parity progress

Reference: HiStrA Bridges 2026.1.1, Dhir saved HRX and Results. Scope: Vert only.

Python recreates all geometry, interfaces, springs and mappings. It reapplies the user-selected material 146 (`Soil_Foundation_ONLY_V75_X024`) to all 148 foundation interfaces before Vert. C# computational objects are comparison references only. Step 0 is initial; steps 1–10 are committed.

## Implemented source corrections

- Native Quad face projection, contact containment, authored node/plane tolerances and Vector3 normalization.
- Native local cell construction and projected fibre stiffness.
- Native float32 ray–plane distance for sliding stiffness.
- Float32 masonry shear/sliding modulus arithmetic. Corrected native diagonal stiffness differs from the saved reference by at most 4.66e-10.
- Compiled polygon-strip bisection for shear-DOF intrinsic coordinates, using the original 0.001 stopping tolerance. Newton inversion followed a different calculation path.

The original DLL routines supply unit-test oracles, including 110 coordinate cases and a midpoint interpolation case. The compiled coordinate result matches every native oracle exactly. The full suite passes: 719 tests, 23 skipped, 623 subtests.

## Every committed spring state

77,080 springs: 56,052 transverse, 6,228 in-plane shear, 12,456 out-of-plane, 2,344 diagonal. Identities match at all steps.

| Step | Maximum spring force difference (kN) | Maximum spring displacement difference | Phase differences |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 2.66094522e-08 | 2.1704413e-11 | 0 |
| 2 | 5.16775787e-08 | 3.68619184e-11 | 0 |
| 3 | 7.88400674e-08 | 5.47125803e-11 | 0 |
| 4 | 1.21955091e-07 | 6.94328502e-11 | 0 |
| 5 | 2.05141985e-07 | 9.03080679e-11 | 0 |
| 6 | 3.0712741e-07 | 1.10558822e-10 | 0 |
| 7 | 3.78937386e-07 | 1.36807608e-10 | 0 |
| 8 | 4.56381802e-07 | 1.88115846e-10 | 0 |
| 9 | 5.17635467e-07 | 2.37187258e-10 | 0 |
| 10 | 6.09430245e-07 | 3.00451657e-10 | 0 |

The final maximum global displacement difference is 1.43e-10; the maximum reaction-component difference is 2.38e-7 kN. SpringStatesTmp, interface states (including forces/moments), quad states, restraints, model nodes, reactions and recorded model-point displacements pass the unchanged comparison thresholds at every available step. DynamicVectorsState is saved only at the final Vert step and passes there.

## Still open

This is not a claim of bit-identical results or complete detailed-history parity. Final SpringStates has these remaining differences:

- Hysteretic Uy1/Uy2: generated Python objects/proxies retain zero yield-coordinate metadata, while C# SetInitial stores Fy/K.
- Umax2: 624 transverse records differ; trace the compression-history initialization and source update path.
- Coulomb CPhaseUnload_t/CPhaseUnload_c: 673 and 586 records differ; trace committed unloading memory in both scalar and compiled implementations.
- C# per-spring E/Ed/Eel database values are NULL for these rows. They are unavailable comparisons, not numeric errors; global energy comparison is separate.

Do not replace these history fields with C# values in a Python solve or restart. Each correction needs native unit tests and a small commit. Do not relax comparison thresholds.

Raw paired arrays and per-field diagnostics are available in the audit folder below. The original HRX and Results hashes remained unchanged.

`C:\Users\mbonatte\Downloads\_Organized_Downloads\Software\dnSpy-net-win64\histra\python-comparison-2026-10-13\dhir-vert-native-intrinsic\static\every-step`
