"""Modal analysis translated from the active HiStrA C# solver path."""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from pathlib import Path
import time
from typing import Any, Callable, Iterator

import numpy as np
import scipy.linalg
import scipy.sparse as sp
from scipy.sparse.linalg import splu

from histra.io.results_reader import ResultsStateError, find_results_path
from histra.model.model import Model
from histra.preprocessing import inspect_solver_readiness, require_solver_ready
from histra.solver.assembler import (
    assemble_global_k,
    generate_line_loads,
    generate_self_weight_loads,
)
from histra.solver.cancellation import (
    CancelCheck,
    exclusive_solver_access,
    raise_if_cancelled,
)
from histra.solver.mass_matrix import (
    MassMatrixAssembly,
    MassMatrixError,
    assemble_mass_matrix,
    build_translational_pseudovectors,
)
from histra.solver.model_manager import ModelManager, pdelta_enabled
from histra.solver.restart import restore_committed_analysis_state
from histra.solver.solve import _set_initial_state
from histra.types.linear_system import LinearSystem


class ModalAnalysisError(RuntimeError):
    """Raised when a modal analysis cannot produce valid eigenmodes."""


class _DotNetRandom:
    """Legacy .NET ``System.Random`` sequence used by the C# solver."""

    _MBIG = 2_147_483_647
    _MSEED = 161_803_398

    def __init__(self, seed: int) -> None:
        subtraction = self._MBIG if seed == -2_147_483_648 else abs(int(seed))
        mj = self._MSEED - subtraction
        if mj < 0:
            mj += self._MBIG
        self._seed_array = [0] * 56
        self._seed_array[55] = mj
        mk = 1
        for index in range(1, 55):
            slot = (21 * index) % 55
            self._seed_array[slot] = mk
            mk = mj - mk
            if mk < 0:
                mk += self._MBIG
            mj = self._seed_array[slot]
        for _ in range(4):
            for index in range(1, 56):
                self._seed_array[index] -= self._seed_array[1 + (index + 30) % 55]
                if self._seed_array[index] < 0:
                    self._seed_array[index] += self._MBIG
        self._inext = 0
        self._inextp = 21

    def next_double(self) -> float:
        self._inext += 1
        if self._inext >= 56:
            self._inext = 1
        self._inextp += 1
        if self._inextp >= 56:
            self._inextp = 1
        value = self._seed_array[self._inext] - self._seed_array[self._inextp]
        if value == self._MBIG:
            value -= 1
        if value < 0:
            value += self._MBIG
        self._seed_array[self._inext] = value
        return value * (1.0 / self._MBIG)


@dataclass(frozen=True)
class ModalMode:
    """One mass-normalized mode and its C# ``ModalValues`` quantities."""

    mode_number: int
    eigenvalue: float
    angular_frequency: float
    frequency: float
    period: float
    participation_x: float
    participation_y: float
    participation_z: float
    effective_mass_x: float
    effective_mass_y: float
    effective_mass_z: float
    total_mass_x: float
    total_mass_y: float
    total_mass_z: float
    mass_percent_x: float
    mass_percent_y: float
    mass_percent_z: float
    max_displacement_x: float
    max_displacement_y: float
    max_displacement_z: float
    residual_norm: float
    shape: np.ndarray

    @property
    def participations(self) -> tuple[float, float, float]:
        return (self.participation_x, self.participation_y, self.participation_z)

    @property
    def effective_masses(self) -> tuple[float, float, float]:
        return (self.effective_mass_x, self.effective_mass_y, self.effective_mass_z)

    @property
    def mass_percentages(self) -> tuple[float, float, float]:
        return (self.mass_percent_x, self.mass_percent_y, self.mass_percent_z)

    def as_modal_values_row(
        self, *, analysis_key: int, combination: int = 1
    ) -> dict[str, float | int]:
        """Return a row matching the C# ``ModalValues`` database terminology."""
        return {
            "AnalysisKey": int(analysis_key),
            "Combination": int(combination),
            "Step": int(self.mode_number),
            "Wn": float(self.angular_frequency),
            "Fn": float(self.frequency),
            "Tn": float(self.period),
            "GammaX": float(self.participation_x),
            "GammaY": float(self.participation_y),
            "GammaZ": float(self.participation_z),
            "MassaX": float(self.effective_mass_x),
            "MassaY": float(self.effective_mass_y),
            "MassaZ": float(self.effective_mass_z),
            "MTotX": float(self.total_mass_x),
            "MTotY": float(self.total_mass_y),
            "MTotZ": float(self.total_mass_z),
            "Mx_pcent": float(self.mass_percent_x),
            "My_pcent": float(self.mass_percent_y),
            "Mz_pcent": float(self.mass_percent_z),
            "UmaxX": float(self.max_displacement_x),
            "UmaxY": float(self.max_displacement_y),
            "UmaxZ": float(self.max_displacement_z),
            "ResidualNorm": float(self.residual_norm),
        }


