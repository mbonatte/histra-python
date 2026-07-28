# HiStrA Python

Python implementation and C#-compatibility work for nonlinear structural
analysis of HiStrA HRX models.

> **Project status:** research/engineering integration. Supported workflows are
> benchmarked, but this repository is not a general replacement for every
> topology and analysis path supported by the original desktop application.

## Supported workflows

- Load locked, solver-ready HRX models.
- Preprocess the validated masonry Quad/fixed-Restraint subset of unlocked HRX
  models.
- Generate full-edge and collinear partial-edge Quad–Quad contacts.
- Run `Vert` followed by a chained Live Load analysis entirely in Python.
- Keep committed nonlinear state in memory across HRX-defined analyses.
- Change selected interface materials between committed analyses.
- Compare selected workflows with committed C# SQLite `.Results` references.

Unsupported model topologies fail explicitly instead of producing a partial
computational model.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run commands from the repository root so the local `histra` package is on
`PYTHONPATH`.

## Run an unrun HRX

```bash
python -m histra.tools.run_vert_live path/to/model.hrx \
  --output-dir python-results
```

This workflow preprocesses the model when required, solves `Vert`, preserves
the committed state, runs the chained Live Load analysis, and exports CSV files
plus `run_summary.json`.

## Analysis-session API

```python
from histra.io.hr_loader import load_model
from histra.solver import AnalysisSession

model = load_model("model.hrx")
session = AnalysisSession(model, on_log=print)
results = session.run_to("LiveLoad_1")
```

Material changes can be applied at committed analysis boundaries with
`session.change_interface_materials(...)`.

## Inspect an HRX

```bash
python -m histra path/to/model.hrx --output inspection.json
```

This command loads the model, assembles the global stiffness matrix, and reports
the displacement state embedded in the HRX. It is an inspection/assembly
utility; use `histra.tools.run_vert_live` or the solver API for nonlinear
analysis.

## Tests

```bash
python -m pytest histra/tests -q
```

Long benchmark acceptance tests may be opt-in. See
[`docs/README.md`](docs/README.md) and
[`docs/STATUS.md`](docs/STATUS.md) before interpreting benchmark claims.

## Repository map

- `histra/` — Python package, tests, tools, and currently retained benchmark data.
- `docs/` — maintained guides, status, reference notes, benchmark evidence, and
  archived audits.
- `article-references/` — annotated source literature; migrated to
  `docs/references/articles/` by the cleanup script.
- `examples/` — notebooks and examples. Legacy examples are labeled as such.

## Documentation rule

Current behavior belongs in maintained guides and `docs/STATUS.md`. Numerical
audit reports and generated metrics belong under `docs/benchmarks/` or
`docs/archive/` and must identify their benchmark and provenance.
