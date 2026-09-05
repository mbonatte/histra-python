# Solver strategy benchmark methodology

Benchmark at least one gravity/seating stage, force-controlled pushover,
displacement-controlled pushover, P-Delta EachStep, P-Delta EachIteration,
coarse mesh, fine mesh, and near-collapse stage. Evaluate every supported
method/integrator/criterion combination that is constructible for that scenario.

A candidate qualifies only when strict equilibrium passes, the reference range
is covered, and response metrics pass the same peak/RMSE/area/stiffness/peak-
displacement limits used by the Article gate. Compare runtime, nonlinear
iterations, tangent factorizations, and peak memory only among qualifying
candidates. Save the exact command, HRX hash, environment, repetitions, warm-up
policy, raw observations, aggregate statistics, and selected recommendation.

Do not publish “always”, “guarantees”, or fixed speedup language from a single
model. The public advisor contains stable codes and model-qualified reasons; it
does not modify HRX settings.

The canonical runner accepts a JSON matrix and writes a versioned raw report:

```json
{
  "scenario": "coarse live-load pushover",
  "hrx": "my_model/Article_Models_Benchmark/Bridge_3.1_Coarse.hrx",
  "target": "Second",
  "max_steps": 5,
  "baseline_id": "force-bisection",
  "candidates": [
    {"id": "authored"},
    {
      "id": "force-bisection",
      "adaptive_convergence_criteria": "ForceMoment",
      "method": "StandardBisectionLineSearch",
      "csharp_line_search_compatibility": false,
      "analysis_overrides": {
        "Vert": {"adaptive_convergence_criteria": "ForceMoment", "method": "StandardBisectionLineSearch"},
        "First": {"adaptive_convergence_criteria": "ForceMoment", "method": "StandardBisectionLineSearch"}
      }
    }
  ]
}
```

```console
python -m histra.tools.strategy_benchmark matrix.json \
  --output release-evidence/strategy/coarse-live-load.json
```

The report includes committed steps, unsafe count, iterations, linear solves,
factorizations, runtime, peak resident memory where the OS exposes it, response
metrics, qualification, and the fastest qualifying candidate.

The baseline must itself be a safe, accepted response. An authored C# strategy
that fails the independent equilibrium audit belongs in the matrix as
compatibility evidence, but it must not be used as the correctness baseline.
ArcLength matrices may additionally vary `csharp_line_search_compatibility`,
`arc_length_procedure`, `dr2`, predictor caps, adaptive-radius behavior, and
bounded cutback settings. These values are recorded with each candidate; they
must not be changed implicitly by the public advisor.

The current P-Delta gravity matrix executes the complete five-increment range.
All measured `EachStep` and `EachIteration` Standard line-search variants
preserve the Bisection baseline response and pass strict equilibrium. The
authored Modified Regula-Falsi `EachStep` configuration is also safe and was
fastest in the recorded single run. This qualifies the gravity scenario only;
it does not replace a P-Delta live-load or near-collapse gate.
