from types import SimpleNamespace

import numpy as np

from histra.io.strain_tensor import add_strain_tensors


def test_native_components_rotation_principal_and_masks():
    interface = SimpleNamespace(parent_type_element1='Quad')
    runtime = SimpleNamespace(_slid_index=[0], _oop0_index=[1], _oop1_index=[2])
    arrays = {'springs/transverse_offsets': np.array([0, 2]),
              'springs/sliding_offsets': np.array([0, 3]),
              '_export/interface_record_order': np.array([0]),
              'mesh/interface_e1': np.array([[0., 1., 0.]]),
              'mesh/interface_e2': np.array([[-1., 0., 0.]]),
              'mesh/interface_e3': np.array([[0., 0., 1.]])}
    for field in ('strain', 'plastic_strain'):
        arrays[f'springs/transverse_{field}'] = np.array([2., 3.])
        arrays[f'springs/transverse_{field}_valid'] = np.array([1, 0])
        arrays[f'springs/sliding_{field}'] = np.array([4., 5., 6.])
        arrays[f'springs/sliding_{field}_valid'] = np.array([1, 1, 0])
    add_strain_tensors(None, runtime, [interface], arrays)
    local = np.array([[0, 4, 0], [4, 2, 5], [0, 5, 0]])
    basis = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    np.testing.assert_array_equal(arrays['fields/interface_strain_local'][0, 0], local)
    expected = basis @ local @ basis.T
    np.testing.assert_array_equal(arrays['fields/interface_strain_global'][0, 0], expected)
    np.testing.assert_allclose(arrays['fields/interface_strain_principal'][0, 0], np.linalg.eigvalsh(expected), rtol=1e-6, atol=1e-6)
    np.testing.assert_array_equal(arrays['fields/interface_strain_valid'], [[1, 0], [0, 0]])
