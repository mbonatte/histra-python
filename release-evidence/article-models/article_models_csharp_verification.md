# Article Models: Python vs C# verification

Warning tolerances are unchanged: force absolute `1e-3`, force relative `1e-5`, active-residual L2 `1e-4`.

| Mode | Model | Steps | Unsafe | Max reaction error (kN) | Max model-point error (mm) | C# parity |
|---|---|---:|---:|---:|---:|---|
| authored | Bridge_1 | 112/297 | 112 | 16.4541 | 0.064037 | NOT RELEASE-READY |
| authored | Bridge_1_traversal_layers | 204/204 | 204 | 77.7456 | 0.486835 | NOT RELEASE-READY |
| authored | Bridge_2 | 430/430 | 430 | 2.56325 | 0.00822544 | NOT RELEASE-READY |
| authored | Bridge_3.1_Coarse | 46/1065 | 46 | 0.0238037 | 0.000140369 | NOT RELEASE-READY |
| authored | Bridge_3.1_Multiring | 91/91 | 91 | 2.33365 | 0.00531718 | NOT RELEASE-READY |
| authored | Bridge_3.2 | 338/338 | 338 | 0.892609 | 0.0131071 | NOT RELEASE-READY |
| authored | Bridge_3.3_2_Zhang_drucker | 167/167 | 167 | 50.0133 | 0.615569 | NOT RELEASE-READY |
| authored | Bridge_3.3_2_Zhang_drucker_tol | 151/151 | 151 | 12.1721 | 0.0350963 | NOT RELEASE-READY |
| authored | Bridge_3.4_Zhang | 179/179 | 179 | 60.5843 | 0.342332 | NOT RELEASE-READY |
| authored | Bridge_3_abutment | 622/622 | 622 | 1.1637 | 0.000490248 | NOT RELEASE-READY |
| authored | Bridge_5.1_coarse | 1585/1585 | 1585 | 177.333 | 1.66406 | NOT RELEASE-READY |
| authored | Bridge_5.1_load_spandrel | 113/113 | 113 | 42.8981 | 0.00982007 | NOT RELEASE-READY |
| authored | Bridge_5.1_load_spandrel_backfill | 255/255 | 255 | 76.7813 | 0.0480068 | NOT RELEASE-READY |
| authored | Bridge_5.2_coarse | 1767/1780 | 1767 | 23.7319 | 0.218435 | NOT RELEASE-READY |
| strict | Bridge_1 | 0/297 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_1_traversal_layers | 4/204 | 0 | 2.43187e-05 | 0.0341453 | NOT RELEASE-READY |
| strict | Bridge_2 | 0/430 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.1_Coarse | 0/1065 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.1_Multiring | 0/91 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.2 | 0/338 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.3_2_Zhang_drucker | 0/167 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.3_2_Zhang_drucker_tol | 0/151 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3.4_Zhang | 0/179 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_3_abutment | 0/622 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_5.1_coarse | 0/1585 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_5.1_load_spandrel | 0/113 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_5.1_load_spandrel_backfill | 0/255 | 0 | n/a | n/a | NOT RELEASE-READY |
| strict | Bridge_5.2_coarse | 0/1780 | 0 | n/a | n/a | NOT RELEASE-READY |

`strict` uses ForceMoment on every nonlinear stage and tightens, never loosens, the HRX convergence tolerance to the unchanged audit limit.

## Article source data

NOT RELEASE-READY
- missing Figure 9 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_09.csv
- missing Figure 12 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_12.csv
- missing Figure 13 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_13.csv
- missing Figure 15 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_15.csv
- missing Figure 17 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_17.csv
- missing Figure 20 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_20.csv
- missing Figure 22 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_22.csv
- missing Figure 24 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_24.csv
- missing Figure 25 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/figure_25.csv
- missing Table 1 source file: /home/mauricio/coding/histra-python/release-evidence/article-source-data/table_01.csv
