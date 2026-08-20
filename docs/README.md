# Documentation

## Start here

- [Project status](STATUS.md)
- [Standalone HRX analysis](guides/standalone-analysis.md)
- [Analysis chains and interface mutation](guides/analysis-chains.md)
- [Preprocessing](guides/preprocessing.md)
- [Documentation and JSON policy](DOCUMENTATION_POLICY.md)

## Reference

Reference notes describe stable concepts and implementation boundaries. They
should not contain benchmark pass counts, machine-specific timings, or claims
that become false when a new model is added.

## Benchmarks

`benchmarks/` contains model-specific numerical evidence. A benchmark report is
not general API documentation. Each report should identify:

- benchmark/model identity;
- relevant analysis names and keys;
- source commit;
- environment;
- command;
- expected terminal condition;
- tolerance and comparison method.

## Archive

`archive/` preserves audit deliverables, generated source inventories, patches,
old metrics, and superseded reports. Archived files are evidence, not current
guidance.
