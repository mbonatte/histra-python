# Article Models: Python vs C# verification

Warning tolerances are unchanged: force absolute `1e-3`, force relative `1e-5`, active-residual L2 `1e-4`.

| Mode | Model | Steps | Unsafe | Comparable response | Status |
|---|---|---:|---:|---|---|
| authored | Bridge_1 | 112/297 | 112 | row parity: dR=16.6507 kN; du=0.0638714 mm | NOT RELEASE-READY |
| authored | Bridge_1_traversal_layers | 204/204 | 204 | row parity: dR=77.9778 kN; du=0.685281 mm | NOT RELEASE-READY |
| authored | Bridge_2 | 430/430 | 430 | row parity: dR=2.56152 kN; du=0.00820875 mm | NOT RELEASE-READY |
| authored | Bridge_3.1_Coarse | 1065/1065 | 1065 | row parity: dR=33.8141 kN; du=0.0431371 mm | NOT RELEASE-READY |
| authored | Bridge_3.1_Multiring | 91/91 | 91 | row parity: dR=2.33459 kN; du=0.00531614 mm | NOT RELEASE-READY |
| authored | Bridge_3.2 | 90/338 | 90 | row parity: dR=218.393 kN; du=0.426792 mm | NOT RELEASE-READY |
| authored | Bridge_3.3_2_Zhang_drucker | 167/167 | 167 | row parity: dR=206.91 kN; du=0.614631 mm | NOT RELEASE-READY |
| authored | Bridge_3.3_2_Zhang_drucker_tol | 151/151 | 151 | row parity: dR=2.39139 kN; du=0.00517316 mm | NOT RELEASE-READY |
| authored | Bridge_3.4_Zhang | 153/179 | 153 | row parity: dR=279.98 kN; du=0.6945 mm | NOT RELEASE-READY |
| authored | Bridge_3_abutment | 622/622 | 622 | row parity: dR=9.16396 kN; du=0.00153691 mm | NOT RELEASE-READY |
| authored | Bridge_5.1_coarse | 1585/1585 | 1585 | row parity: dR=170.828 kN; du=0.981441 mm | NOT RELEASE-READY |
| authored | Bridge_5.1_load_spandrel | 113/113 | 113 | row parity: dR=31.2639 kN; du=0.00896841 mm | NOT RELEASE-READY |
| authored | Bridge_5.1_load_spandrel_backfill | 255/255 | 255 | row parity: dR=17.1135 kN; du=0.00763223 mm | NOT RELEASE-READY |
| authored | Bridge_5.2_coarse | 257/1780 | 257 | row parity: dR=424.727 kN; du=0.338733 mm | NOT RELEASE-READY |

`authored` is judged by stored C# rows. `strict` is judged only by its physical load--displacement curve, safe committed states, and physical-displacement spring checkpoints; it is never judged by C# authored row number.

## Article source data

PASS