@dataclass(frozen=True)
class ModalAnalysisResult:
    """Complete result of one HRX modal analysis."""

    analysis_key: int
    analysis_name: str
    combination: int
    requested_modes: int
    procedure: str
    convergence_criteria: str
    requested_mass_matrix_type: str
    effective_mass_matrix_type: str
    dof_count: int
    stiffness_nnz: int
    mass_nnz: int
    runtime_seconds: float
    modes: tuple[ModalMode, ...]

    @property
    def converged_modes(self) -> int:
        return len(self.modes)

    @property
    def frequencies(self) -> np.ndarray:
        return np.asarray([mode.frequency for mode in self.modes], dtype=float)

    @property
    def angular_frequencies(self) -> np.ndarray:
        return np.asarray([mode.angular_frequency for mode in self.modes], dtype=float)

    @property
    def periods(self) -> np.ndarray:
        return np.asarray([mode.period for mode in self.modes], dtype=float)

    @property
    def mode_shapes(self) -> np.ndarray:
        if not self.modes:
            return np.empty((self.dof_count, 0), dtype=float)
        return np.column_stack([mode.shape for mode in self.modes])

    def modal_values_rows(self) -> list[dict[str, float | int]]:
        return [
            mode.as_modal_values_row(
                analysis_key=self.analysis_key,
                combination=self.combination,
            )
            for mode in self.modes
        ]

    def modal_shape_rows(self) -> Iterator[dict[str, float | int]]:
        """Yield rows matching C# ``ModalShapeValues`` without materializing them."""
        for mode in self.modes:
            for dof, value in enumerate(mode.shape):
                yield {
                    "AnalysisKey": int(self.analysis_key),
                    "Combination": int(self.combination),
                    "Step": int(mode.mode_number),
                    # The C# SQLite table stores zero-based Dof values.
                    "Dof": int(dof),
                    "Val": float(value),
                }

    def as_dict(self, *, include_shapes: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "analysis_key": self.analysis_key,
            "analysis_name": self.analysis_name,
            "combination": self.combination,
            "requested_modes": self.requested_modes,
            "converged_modes": self.converged_modes,
            "procedure": self.procedure,
            "convergence_criteria": self.convergence_criteria,
            "requested_mass_matrix_type": self.requested_mass_matrix_type,
            "effective_mass_matrix_type": self.effective_mass_matrix_type,
            "dof_count": self.dof_count,
            "stiffness_nnz": self.stiffness_nnz,
            "mass_nnz": self.mass_nnz,
            "runtime_seconds": self.runtime_seconds,
            "modal_values": self.modal_values_rows(),
        }
        if include_shapes:
            result["mode_shapes"] = self.mode_shapes.tolist()
        return result


