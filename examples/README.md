# Supplementary analytical example

`analytical_overturning.py` contains independent closed-form overturning and
sensitivity helpers formerly used by the removed sensitivity notebook. It is
source-only reference material, outside the installable `histra` solver and its
C# numerical-qualification boundary. Its formulas use metres and kN as declared
in its docstrings; they do not define the native result-file units.

From the checkout root:

```python
from examples.analytical_overturning import critical_force

capacity_kN = critical_force(weight_kn=100.0, d1_m=0.5, d2_m=2.0)
```

The module requires NumPy. It has no plotting dependency or notebook requirement.
Use the [standalone guide](../docs/guides/standalone-analysis.md) and
[analysis-chain guide](../docs/guides/analysis-chains.md) for supported solver use.
