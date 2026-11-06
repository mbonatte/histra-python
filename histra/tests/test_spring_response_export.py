"""Native getter differentials and committed spring output integration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import pytest

from histra import AnalysisSession, SimulationResults, load_model
from histra.io.results_snapshot import capture_export_snapshot
from histra.io.spring_response import project_spring_response
from histra.solver.model_manager import ModelManager
from histra.springs.transverse_fiber_group import TransverseFiberGroup

ROOT = Path(__file__).parents[2]
FIXTURE = json.loads((Path(__file__).parent / 'fixtures/csharp_spring_response_2026_1_1.json').read_text())


@pytest.mark.parametrize('case', FIXTURE['cases'], ids=lambda case: case['name'])
def test_response_getters_match_executed_original_csharp(case):
    fields = project_spring_response([case['u']], [case['f']], [case['k']], [case['fy']],
                                     [case['ur']], [case['length']], [case['kind']], [case['phase']], [case['k']])
    for name in ('strain', 'plastic_displacement', 'plastic_strain', 'plastic_ratio'):
        bits = case['expected_bits'][name]
        code = 'd' if name == 'plastic_displacement' else 'f'
        expected_bytes = bytes.fromhex(bits)
        expected = struct.unpack('>' + code, expected_bytes)[0]
        value = fields[name][0]
        if np.isfinite(expected):
            assert fields[f'{name}_valid'][0] == 1
            assert struct.pack('>' + code, value) == expected_bytes, (name, value, expected)
        else:
            assert fields[f'{name}_valid'][0] == 0
            assert value == 0.0
        if name in ('strain', 'plastic_strain'):
            raw = fields[f'native_{name}_raw'][0]
            if np.isnan(expected):
                assert np.isnan(raw)
            else:
                assert raw == expected
    if 'unlimited_tension' in case['name'] or 'unlimited_compression' in case['name']:
        assert fields['plastic_ratio_is_normalized'][0] == 0
    elif fields['plastic_ratio_valid'][0]:
        assert fields['plastic_ratio_is_normalized'][0] == 1
    phase = case['phase']
    assert fields['is_plastic'][0] == (phase in (1, 2))
    assert fields['is_ruptured'][0] == (phase in (7, 8, 9))
    assert fields['is_slipping'][0] == (phase == 10)


def test_getter_fixture_bound_to_original_source_if_available():
    for relative, digest in FIXTURE['source_sha256'].items():
        source = ROOT / 'C#_Original/source' / relative
        if source.exists():
            assert hashlib.sha256(source.read_bytes()).hexdigest() == digest


@pytest.fixture(scope='module')
def solved():
    session = AnalysisSession(load_model(ROOT / 'histra/model-output/model.hrx'))
    execution = session.run('Vert')
    return session, execution


@pytest.mark.parametrize('format', ['npz', 'histra', 'h5'])
def test_roundtrip_spring_response_arrays_and_accessors(solved, tmp_path, format):
    if format == 'h5':
        pytest.importorskip('h5py')
    session, execution = solved
    files = session.export_analysis('Vert', tmp_path, format=format)
    with SimulationResults.load(files.get('bundle') or files['fields']) as result:
        assert result.summary['metadata']['schema_version'] == '2.2.0'
        assert result.summary['metadata']['spring_response']['scope'] == 'committed_stage_end'
        assert json.loads(result['metadata/spring_response'].item())['units']['strain'] == '1'
        for kind in ('transverse', 'sliding', 'quad'):
            for name in ('displacement', 'strain', 'plastic_displacement', 'plastic_strain',
                         'plastic_ratio', 'length', 'is_plastic', 'is_ruptured', 'is_slipping'):
                key = f'springs/{kind}_{name}'
                expected = execution.export_snapshot[key]
                actual = result[key]
                assert actual.dtype == expected.dtype
                assert actual.tobytes() == expected.tobytes()
            assert result[f'springs/{kind}_strain'].dtype == np.float32
            assert result[f'springs/{kind}_plastic_displacement'].dtype == np.float64
        for interface_key in result.mesh_interface_keys[:3]:
            history = result.get_interface_spring_history(int(interface_key))
            np.testing.assert_array_equal(history['step'], execution.spring_history['springs/history_step'])
            np.testing.assert_array_equal(history['plastic_strain'][-1],
                                          result.get_interface_springs(int(interface_key))['plastic_strain'])
            tensors = result.get_interface_strain_tensors(int(interface_key))
            assert tensors['local'].shape[1:] == (2, 3, 3)
            start, end = result['springs/transverse_offsets'][:2] if interface_key == result.mesh_interface_keys[0] else (0, 0)
            if end:
                np.testing.assert_array_equal(tensors['local'], execution.export_snapshot['fields/interface_strain_local'][start:end])
            for kind in ('transverse', 'sliding'):
                springs = result.get_interface_springs(int(interface_key), kind)
                assert {'strain', 'plastic_strain', 'plastic_ratio', 'is_ruptured'} <= set(springs)
                assert all(value.shape == springs['force'].shape for value in springs.values())
        quads = result.get_quad_springs()
        assert quads['strain'].shape == result.mesh_quad_keys.shape
        for index, key in enumerate(result.mesh_quad_keys[:3]):
            np.testing.assert_array_equal(result.get_quad_springs(int(key))['displacement'], quads['displacement'][index:index+1])
        with pytest.raises(KeyError):
            result.get_quad_springs(-99)


def test_new_snapshot_fields_do_not_materialize_fibres_or_mutate_runtime(solved, monkeypatch):
    session, execution = solved
    runtime = ModelManager.hysteretic_batch_for(session.model)
    before = (runtime.committed.tobytes(), runtime.trial.tobytes(),
              runtime.coulomb_state.tobytes(), runtime.quad_state.tobytes())
    groups = [i.trasv_1 for i in session.model.collections.interfaces.values()
              if getattr(i.trasv_1, 'is_batch_backed', False)]
    caches = [dict(group._cache) for group in groups]
    def reject_proxy(*args):
        pytest.fail('spring output materialized a fibre proxy')
    monkeypatch.setattr(TransverseFiberGroup, '_materialize_proxy', reject_proxy)
    snapshot = capture_export_snapshot(session.model)
    assert before == (runtime.committed.tobytes(), runtime.trial.tobytes(),
                      runtime.coulomb_state.tobytes(), runtime.quad_state.tobytes())
    assert caches == [group._cache for group in groups]
    for key, array in execution.export_snapshot.items():
        assert array.tobytes() == snapshot[key].tobytes()


def test_geometric_length_and_signed_plastic_demand_are_preserved(solved):
    session, execution = solved
    snapshot = execution.export_snapshot
    lengths = snapshot['springs/transverse_length']
    undefined = lengths == 0
    assert undefined.any()  # Native SetQuadTrasvSpring leaves these zero.
    reference = snapshot['springs/transverse_strain_reference_length']
    geometric = snapshot['springs/transverse_strain_reference_is_geometric'].astype(bool)
    assert geometric[undefined].all()
    assert (reference[undefined] > 0).all()
    assert not snapshot['springs/transverse_strain_valid'][undefined].any()
    assert not snapshot['springs/transverse_plastic_strain_valid'][undefined].any()
    assert snapshot['springs/transverse_derived_strain_valid'][undefined].all()
    assert snapshot['springs/transverse_derived_plastic_strain_valid'][undefined].all()
    np.testing.assert_allclose(snapshot['springs/transverse_derived_strain'][undefined],
                               (snapshot['springs/transverse_displacement'][undefined] / reference[undefined]).astype(np.float32))
    np.testing.assert_allclose(snapshot['springs/transverse_derived_plastic_strain'][undefined],
                               (snapshot['springs/transverse_plastic_displacement'][undefined] / reference[undefined]).astype(np.float32))
    assert np.isfinite(snapshot['springs/transverse_strain']).all()
    assert np.isfinite(snapshot['springs/transverse_plastic_strain']).all()
    # Native Coulomb demand can be signed and must not be clamped to [0,1].
    case = next(case for case in FIXTURE['cases'] if case['name'] == 'coulomb_opposite_sign_up')
    fields = project_spring_response([case['u']], [case['f']], [case['k']], [case['fy']],
                                     [case['ur']], [case['length']], [12], [1], [10.0])
    assert fields['plastic_displacement'][0] < 0
    assert fields['plastic_ratio'][0] < 0


def test_reference_lengths_follow_preprocessing_fibre_geometry(solved):
    from histra.preprocessing.spring_assignment import _interface_cells, _transverse_side_properties_batch

    session, execution = solved
    model = session.model
    interfaces = [i for _, i in sorted(model.collections.interfaces.items())]
    offsets = execution.export_snapshot['springs/transverse_offsets']
    for index in (0, len(interfaces) - 1):
        interface = interfaces[index]
        cells = _interface_cells(interface)
        material = model.collections.materials.get(interface.material_key)
        sides = [_transverse_side_properties_batch(model, kind, key, face, interface, cells, material)[0]
                 for kind, key, face in ((interface.parent_type_element1, interface.parent_element_key1, interface.face1),
                                         (interface.parent_type_element2, interface.parent_element_key2, interface.face2))]
        expected = sides[0][:, 2] + sides[1][:, 2]
        actual = execution.export_snapshot['springs/transverse_strain_reference_length'][offsets[index]:offsets[index + 1]]
        np.testing.assert_array_equal(actual, expected)


def test_missing_geometric_reference_stays_invalid(solved, monkeypatch):
    session, _ = solved
    interface = next(i for i in session.model.collections.interfaces.values() if len(i.trasv_1))
    monkeypatch.delattr(interface, '_transverse_reference_length')
    snapshot = capture_export_snapshot(session.model)
    index = int(np.flatnonzero(snapshot['mesh/interface_keys'] == interface.key)[0])
    offsets = snapshot['springs/transverse_offsets']
    span = slice(offsets[index], offsets[index + 1])
    assert not snapshot['springs/transverse_strain_valid'][span].any()
    assert not snapshot['springs/transverse_plastic_strain_valid'][span].any()
    assert not snapshot['springs/transverse_derived_plastic_strain_valid'][span].any()


def test_snapshot_isolation_after_later_runtime_changes(solved, monkeypatch, tmp_path):
    session, execution = solved
    expected = execution.export_snapshot['springs/transverse_strain'].tobytes()
    expected_up = execution.export_snapshot['springs/sliding_plastic_displacement'].tobytes()
    runtime = ModelManager.hysteretic_batch_for(session.model)
    committed = runtime.committed.copy()
    committed[:, 7] += 9.0
    coulomb = runtime.coulomb_state.copy()
    coulomb[:, 4] += 7.0
    monkeypatch.setattr(runtime, 'committed', committed)
    monkeypatch.setattr(runtime, 'coulomb_state', coulomb)
    files = session.export_analysis('Vert', tmp_path, format='histra')
    with SimulationResults.load(files['bundle']) as result:
        assert result['springs/transverse_strain'].tobytes() == expected
        assert result['springs/sliding_plastic_displacement'].tobytes() == expected_up


def test_saved_step_history_respects_csharp_step_save_and_commits(tmp_path):
    session = AnalysisSession(load_model(ROOT / 'histra/model-output/model.hrx'), strategy_policy='off')
    session.resolve_analysis('Vert').step_save = 2
    expected = {}

    def committed(row, analysis):
        if row['step'] % analysis.step_save == 0:
            snapshot = capture_export_snapshot(session.model)
            expected[row['step']] = snapshot['springs/transverse_plastic_displacement'].copy()

    execution = session.run('Vert', max_committed_steps=3, on_step_committed=committed)
    history = execution.spring_history
    np.testing.assert_array_equal(history['springs/history_step'], [0, 2])
    np.testing.assert_array_equal(history['springs/history_transverse_plastic_displacement'][1], expected[2])
    assert not np.array_equal(history['springs/history_transverse_displacement'][1],
                              execution.export_snapshot['springs/transverse_displacement'])
    bundle = session.export_bundle(tmp_path / 'history.histra')
    with SimulationResults.load(bundle) as result:
        key = int(result.mesh_interface_keys[0])
        observed = result.get_interface_spring_history(key)
        offsets = result['springs/transverse_offsets']
        np.testing.assert_array_equal(observed['step'], [0, 2])
        np.testing.assert_array_equal(observed['plastic_displacement'],
                                      history['springs/history_transverse_plastic_displacement'][:, offsets[0]:offsets[1]])
        assert observed['yield_force'].shape == (*observed['force'].shape, 2)
        np.testing.assert_array_equal(observed['native_plastic_strain_raw'],
                                      history['springs/history_transverse_native_plastic_strain_raw'][:, offsets[0]:offsets[1]])
