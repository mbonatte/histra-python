# Changelog

## 1.0.0 - Unreleased

First private production release of the Python HiStrA masonry solver.

### Included

- Quad/Interface masonry preprocessing, six-face contacts, afference, self-weight,
  load combinations, staged dependencies, restart/state transfer, and interface
  material changes.
- Force- and displacement-controlled nonlinear static analysis with LoadControl,
  ArcLength, ArcLengthLinear, Newton and supported line-search variants.
- ForceMoment, DispRotation, and Work convergence criteria with an independent
  equilibrium audit; strict execution rejects unsafe committed states.
- P-Delta EachStep and EachIteration paths.
- Modal eigensolution, participation, effective mass, and mode-shape projection.
- Explicit capability preflight and solver-strategy advisories.

### Qualification & Verification
 
- Fresh brand-new Python preprocessing enforced across all benchmarks and entry points; never solves on serialized `.hrx` computational objects.
- All 14 Article models benchmarked in authored mode under fresh preprocessing with full step history and curve parity against `Original_article_data.csv`.
- Five-stage interface material chain qualified under fresh preprocessing with 0 unmanaged objects.
- P-Delta gravity strategy matrix requalified with 3 fresh-model repeats recommending `authored-each-step`.
- 100% compiled backend enforcement verified across initialization, restart, and post-mutation boundaries.
- Clean wheel and sdist built, byte-verified against source, and smoke-tested in isolated clean virtual environments.

### Release Status

The implementation, packaging, fresh-preprocessing verification, and local test matrix are complete.
Ready for remote CI execution on push and `v1.0.0` tagging. See `docs/release/v1-release-checklist.md`.
