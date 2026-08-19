from __future__ import annotations

import numpy as np
import pytest

from histra.solver import hysteretic_batch as hb

pytestmark = pytest.mark.skipif(
    hb._evaluate_simple_linear_batch is None,
    reason="Numba is unavailable",
)


def _simple_params(count: int) -> np.ndarray:
    params = np.zeros((count, hb.SIMPLE_TRANSVERSE_PARAM_SIZE), dtype=np.float64)
    params[:, 0] = 1.0e-3
    params[:, 1] = 1.0
    params[:, 2] = 2.0e-3
    params[:, 3] = 0.8
    params[:, 4] = 3.0e-3
    params[:, 6] = -1.0
    params[:, 7] = -1.0e-3
    params[:, 8] = -2.0e-3
    params[:, 9] = -0.8
    params[:, 10] = -3.0e-3
    params[:, 12] = 1000.0
    params[:, 13] = 1000.0
    params[:, 14] = -200.0
    params[:, 15] = -200.0
    params[:, 16] = -100.0
    params[:, 17] = -100.0
    params[:, 18] = 1000.0
    params[:, 19] = 1000.0
    return params


def test_parallel_simple_hysteretic_matches_scalar_loop_exactly() -> None:
    count = 257
    rng = np.random.default_rng(734)
    params = _simple_params(count)
    committed = np.zeros((count, 9), dtype=np.float64)
    committed[:, 0] = 2.0e-4
    committed[:, 1] = -2.0e-4
    committed[:, 6] = rng.normal(0.0, 0.1, count)
    committed[:, 7] = rng.normal(0.0, 1.0e-4, count)
    trial_reference = np.zeros((count, 10), dtype=np.float64)
    trial_reference[:, 9] = 1000.0
    trial_parallel = trial_reference.copy()
    targets = rng.normal(0.0, 3.0e-4, count)
    enabled = np.ones(count, dtype=np.bool_)

    hb._evaluate_simple_linear_batch.py_func(
        params.copy(), committed.copy(), trial_reference, targets.copy(), enabled.copy()
    )
    hb._evaluate_simple_linear_batch(
        params.copy(), committed.copy(), trial_parallel, targets.copy(), enabled.copy()
    )

    np.testing.assert_array_equal(trial_parallel, trial_reference)


def test_parallel_interface_reduction_preserves_spring_order_exactly() -> None:
    records = 7
    springs_per_record = 19
    count = records * springs_per_record
    rng = np.random.default_rng(991)
    trial = np.zeros((count, 10), dtype=np.float64)
    committed = np.zeros((count, 9), dtype=np.float64)
    trial[:, 6] = rng.normal(size=count)
    trial[:, 7] = rng.normal(scale=1.0e-4, size=count)
    committed[:, 6] = rng.normal(size=count)
    di = np.tile(np.linspace(0.03, 0.97, springs_per_record), records)
    dj = 1.0 - di
    ecc = np.tile(np.linspace(-0.3, 0.3, springs_per_record), records)
    lengths = np.linspace(0.7, 1.3, records)
    starts = np.arange(records, dtype=np.int32) * springs_per_record
    stops = starts + springs_per_record
    constrained = np.asarray([False, True, False, True, False, True, False])

    reference = [
        np.zeros((records, 6), dtype=np.float64),
        np.zeros(records, dtype=np.float64),
        np.zeros(records, dtype=np.float64),
        np.zeros(records, dtype=np.float64),
    ]
    parallel = [array.copy() for array in reference]

    hb._finish_transverse_batch.py_func(
        trial, committed, di, dj, ecc, lengths, starts, stops, constrained, *reference
    )
    hb._finish_transverse_batch(
        trial, committed, di, dj, ecc, lengths, starts, stops, constrained, *parallel
    )

    for actual, expected in zip(parallel, reference):
        np.testing.assert_array_equal(actual, expected)


