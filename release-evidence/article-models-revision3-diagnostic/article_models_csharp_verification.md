# Article Models: Python vs C# verification

Warning tolerances are unchanged: force absolute `1e-3`, force relative `1e-5`, active-residual L2 `1e-4`.

| Mode | Model | Steps | Unsafe | Max reaction error (kN) | Max model-point error (mm) | C# parity |
|---|---|---:|---:|---:|---:|---|
| strict | Bridge_3.1_Coarse | 13/1065 | 0 | 80.6407 | 0.593964 | NOT RELEASE-READY |

`strict` uses ForceMoment with Standard Bisection on every nonlinear stage, uses consistent ArcLength line-search projections, and tightens, never loosens, the HRX convergence tolerance to the unchanged audit limit.

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