def solve_modal_analysis(
    model: Model,
    analysis: Any,
    combination: int = 1,
    *,
    on_log: Callable[[str], None] | None = None,
    on_progress: Callable[[float], None] | None = None,
    results_path: str | Path | None = None,
    initial_displacement: np.ndarray | None = None,
    restart_from_current_state: bool = False,
    auto_prepare: bool = True,
    should_cancel: CancelCheck | None = None,
    eigensolver_tolerance: float | None = None,
) -> ModalAnalysisResult:
    """Run the C# modal workflow on the supported Python Quad model.

    The stiffness matrix is the current tangent (``alfa=1``), so a modal
    analysis chained to a nonlinear predecessor uses that predecessor's
    committed constitutive state. Modes are mass-normalized before modal
    participation quantities are evaluated.
    """
    with exclusive_solver_access(should_cancel):
        return _solve_modal_analysis_impl(
            model,
            analysis,
            combination,
            on_log=on_log,
            on_progress=on_progress,
            results_path=results_path,
            initial_displacement=initial_displacement,
            restart_from_current_state=restart_from_current_state,
            auto_prepare=auto_prepare,
            should_cancel=should_cancel,
            eigensolver_tolerance=eigensolver_tolerance,
        )


def _solve_modal_analysis_impl(
    model: Model,
    analysis: Any,
    combination: int,
    *,
    on_log: Callable[[str], None] | None,
    on_progress: Callable[[float], None] | None,
    results_path: str | Path | None,
    initial_displacement: np.ndarray | None,
    restart_from_current_state: bool,
    auto_prepare: bool,
    should_cancel: CancelCheck | None,
    eigensolver_tolerance: float | None,
) -> ModalAnalysisResult:
    started = time.perf_counter()

    def log(message: str) -> None:
        if on_log is not None:
            on_log(message)

    def progress(value: float) -> None:
        if on_progress is not None:
            on_progress(float(min(1.0, max(0.0, value))))

    raise_if_cancelled(should_cancel)
    if model.collections is None:
        raise ModalAnalysisError("Model.collections is not initialized.")
    if int(getattr(analysis, "analysis_type", 5)) != 5:
        raise ModalAnalysisError(
            f"Analysis {getattr(analysis, 'key', '?')} is not a modal analysis "
            f"(AnalysisType={getattr(analysis, 'analysis_type', None)})."
        )
    if pdelta_enabled(getattr(analysis, "pdelta_effect", None)):
        raise NotImplementedError(
            "P-Delta modal stiffness is unavailable because the Python port does not "
            "yet include the C# frame/load-generation subsystem."
        )

    readiness = inspect_solver_readiness(model)
    if not readiness.is_ready and auto_prepare:
        log(
            "Preparing unlocked HRX computational model for modal analysis "
            f"({readiness.quad_count} Quads)..."
        )
        ModelManager.prepare_model(model)
    require_solver_ready(model)
    progress(0.05)
    raise_if_cancelled(should_cancel)

    n = int(model.gdl)
    if n < 3:
        raise ModalAnalysisError("Modal analysis requires at least three active DOFs.")
    requested = min(max(1, int(getattr(analysis, "number_of_eigen_modes", 1))), n - 2)

    # Reproduce Program -> SetStatus before PrepareK. For an in-memory chained
    # run, the model objects are already the predecessor's committed state.
    initial_key = int(getattr(analysis, "initial_analysis_key", -100))
    if initial_key < 0:
        if restart_from_current_state or initial_displacement is not None:
            raise ModalAnalysisError(
                "A virgin modal analysis cannot restart from an in-memory state."
            )
        ModelManager.clear_hysteretic_batch()
        state_system = LinearSystem(n)
        _set_initial_state(
            model,
            np.zeros(n, dtype=float),
            np.zeros(n, dtype=float),
            state_system,
        )
    elif restart_from_current_state:
        if initial_displacement is None:
            raise ModalAnalysisError(
                "restart_from_current_state=True requires initial_displacement."
            )
        restored = np.asarray(initial_displacement, dtype=float)
        if restored.shape != (n,) or not np.all(np.isfinite(restored)):
            raise ModalAnalysisError(
                f"Expected a finite initial_displacement vector with shape ({n},)."
            )
    else:
        resolved_results = Path(results_path) if results_path is not None else (
            find_results_path(model.source_path) if model.source_path else None
        )
        if resolved_results is None:
            raise ResultsStateError(
                "Chained modal analysis requires a C# .Results database. Pass "
                "results_path=... or run through AnalysisSession after its predecessor."
            )
        ModelManager.clear_hysteretic_batch()
        state_system = LinearSystem(n)
        u = np.zeros(n, dtype=float)
        v = np.zeros(n, dtype=float)
        restart = restore_committed_analysis_state(
            model,
            resolved_results,
            initial_key,
            int(getattr(analysis, "initial_combination_analysis_key", combination)),
            u,
            v,
            state_system,
        )
        log(
            f"Restored predecessor analysis {restart.analysis_key}, combination "
            f"{restart.combination}, step {restart.step} for tangent modal analysis."
        )

    raise_if_cancelled(should_cancel)
    # C# PrepareModelForAnalysis regenerates the element loads before the
    # modal execution: GenerateLoadsForceAnalysis zeroes every Quad P and
    # rebuilds only the modal analysis's own combination.  GetCombCoeffGravity
    # returns a zero gravity coefficient for modal analyses, so self-weight
    # never re-enters P and only direct line loads can survive.  Without this,
    # a modal analysis chained to a static predecessor would inherit its
    # applied loads as spurious point masses in AssembleM.
    for quad in model.collections.quads.values():
        for index in range(7):
            quad.status.p[index] = 0.0
    analysis_key = int(getattr(analysis, "key", 0))
    generate_self_weight_loads(model, analysis_key, combination)
    generate_line_loads(model, analysis_key, combination)

    log("Assembling current tangent stiffness matrix (alfa=1).")
    stiffness = assemble_global_k(model, alfa=1.0).tocsc()
    stiffness.sum_duplicates()
    if stiffness.nnz == 0 or np.any(~np.isfinite(stiffness.data)):
        raise ModalAnalysisError("The assembled modal stiffness matrix is empty or invalid.")
    stiffness = _validated_symmetric(stiffness, "stiffness")
    progress(0.25)

    raise_if_cancelled(should_cancel)
    log("Computing C#-compatible Quad mass matrix.")
    mass_assembly = assemble_mass_matrix(
        model,
        on_progress=(
            (lambda value: progress(0.25 + 0.20 * value)) if on_progress is not None else None
        ),
    )
    mass = _validated_symmetric(mass_assembly.matrix, "mass")
    diagonal = mass.diagonal()
    if np.any(diagonal <= 0.0):
        indices = np.flatnonzero(diagonal <= 0.0)
        preview = ", ".join(str(int(index + 1)) for index in indices[:10])
        raise MassMatrixError(
            "The mass matrix is not positive on every active DOF; zero/non-positive "
            f"diagonal DOFs include {preview}."
        )
    directions, mass_directions, total_masses = build_translational_pseudovectors(
        model, mass
    )
    progress(0.48)

    procedure = str(getattr(analysis, "modal_procedure", "SubspaceIterations"))
    criteria = str(getattr(analysis, "modal_convergence_criteria", "Frquency"))
    tolerance = _resolve_modal_tolerance(analysis, eigensolver_tolerance)
    max_iterations = max(1, int(getattr(analysis, "max_iterations", 1000)))
    log(
        f"Solving for {requested} eigenmodes with {procedure} "
        f"(C# convergence tolerance {tolerance:.3g})."
    )

    if procedure.casefold() == "inverseiterations":
        eigenvalues, eigenvectors = _inverse_iterations(
            stiffness,
            mass,
            requested,
            criteria=criteria,
            csharp_tolerance=tolerance,
            max_iterations=max_iterations,
            should_cancel=should_cancel,
            on_mode=lambda index: progress(0.48 + 0.48 * index / requested),
        )
    else:
        eigenvalues, eigenvectors = _subspace_modes(
            stiffness,
            mass,
            requested,
            csharp_tolerance=tolerance,
            max_iterations=max(1000, max_iterations),
            should_cancel=should_cancel,
            on_iteration=lambda iteration, error: log(
                f"Subspace iteration {iteration}: normalized eigenvalue error={error:.6g}%"
            ),
        )
        progress(0.96)

    if eigenvalues.size == 0:
        raise ModalAnalysisError("No positive modal eigenvalues converged.")
    if eigenvalues.size < requested:
        log(
            f"Warning: requested {requested} modes but only {eigenvalues.size} converged."
        )

    modes: list[ModalMode] = []
    for index, (eigenvalue, vector) in enumerate(
        zip(eigenvalues, eigenvectors.T, strict=True), start=1
    ):
        raise_if_cancelled(should_cancel)
        mode = _compute_mode(
            index,
            float(eigenvalue),
            np.asarray(vector, dtype=float),
            stiffness,
            mass,
            directions,
            mass_directions,
            total_masses,
        )
        modes.append(mode)
        log(
            f"Mode {index}: Fn={mode.frequency:.8g} Hz, "
            f"T={mode.period:.8g} s, residual={mode.residual_norm:.3g}."
        )

    progress(1.0)
    return ModalAnalysisResult(
        analysis_key=int(getattr(analysis, "key", 0)),
        analysis_name=str(getattr(analysis, "name", "")),
        combination=int(combination),
        requested_modes=requested,
        procedure=procedure,
        convergence_criteria=criteria,
        requested_mass_matrix_type=mass_assembly.requested_type,
        effective_mass_matrix_type=mass_assembly.effective_type,
        dof_count=n,
        stiffness_nnz=int(stiffness.nnz),
        mass_nnz=int(mass.nnz),
        runtime_seconds=float(time.perf_counter() - started),
        modes=tuple(modes),
    )


