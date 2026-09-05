# Revision-3 strict Article run: interrupted

Command:

```console
python -m histra.tools.article_models_benchmark \
  --models-dir my_model/Article_Models_Benchmark \
  --run-mode strict --max-workers 4 \
  --output-dir release-evidence/article-models-revision3-strict \
  --allow-incomplete
```

The run started at 2026-09-05 11:23 WEST and was interrupted at 11:56 WEST
after roughly 32 minutes without a fourth checkpoint. The interruption was
recoverable: three complete revision-3 checkpoints are retained and can be
resumed by rerunning the command with `--resume`.

| Model | Strict steps | Unsafe commits | Terminal result | Runtime |
|---|---:|---:|---|---:|
| Bridge_3.1_Coarse | 13/1,065 | 0 | configured displacement limit | 9.66 s |
| Bridge_3.1_Multiring | 9/91 | 0 | configured displacement limit | 43.69 s |
| Bridge_3.2 | 1/338 | 0 | nonconverged | 364.61 s |

None passes the Article release gate. The unfinished workers produced no
checkpoint and therefore provide no acceptance evidence. The coordinator did
not write an aggregate report because the run was interrupted.
