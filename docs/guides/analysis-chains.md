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

## Material-reset registration strategy

C# 2026.1.1 `ReSetInterfaces` rebuilds a changed interface and appends its key
to each Quad parent's edge list again. `Quad.ComputeDN` traverses every entry,
including repeated keys. Python defaults to reproducing that sequence:

```python
session = AnalysisSession(model, interface_registration="csharp")
```

For an explicit sensitivity comparison using unique neighbour links:

```python
session = AnalysisSession(model, interface_registration="single_link")
```

The alternative emits `InterfaceRegistrationWarning` when a Quad material
reset differs from C# registration. The free `change_interface_materials`
function accepts the same keyword. Mutation reports record the selected
strategy and number of appended Quad links. Choose the strategy before starting
the chain and regenerate the model independently for each comparison.

This is a workflow-dependent registration rule, not a blanket multiplication
of diagonal force by two. One material reset adds one reference to the current
interface; later distinct resets append further references. An unchanged
material request adds none. It does not keep separate old/new material springs
or duplicate the interface's global stiffness and reaction assembly.

Both strategies use the existing compiled Quad normal-force reductions.
Neighbour caches and the compiled runtime are rebuilt at a material boundary,
preserving committed state; failures restore interface definitions and links
atomically, including failed session backend validation.

The supplied HiStrA user manual (2025, pages 67–69) describes normal-stress
dependence of diagonal shear resistance and refers to a theoretical manual.
It does not establish that repeated registration after a material reset is an
intentional modelling rule. C# is the behavioural reference; mathematical
correctness remains unverified for this distinction. The `single_link` strategy
is retained for investigation rather than labelled a validated correction.
