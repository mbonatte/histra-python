# Benchmark Results

## Final full run

Completion code: 0. Runtime: 34.450 seconds. Committed steps: 1, 2, 3, 4, 5. All values finite.

| Step | LF | Iter. | Work error | Residual norm | Increment norm | Relative U error | Max abs U error |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.2 | 3 | 8.474e-5 | 6.705e1 | 1.454e-4 | 1.311e-14 | 6.365e-17 |
| 2 | 0.4 | 11 | 9.806e-5 | 1.380e2 | 2.130e-4 | 5.930e-2 | 7.257e-4 |
| 3 | 0.6 | 16 | 9.901e-5 | 1.826e2 | 1.494e-3 | 1.799e-1 | 3.338e-3 |
| 4 | 0.8 | 7 | 6.155e-5 | 2.643e2 | 4.238e-4 | 1.915e-1 | 4.313e-3 |
| 5 | 1.0 | 38 | 8.777e-5 | 2.170e2 | 3.762e-5 | 1.153e-1 | 5.408e-3 |

All load-factor errors are within 1e-15. Step ordering is exact. Only step 1 satisfies the displacement criterion.

## Improvement over baseline

The untouched solver stalled during step 2 after committing step 1 with relative error 2.214e-3. The corrected solver completes all steps, and step 1 is reduced to roundoff-level error. Normal-force coupling and the correct out-of-plane interface stiffness were necessary to move the divergence from the initial response and permit the full run.
