# V1.0.0 private release checklist

The package version is `1.0.0`, but the release is not approved and must not be
tagged until every checkbox below is backed by an artifact.

- [ ] Linux Python 3.12, 3.13, and 3.14 CI passes.
- [ ] Windows Python 3.12, 3.13, and 3.14 CI passes.
- [ ] Full suite preserves or explains the `496 passed, 5 skipped, 12 warnings` baseline.
- [ ] Wheel and sdist build; `twine check dist/*` passes.
- [ ] A clean environment installs the wheel and passes import/version/public-API smoke tests.
- [ ] All 14 Article models pass authored and strict gates; strict has zero unsafe commits.
- [ ] Original data validates Figures 9, 12, 13, 15, 17, 20, 22, 24, 25 and Table 1.
- [ ] Strategy benchmark report contains only safe, response-preserving recommendations.
- [ ] Supported-feature matrix, limitations, compatibility mode, and production-safe mode are reviewed.
- [ ] Wheel, sdist, reports, plots, and `SHA256SUMS` are preserved together.

Private upload is intentionally external to this repository:

```console
python -m build
python -m twine check dist/*.whl dist/*.tar.gz
python -m histra.tools.release_manifest dist --output dist/SHA256SUMS
python -m twine upload --repository-url <PRIVATE_INDEX_URL> dist/*.whl dist/*.tar.gz
```

Credentials must be provided by the deployment environment and must never be
stored in the repository or command history.

Install the pinned private release without embedding credentials in a project
file:

```console
python -m pip install --index-url <PRIVATE_INDEX_URL> histra-python==1.0.0
```

Use the deployment environment's keyring, CI secret injection, or index-native
authentication mechanism. Do not commit a URL containing a token.

After all gates pass, create signed tag `v1.0.0`. Only after that tag and compact
evidence are preserved may raw ignored Article assets be retired. Record every
removed absolute path and byte size; retain the canonical harness, provenance,
hashes, reports, sampled golden rows, spring checkpoints, and final plots.