def _validated_symmetric(matrix: sp.csc_matrix, name: str) -> sp.csc_matrix:
    difference = matrix - matrix.T
    denominator = max(float(sp.linalg.norm(matrix)), np.finfo(float).tiny)
    relative = float(sp.linalg.norm(difference)) / denominator
    if not np.isfinite(relative) or relative > 1.0e-8:
        raise ModalAnalysisError(
            f"The assembled {name} matrix is not sufficiently symmetric "
            f"(relative asymmetry {relative:.6g})."
        )
    # Remove harmless floating-point assembly asymmetry before a symmetric solver.
    result = ((matrix + matrix.T) * 0.5).tocsc()
    result.sum_duplicates()
    return result


def _resolve_modal_tolerance(analysis: Any, override: float | None) -> float:
    if override is not None:
        value = float(override)
        if value <= 0.0 or not np.isfinite(value):
            raise ValueError("eigensolver_tolerance must be positive and finite.")
        return value
    source = abs(float(getattr(analysis, "convergence_tolerance", 1.0e-4)))
    return source if source > 0.0 else 1.0e-4


def _subspace_modes(
    stiffness: sp.csc_matrix,
    mass: sp.csc_matrix,
    count: int,
    *,
    csharp_tolerance: float,
    max_iterations: int,
    should_cancel: CancelCheck | None = None,
    on_iteration: Callable[[int, float], None] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Port C# ``Matrix.SubSpaceIteration2``.

    The source uses ``min(n+8, 2n, N)`` trial vectors initialized by .NET
    ``Random(0)``. Each iteration applies ``K^-1 M``, solves a reduced
    generalized eigenproblem, and stops when the sum of changes in the first
    requested eigenvalues, normalized by the first iteration, is at most the
    HRX tolerance in percent.
    """
    n_total = stiffness.shape[0]
    subspace_size = min(count + 8, 2 * count, n_total)
    random = _DotNetRandom(0)
    values = np.fromiter(
        (random.next_double() * 2.0 - 1.0 for _ in range(n_total * subspace_size)),
        dtype=float,
        count=n_total * subspace_size,
    )
    vectors = values.reshape(n_total, subspace_size)
    try:
        factor = splu(stiffness)
    except Exception as exc:
        raise ModalAnalysisError("Unable to factor the tangent stiffness matrix.") from exc

    previous = np.zeros(subspace_size, dtype=float)
    first_error = 1.0
    reduced_values = previous
    for iteration in range(1, max_iterations + 1):
        raise_if_cancelled(should_cancel)
        mass_projection = np.asarray(mass @ vectors, dtype=float)
        projected = np.asarray(factor.solve(mass_projection), dtype=float)
        reduced_stiffness = projected.T @ (stiffness @ projected)
        reduced_mass = projected.T @ (mass @ projected)
        reduced_stiffness = (reduced_stiffness + reduced_stiffness.T) * 0.5
        reduced_mass = (reduced_mass + reduced_mass.T) * 0.5
        try:
            reduced_values, reduced_vectors = scipy.linalg.eigh(
                reduced_stiffness,
                reduced_mass,
                check_finite=False,
            )
        except Exception as exc:
            raise ModalAnalysisError(
                f"Reduced generalized eigenproblem failed at subspace iteration {iteration}."
            ) from exc
        vectors = projected @ reduced_vectors
        error_sum = float(
            np.abs(np.sort(previous)[:count] - np.sort(reduced_values)[:count]).sum()
        )
        if iteration == 1:
            first_error = error_sum
        normalized_error = 0.0 if first_error == 0.0 else error_sum / first_error * 100.0
        if on_iteration is not None:
            on_iteration(iteration, normalized_error)
        previous = reduced_values.copy()
        if normalized_error <= csharp_tolerance:
            return _sorted_positive_modes(reduced_values, vectors, limit=count)

    raise ModalAnalysisError(
        "C#-compatible subspace iteration exceeded the Python safety limit of "
        f"{max_iterations} iterations (HRX tolerance {csharp_tolerance})."
    )


def _inverse_iterations(
    stiffness: sp.csc_matrix,
    mass: sp.csc_matrix,
    count: int,
    *,
    criteria: str,
    csharp_tolerance: float,
    max_iterations: int,
    should_cancel: CancelCheck | None,
    on_mode: Callable[[int], None],
) -> tuple[np.ndarray, np.ndarray]:
    """Sequential inverse iteration following C# ``ModalAnalysis.InverseIteration``."""
    try:
        factor = splu(stiffness)
    except Exception as exc:
        raise ModalAnalysisError("Unable to factor the tangent stiffness matrix.") from exc

    n = stiffness.shape[0]
    euclidean_modes: list[np.ndarray] = []
    values: list[float] = []
    vectors: list[np.ndarray] = []
    use_frequency = criteria.casefold() != "eigenvector"

    for mode_index in range(count):
        raise_if_cancelled(should_cancel)
        x = np.ones(n, dtype=float)
        x = _euclidean_deflate(x, euclidean_modes)
        b = np.asarray(mass @ x, dtype=float)
        previous_value = 0.0
        previous_residual = 0.0
        residual_reference: float | None = None
        converged = False
        value = float("nan")

        for iteration in range(1, max_iterations + 1):
            raise_if_cancelled(should_cancel)
            x = factor.solve(b)
            x = _euclidean_deflate(x, euclidean_modes)
            numerator = float(np.dot(b, x))
            mx = np.asarray(mass @ x, dtype=float)
            denominator = float(np.dot(mx, x))
            if denominator <= 0.0 or not np.isfinite(denominator):
                break
            value = numerator / denominator
            mass_norm = sqrt(denominator)
            x /= mass_norm
            b = mx / mass_norm

            euclidean_norm = float(np.linalg.norm(x))
            if euclidean_norm == 0.0 or not np.isfinite(euclidean_norm):
                break
            candidate_euclidean = x / euclidean_norm

            residual = np.asarray(stiffness @ x - value * (mass @ x), dtype=float)
            residual_norm = float(np.linalg.norm(residual))
            if use_frequency:
                error = (
                    float("inf")
                    if previous_value == 0.0
                    else 10000.0 * abs(value - previous_value) / abs(value)
                )
                converged = error <= csharp_tolerance
            else:
                error = (
                    float("inf")
                    if residual_norm == 0.0 or previous_residual == 0.0
                    else abs(residual_norm - previous_residual) / residual_norm
                )
                if residual_reference is None:
                    residual_reference = residual_norm / 2.0
                converged = (
                    error <= csharp_tolerance
                    and residual_norm <= residual_reference
                )
            previous_value = value
            previous_residual = residual_norm
            if converged:
                euclidean_modes.append(candidate_euclidean.copy())
                values.append(float(value))
                vectors.append(x.copy())
                break

        if not converged:
            break
        on_mode(mode_index + 1)

    if not values:
        return np.empty(0, dtype=float), np.empty((n, 0), dtype=float)
    return _sorted_positive_modes(np.asarray(values), np.column_stack(vectors))


def _euclidean_deflate(vector: np.ndarray, modes: list[np.ndarray]) -> np.ndarray:
    result = np.asarray(vector, dtype=float).copy()
    for mode in modes:
        result -= float(np.dot(mode, result)) * mode
    return result


def _sorted_positive_modes(
    values: np.ndarray, vectors: np.ndarray, *, limit: int | None = None
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float).reshape(-1)
    vectors = np.asarray(vectors, dtype=float)
    if vectors.ndim == 1:
        vectors = vectors.reshape(-1, 1)
    finite_positive = np.isfinite(values) & (values > 0.0)
    values = values[finite_positive]
    vectors = vectors[:, finite_positive]
    order = np.argsort(values)
    if limit is not None:
        order = order[:limit]
    return values[order], vectors[:, order]


def _compute_mode(
    mode_number: int,
    eigenvalue: float,
    vector: np.ndarray,
    stiffness: sp.csc_matrix,
    mass: sp.csc_matrix,
    directions: np.ndarray,
    mass_directions: np.ndarray,
    total_masses: np.ndarray,
) -> ModalMode:
    mass_vector = np.asarray(mass @ vector, dtype=float)
    norm_squared = float(np.dot(vector, mass_vector))
    if norm_squared <= 0.0 or not np.isfinite(norm_squared):
        raise ModalAnalysisError(f"Mode {mode_number} has a zero/invalid modal mass norm.")
    shape = vector / sqrt(norm_squared)

    # Eigenvector sign is mathematically arbitrary. Fix it for deterministic
    # archives/tests while preserving all C# modal quantities except Gamma sign.
    largest = int(np.argmax(np.abs(shape)))
    if shape[largest] < 0.0:
        shape = -shape

    participations = np.asarray(shape @ mass_directions, dtype=float)
    effective = participations * participations
    percentages = effective / total_masses * 100.0
    maxima = np.max(np.abs(shape[:, None] * directions), axis=0)

    k_shape = np.asarray(stiffness @ shape, dtype=float)
    m_shape = np.asarray(mass @ shape, dtype=float)
    residual = k_shape - eigenvalue * m_shape
    residual_norm = float(
        np.linalg.norm(residual) / max(np.linalg.norm(k_shape), np.finfo(float).tiny)
    )
    angular = sqrt(eigenvalue)
    frequency = angular / (2.0 * pi)
    period = 2.0 * pi / angular

    return ModalMode(
        mode_number=mode_number,
        eigenvalue=eigenvalue,
        angular_frequency=angular,
        frequency=frequency,
        period=period,
        participation_x=float(participations[0]),
        participation_y=float(participations[1]),
        participation_z=float(participations[2]),
        effective_mass_x=float(effective[0]),
        effective_mass_y=float(effective[1]),
        effective_mass_z=float(effective[2]),
        total_mass_x=float(total_masses[0]),
        total_mass_y=float(total_masses[1]),
        total_mass_z=float(total_masses[2]),
        mass_percent_x=float(percentages[0]),
        mass_percent_y=float(percentages[1]),
        mass_percent_z=float(percentages[2]),
        max_displacement_x=float(maxima[0]),
        max_displacement_y=float(maxima[1]),
        max_displacement_z=float(maxima[2]),
        residual_norm=residual_norm,
        shape=np.asarray(shape, dtype=float),
    )