def test_parallel_general_hysteretic_matches_scalar_loop_exactly() -> None:
    count = 257
    rng = np.random.default_rng(735)
    params = np.zeros((count, hb.TRANSVERSE_PARAM_SIZE), dtype=np.float64)
    compact = _simple_params(count)
    params[:, 8] = 1.0
    params[:, 10:30] = compact[:, :20]
    params[:, 31] = 1000.0
    params[:, hb.TENSILE_CURVE_TYPE_PARAM] = compact[:, hb.SIMPLE_TENSILE_CURVE_TYPE_PARAM]
    committed = np.zeros((count, 9), dtype=np.float64)
    committed[:, 0] = 2.0e-4
    committed[:, 1] = -2.0e-4
    committed[:, 6] = rng.normal(0.0, 0.1, count)
    committed[:, 7] = rng.normal(0.0, 1.0e-4, count)
    reference = np.zeros((count, 10), dtype=np.float64)
    reference[:, 9] = 1000.0
    parallel = reference.copy()
    targets = rng.normal(0.0, 3.0e-4, count)
    enabled = np.ones(count, dtype=np.bool_)

    hb._evaluate_linear_batch.py_func(
        params.copy(), committed.copy(), reference, targets.copy(), enabled.copy()
    )
    hb._evaluate_linear_batch(
        params.copy(), committed.copy(), parallel, targets.copy(), enabled.copy()
    )
    np.testing.assert_array_equal(parallel, reference)


def test_parallel_target_update_is_exact() -> None:
    records = 11
    springs_per_record = 13
    count = records * springs_per_record
    rng = np.random.default_rng(736)
    trial = rng.normal(size=(count, 10))
    record_index = np.repeat(np.arange(records, dtype=np.int32), springs_per_record)
    num = rng.normal(size=records)
    num2 = rng.normal(size=records)
    di = rng.random(count)
    dj = 1.0 - di
    lengths = rng.random(records) + 0.5
    delta_flex = rng.normal(size=records)
    ecc = rng.normal(size=count)
    reference = np.empty(count, dtype=np.float64)
    parallel = np.empty(count, dtype=np.float64)

    hb._advance_transverse_targets.py_func(
        trial, record_index, num, num2, di, dj, lengths, delta_flex, ecc, reference
    )
    hb._advance_transverse_targets(
        trial, record_index, num, num2, di, dj, lengths, delta_flex, ecc, parallel
    )
    np.testing.assert_array_equal(parallel, reference)


def test_fused_target_and_simple_hysteretic_matches_separate_kernels_exactly() -> None:
    records = 17
    springs_per_record = 23
    count = records * springs_per_record
    rng = np.random.default_rng(737)

    params = _simple_params(count)
    committed = np.zeros((count, 9), dtype=np.float64)
    committed[:, 0] = 2.5e-4
    committed[:, 1] = -2.5e-4
    committed[:, 4] = rng.normal(0.0, 1.0e-5, count)
    committed[:, 5] = rng.integers(0, 3, size=count)
    committed[:, 6] = rng.normal(0.0, 0.1, count)
    committed[:, 7] = rng.normal(0.0, 1.0e-4, count)
    committed[:, 8] = hb.ELASTIC

    trial_reference = np.zeros((count, 10), dtype=np.float64)
    trial_reference[:, 5] = committed[:, 5]
    trial_reference[:, 6] = committed[:, 6]
    trial_reference[:, 7] = committed[:, 7]
    trial_reference[:, 8] = committed[:, 8]
    trial_reference[:, 9] = 1000.0
    trial_fused = trial_reference.copy()

    record_index = np.repeat(np.arange(records, dtype=np.int32), springs_per_record)
    num = rng.normal(0.0, 2.0e-4, records)
    num2 = rng.normal(0.0, 2.0e-4, records)
    di = rng.random(count)
    dj = 1.0 - di
    lengths = rng.random(records) + 0.5
    delta_flex = rng.normal(0.0, 2.0e-4, records)
    ecc = rng.normal(0.0, 0.2, count)
    enabled = np.ones(count, dtype=np.bool_)
    enabled[::31] = False

    targets_reference = np.empty(count, dtype=np.float64)
    targets_fused = np.empty(count, dtype=np.float64)

    hb._advance_transverse_targets(
        trial_reference,
        record_index,
        num,
        num2,
        di,
        dj,
        lengths,
        delta_flex,
        ecc,
        targets_reference,
    )
    hb._evaluate_simple_linear_batch(
        params,
        committed,
        trial_reference,
        targets_reference,
        enabled,
    )

    hb._advance_and_evaluate_simple_linear_batch(
        params,
        committed,
        trial_fused,
        targets_fused,
        enabled,
        record_index,
        num,
        num2,
        di,
        dj,
        lengths,
        delta_flex,
        ecc,
    )

    np.testing.assert_array_equal(targets_fused, targets_reference)
    np.testing.assert_array_equal(trial_fused, trial_reference)


