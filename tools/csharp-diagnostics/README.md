# Native C# restart diagnostics

This development tool adds calls to an independently compiled C# trace helper around twelve methods in the original HiStrA 2026.1.1 `SolverRuntime.dll`. It preserves the original solver instructions and branches, rather than rebuilding numerical methods from decompiled source. The installed application and reference models are not modified. Use only a separate application copy and separate model/results copies.

The helper always appends and immediately flushes TSV records, including successful runs, to `app/parity-logs/trace-<UTC>-<PID>.tsv`. It records restart and resisting-force baseline preparation; both load-step overloads; Newton convergence messages, errors and return codes; rollback; commits; and result-save calls. Step-zero result-save calls remain explicitly identifiable by their original arguments.

Before/after snapshots cover interfaces 681, 1806, 863 and 5818 and Quad 1111. They include interface local displacement, transverse/shear/out-of-plane spring U/F/history, diagonal state, and the distinction between base spring U and committed/trial strain. These are diagnostic samples selected from the current first-step discrepancy; complete committed outputs still come from the `.Results` database. Global vectors are abbreviated to sixteen entries to keep logging bounded.

Requirements: Windows, .NET Framework 4.8, .NET 10 SDK and dnSpy's dnlib assembly. Build from Windows PowerShell:

```powershell
.\Build-Diagnostic.ps1 -InstalledRoot 'C:\Program Files\Gruppo Sismica\HiStrA Bridges 2026.1.1' -DiagnosticRoot 'C:\Users\mbonatte\Documents\Histra\csharp-diagnostics-2026.1.1' -DnlibPath 'C:\Users\mbonatte\Downloads\_Organized_Downloads\Software\dnSpy-net-win64\bin\dnlib.dll'
```

`Test-Diagnostic.ps1` calls the instrumented original assembly without an error, verifies flushed success and convergence messages, before/after commit and rollback records, and round-trip native spring U/Cstrain snapshots. This is a diagnostic smoke test, not an end-to-end structural validation of the instrumented GUI application. The next full model run must be compared with the original reference to establish that the logging does not alter its outputs.

For the current experiment, open the diagnostic `app/HiStrA.exe`, open the model copy under the diagnostic `model` folder, unlock that copy and rerun **Vert then TLM_Constant_UDL** with the saved settings and foundation material 146 unchanged. Stop before pushover, save the model/results and retain the TSV log. The purpose is to determine whether the first constant-load displacement offset arises during restart, failed iterations/rollback or a different transition. A rollback defect is not established as the cause of the saved reference discrepancy yet.
