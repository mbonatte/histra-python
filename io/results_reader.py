"""Reader for the HiStrA .Results SQLite database."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Dict, List


def _connect(results_path: str | Path) -> sqlite3.Connection:
    p = Path(results_path)
    if not p.exists():
        raise FileNotFoundError(f"Results database not found: {p}")
    return sqlite3.connect(str(p))


def available_steps(conn: sqlite3.Connection, analysis_key: int, combination: int = 1) -> List[int]:
    """Return ordered list of Step integers present for the given analysis/combination."""
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT Step FROM QuadStates WHERE AnalysisKey=? AND Combination=? ORDER BY Step",
        (analysis_key, combination),
    )
    return [r[0] for r in cur.fetchall()]


def read_quad_states(
    results_path: str | Path,
    analysis_key: int,
    combination: int = 1,
    step: Optional[int] = None,
) -> Dict[int, List[float]]:
    """Read Quad U1..U7 from the .Results DB.

    If `step` is None, the LAST available step is used.
    Returns dict keyed by Quad key, with 7 U values.
    """
    conn = _connect(results_path)
    try:
        if step is None:
            steps = available_steps(conn, analysis_key, combination)
            if not steps:
                return {}
            step = steps[-1]
        cur = conn.cursor()
        cur.execute(
            "SELECT ParentKey, U1, U2, U3, U4, U5, U6, U7 "
            "FROM QuadStates WHERE AnalysisKey=? AND Combination=? AND Step=?",
            (analysis_key, combination, step),
        )
        out: Dict[int, List[float]] = {}
        for row in cur.fetchall():
            out[row[0]] = [float(row[i + 1]) for i in range(7)]
        return out
    finally:
        conn.close()


def find_results_path(hrx_path: str | Path) -> Optional[Path]:
    """Heuristic: sibling .Results file of the HRX model."""
    p = Path(hrx_path)
    for cand in (p.with_suffix(".Results"), p.parent / (p.stem + ".Results")):
        if cand.exists():
            return cand
    return None


def read_dynamic_vectors(
    results_path: str | Path,
    analysis_key: int,
    combination: int = 1,
    step: Optional[int] = None,
    *,
    size: Optional[int] = None,
):
    """Read global displacement and velocity vectors from C# results.

    When ``step`` is omitted, the latest step present in
    ``DynamicVectorsState`` is selected.  DOF identifiers in the database are
    one-based and are converted to zero-based array positions.
    """
    import numpy as np

    conn = _connect(results_path)
    try:
        if step is None:
            row = conn.execute(
                "SELECT MAX(Step) FROM DynamicVectorsState "
                "WHERE AnalysisKey=? AND Combination=?",
                (analysis_key, combination),
            ).fetchone()
            if row is None or row[0] is None:
                return np.zeros(size or 0), np.zeros(size or 0), None
            step = int(row[0])

        rows = conn.execute(
            "SELECT Dof, U, V FROM DynamicVectorsState "
            "WHERE AnalysisKey=? AND Combination=? AND Step=? ORDER BY Dof",
            (analysis_key, combination, step),
        ).fetchall()
        inferred_size = max((int(row[0]) for row in rows), default=0)
        n = max(int(size or 0), inferred_size)
        u = np.zeros(n)
        v = np.zeros(n)
        for dof, u_value, v_value in rows:
            index = int(dof) - 1
            if 0 <= index < n:
                u[index] = float(u_value or 0.0)
                v[index] = float(v_value or 0.0)
        return u, v, step
    finally:
        conn.close()
