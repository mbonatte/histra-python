from __future__ import annotations

import time
import numpy as np
import pytest

from histra import load_model
from histra.solver.assembler import _assemble_global_k_legacy, _get_stiffness_assembly_plan
from histra.solver.model_manager import ModelManager
from histra.types.linear_system import LinearSystem


def test_batch_stiffness_matches_legacy_assembly_exact() -> None:
    model = load_model("my_model/Article_Models_Benchmark/Bridge_1.hrx")
    ModelManager.prepare_model(model, force=True)
    ModelManager.prepare_hysteretic_batch(model)

    ls = LinearSystem(model.gdl)

    for alfa in [0.0, 0.5, 1.0]:
        # Legacy authoritative assembly
        k_legacy = _assemble_global_k_legacy(model, alfa=alfa, recompute_elements=True)

        # Batch accelerated assembly
        ModelManager.compute_ktang(model, ls, alfa)
        k_batch = ls.k

        diff_mat = k_batch - k_legacy
        max_diff = np.max(np.abs(diff_mat.data)) if diff_mat.nnz > 0 else 0.0
        rel_diff = max_diff / np.max(np.abs(k_legacy.data))
        assert rel_diff < 1e-13, f"alfa={alfa} relative diff {rel_diff} exceeds 1e-13"


def test_batch_stiffness_preserves_non_uniform_plastic_tangents() -> None:
    model = load_model("my_model/Article_Models_Benchmark/Bridge_1.hrx")
    ModelManager.prepare_model(model, force=True)
    runtime = ModelManager.prepare_hysteretic_batch(model)
    assert runtime is not None

    # Mutate tangent stiffnesses of the first 50 springs in runtime.trial to simulate plasticity
    runtime.trial[:50, 9] = runtime.trial[:50, 9] * 0.12345
    # Also sync to objects so legacy assembly sees the same tangents
    runtime.sync_tangents_to_objects()

    ls = LinearSystem(model.gdl)

    k_legacy = _assemble_global_k_legacy(model, alfa=1.0, recompute_elements=True)
    ModelManager.compute_ktang(model, ls, 1.0)
    k_batch = ls.k

    diff_mat = k_batch - k_legacy
    max_diff = np.max(np.abs(diff_mat.data)) if diff_mat.nnz > 0 else 0.0
    rel_diff = max_diff / np.max(np.abs(k_legacy.data))
    assert rel_diff < 1e-13, f"Plastic tangent relative diff {rel_diff} exceeds 1e-13"


def test_batch_stiffness_across_multiple_article_models() -> None:
    for model_name in ["Bridge_2.hrx", "Bridge_3.1_Coarse.hrx"]:
        model = load_model(f"my_model/Article_Models_Benchmark/{model_name}")
        ModelManager.prepare_model(model, force=True)
        ModelManager.prepare_hysteretic_batch(model)
        ls = LinearSystem(model.gdl)

        for alfa in [0.0, 1.0]:
            k_legacy = _assemble_global_k_legacy(model, alfa=alfa, recompute_elements=True)
            ModelManager.compute_ktang(model, ls, alfa)
            k_batch = ls.k

            diff_mat = k_batch - k_legacy
            max_diff = np.max(np.abs(diff_mat.data)) if diff_mat.nnz > 0 else 0.0
            rel_diff = max_diff / np.max(np.abs(k_legacy.data))
            assert rel_diff < 1e-13, f"{model_name} alfa={alfa} rel_diff {rel_diff} exceeds 1e-13"


def test_batch_stiffness_performance_gain() -> None:
    model = load_model("my_model/Article_Models_Benchmark/Bridge_1.hrx")
    ModelManager.prepare_model(model, force=True)
    ModelManager.prepare_hysteretic_batch(model)
    ls = LinearSystem(model.gdl)

    # Warmup
    ModelManager.compute_ktang(model, ls, 1.0)

    # Measure batch compute_ktang
    t0 = time.perf_counter()
    reps = 50
    for _ in range(reps):
        ModelManager.compute_ktang(model, ls, 1.0)
    dt_batch = (time.perf_counter() - t0) / reps

    # Batch compute_ktang must be under 5 ms (typically ~1.7 ms, vs ~56 ms baseline)
    assert dt_batch < 0.005, f"Batch stiffness time {dt_batch*1000:.2f} ms exceeds 5 ms threshold"
