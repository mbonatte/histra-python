# Analysis chains and interface material mutation

`AnalysisSession` executes HRX-defined dependency chains while keeping committed
model and constitutive state in memory.

```python
from histra.io.hr_loader import load_model
from histra.solver import AnalysisSession

model = load_model("model.hrx")
session = AnalysisSession(model, on_log=print)

for definition in session.dependency_chain("LiveLoad_1"):
    print(definition.key, definition.name)

results = session.run_to("LiveLoad_1")
```

The HRX remains authoritative for analysis definitions, predecessor keys, load
metadata, integration methods, solution methods, convergence settings, and
termination conditions.

Selected interfaces can be rebuilt between committed analyses:

```python
session.run("Vert")
session.change_interface_materials(
    interface_keys=[359, 360, 361, 362],
    material_key=147,
    preserve_committed_state=True,
)
session.run("scour_1")
session.run("LiveLoad_1")
```

This is an analysis-boundary operation. It is not a substitute for arbitrary
stage mutation inside a load-control step.