def _finish_transverse_reference(
    trial: np.ndarray,
    committed: np.ndarray,
    di: np.ndarray,
    dj: np.ndarray,
    ecc: np.ndarray,
    lengths: np.ndarray,
    starts: np.ndarray,
    stops: np.ndarray,
    constrained: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pre-optimization force reduction, kept as a bit-exact oracle."""
    local_forces = np.zeros((starts.size, 6), dtype=np.float64)
    normal_increments = np.zeros(starts.size, dtype=np.float64)
    committed_forces = np.zeros(starts.size, dtype=np.float64)
    max_displacements = np.zeros(starts.size, dtype=np.float64)

    for record_index in range(starts.size):
        start = int(starts[record_index])
        stop = int(stops[record_index])
        normal_increment = 0.0
        committed_force = 0.0
        max_displacement = 0.0
        for spring_index in range(start, stop):
            force = trial[spring_index, 6]
            committed_value = committed[spring_index, 6]
            normal_increment -= force - committed_value
            committed_force += committed_value
            displacement = abs(trial[spring_index, 7])
            if displacement > max_displacement:
                max_displacement = displacement

            length = lengths[record_index]
            if not constrained[record_index]:
                local_forces[record_index, 3] += force * dj[spring_index] / length
                local_forces[record_index, 2] += force * di[spring_index] / length
                local_forces[record_index, 0] += (0.0 - force) * dj[spring_index] / length
                local_forces[record_index, 1] += (0.0 - force) * di[spring_index] / length
            else:
                local_forces[record_index, 3] += force * dj[spring_index] / length
                local_forces[record_index, 2] += force * di[spring_index] / length
                local_forces[record_index, 0] += (
                    (0.0 - force) * di[spring_index] / length
                    - force * dj[spring_index] / length
                )
                local_forces[record_index, 1] += 0.5 * length * (
                    force * dj[spring_index] / length
                    - force * di[spring_index] / length
                )
            local_forces[record_index, 4] += force * ecc[spring_index]
            local_forces[record_index, 5] += (0.0 - force) * ecc[spring_index]

        normal_increments[record_index] = normal_increment
        committed_forces[record_index] = committed_force
        max_displacements[record_index] = max_displacement

    return local_forces, normal_increments, committed_forces, max_displacements


def test_interface_reduction_hoisted_invariants_match_previous_loop_exactly() -> None:
    records = 13
    springs_per_record = 27
    count = records * springs_per_record
    rng = np.random.default_rng(738)
    trial = np.zeros((count, 10), dtype=np.float64)
    committed = np.zeros((count, 9), dtype=np.float64)
    trial[:, 6] = rng.normal(size=count)
    trial[:, 7] = rng.normal(scale=1.0e-4, size=count)
    committed[:, 6] = rng.normal(size=count)
    di = rng.random(count)
    dj = 1.0 - di
    ecc = rng.normal(scale=0.3, size=count)
    lengths = rng.random(records) + 0.5
    starts = np.arange(records, dtype=np.int32) * springs_per_record
    stops = starts + springs_per_record
    constrained = (np.arange(records) % 2 == 0)

    expected = _finish_transverse_reference(
        trial, committed, di, dj, ecc, lengths, starts, stops, constrained
    )
    actual = (
        np.zeros((records, 6), dtype=np.float64),
        np.zeros(records, dtype=np.float64),
        np.zeros(records, dtype=np.float64),
        np.zeros(records, dtype=np.float64),
    )

    hb._finish_transverse_batch(
        trial,
        committed,
        di,
        dj,
        ecc,
        lengths,
        starts,
        stops,
        constrained,
        *actual,
    )

    for actual_array, expected_array in zip(actual, expected):
        np.testing.assert_array_equal(actual_array, expected_array)
