# Newton snapshot storage performance, 2026-10-15

Newton iteration snapshots can reuse the previous disposable iteration's dense
spring buffers. Every state field is still copied, with no arithmetic changes.
Step, line-search and independent snapshots retain their separate storage.
Shape, dtype, writable-buffer and alias checks reject invalid reuse before any
buffer is overwritten. Rollback still restores the complete captured state.

On the fresh 16,408-DOF horizontal model (77,080 springs), the dense snapshot
payload is 17,289,024 bytes. Eight alternating 60-snapshot microbenchmark samples
measure a median 4.83x improvement in that copy operation. This is not a whole
solver speedup.

Sequential fresh baseline/optimized profiles use identical native UMFPACK
strategy 3, refinement 2 and AMD ordering. The baseline disables buffer reuse
without otherwise changing the numerical implementation. Both runs reproduce
all checked available C# fields through Vert 20 and horizontal commit 1 exactly,
including the same 2,125 iterations in the horizontal step.

| Profiled horizontal Newton step | Allocate each iteration | Reuse buffers |
| --- | ---: | ---: |
| Total time | 73.913 s | 67.627 s |
| All snapshots | 9.322 s | 5.276 s |
| Dense spring snapshots | 5.989 s | 2.066 s |

This single profiled pair measures an 8.50% reduction in Newton runtime.
Repeated full-chain timings and other platforms are not qualified by that pair.
Full committed-state regression results are recorded separately once complete.
The full suite passes 793 tests and 1,585 subtests, with 14 skips.

The alternative UMFPACK workspace solve was tested but not adopted: although
all 32 tested solutions were identical, it was slightly slower on this matrix.
SuiteSparse documents the workspace API as mathematically identical to the
ordinary solve with explicit reusable workspace; see the
[official header](https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/dev/UMFPACK/Include/umfpack.h).

[Compact evidence](../../release-evidence/performance/2026-10-15-snapshot-reuse.json)
records source ed8a104, raw timing samples and scope. The larger native solve
remains the principal cost; this change does not alter convergence settings,
iteration counts, tangent choices or precision.
