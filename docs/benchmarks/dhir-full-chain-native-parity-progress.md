# Dhir full-chain comparison, 2026-10-14

Full output parity is **not yet qualified**. The new C# 2026.1.1 reference contains 20 Vert commits, 10 constant-load commits and 58 pushover commits. Pushover attempt 59 fails with code -2; saved step zero is initial state, not a commit.

Python independently generates the model from geometry and reapplies material 146 to all 148 foundation interfaces. It does not reuse native computational objects or histories. All 77,080 spring identities are checked at every compared state, along with local element outputs, reactions, model points and available energy/vector measurements.

Two source differences were corrected in separate commits with native-backed unittest fixtures:

- `5ba058c`: interface flexural laws now use the original Float32 axis dot product and orientation blending, including the original curve-selection rules. This fixes the first mismatch at pushover step 6.
- `6d17b1c`: scalar and batch diagonal stiffness use the original Framework power operation and multiplication association. Six model quads had a last-bit difference in their squared kinematic factor. `cosAlfa` also now follows the source's explicit multiplication.

After both changes, the strict gate passes Vert, constant load and pushover commits 1–22. At commit 23 one transverse spring, interface 356 / group 1 / spring 6, has Python phase 5 (`Reload_t`) versus native phase 4 (`Unload_c`). All available numeric fields at that state pass. The gate remains failed; no phase tolerance or reference-state injection was introduced.

The preceding commit-22 force in the projection-corrected run was +5.204170427930421e-18 in Python versus -3.469446951953614e-18 in C#. The source uses force sign in its subsequent phase selection. Original `SpringHysteretic.setTrialStrain` calls with Python's parameters and committed history reproduce Python's force and phase, even with the C# endpoint displacement. This establishes that those tested inputs follow the native routine; it does not establish exact equality of the unrecorded native internal history. A diagnostic G15 rounding experiment also retained the step-23 mismatch and was not added to production.

A separate diagnostic run before the two construction corrections explicitly retained phase mismatches while continuing. It reached 58 commits and naturally failed attempt 59, with identical iteration counts and exactly equal reaction vectors at every saved state. All available numerical fields passed; maximum spring force difference was 2.2634649710084886e-10 kN and maximum spring displacement difference was 7.06072353362508e-13. This is useful localization evidence, **not qualification of the current implementation or full output parity**.

The native results contain no complete pushover `SpringStates` history or full global pushover displacement vector. NULL per-spring energy measurements remain unavailable. The independent equilibrium diagnostic also continues to report failures under the source Work acceptance criterion; output parity does not qualify strict equilibrium acceptance.

The full unittest suite after the changes passes 730 tests and 875 subtests, with 23 skips. [Compact evidence](../../release-evidence/dhir/2026-10-14-full-chain-progress.json) records reference hashes and the first strict mismatch. Complete paired arrays remain in the local audit folders `dhir-full-chain-native-quad-power` and `dhir-full-chain-phase-probe`.

The next native run needs the targeted trace helper, which now captures interfaces 272 and 356 including envelope coefficients and committed/trial hysteretic history. Its original-assembly smoke test verifies those fields and successful log flushing. The helper is installed in the separate diagnostic application; original installed solver assemblies and reference files are unchanged.
