"""Stage-end interface tensors based on C# Interface.GetTensorMap.

Both out-of-plane spring choices are retained: C# selects one by position.
The shear entries follow the native display tensor, without halving them.
"""
import numpy as np


def add_strain_tensors(model, runtime, interfaces, arrays):
    offsets = arrays['springs/transverse_offsets']
    sliding_offsets = arrays['springs/sliding_offsets']
    order = arrays['_export/interface_record_order']
    count = int(offsets[-1])
    for field in ('strain', 'plastic_strain'):
        local = np.zeros((count, 2, 3, 3), np.float32)
        valid = np.zeros((count, 2), np.uint8)
        for i, interface in enumerate(interfaces):
            span = slice(int(offsets[i]), int(offsets[i + 1]))
            record = int(order[i])
            slots = [int(rows[record]) for rows in
                     (runtime._slid_index, runtime._oop0_index, runtime._oop1_index)]
            positions = {}
            cursor = int(sliding_offsets[i])
            for slot, row in enumerate(slots):
                if row >= 0:
                    positions[slot] = cursor
                    cursor += 1
            normal = arrays[f'springs/transverse_{field}'][span]
            normal_valid = arrays[f'springs/transverse_{field}_valid'][span].astype(bool)
            if field == 'strain' and _soil_first_parent(model, interface):
                normal = -np.abs(normal)
            for side in range(2):
                if 0 not in positions or side + 1 not in positions:
                    continue
                shear, out = positions[0], positions[side + 1]
                values = arrays[f'springs/sliding_{field}']
                mask = arrays[f'springs/sliding_{field}_valid']
                local[span, side, 1, 1] = normal
                local[span, side, 0, 1] = local[span, side, 1, 0] = values[shear]
                local[span, side, 1, 2] = local[span, side, 2, 1] = values[out]
                valid[span, side] = normal_valid & bool(mask[shear]) & bool(mask[out])
        _store_tensors(arrays, field, local, valid, offsets)


def _soil_first_parent(model, interface):
    if interface.parent_type_element1 != 'Restraint':
        return False
    restraint = model.collections.restraints.get(interface.parent_element_key1)
    return restraint is not None and (restraint.material_key in model.collections.materials
                                      or restraint.material_key in model.unsupported_material_templates)


def _store_tensors(arrays, field, local, valid, offsets):
    axes = np.stack([arrays[f'mesh/interface_e{i}'] for i in (1, 2, 3)], axis=2)
    axes = np.repeat(axes, np.diff(offsets).astype(int), axis=0)
    finite = np.isfinite(axes).all(axis=(1, 2))
    axes = np.where(np.isfinite(axes), axes, 0)
    basis_valid = finite & np.all(np.isclose(np.swapaxes(axes, 1, 2) @ axes, np.eye(3), atol=1e-5), axis=(1, 2))
    valid &= basis_valid[:, None]
    global_tensor = np.einsum('nij,nsjk,nlk->nsil', axes, local, axes)
    principal = np.linalg.eigvalsh(global_tensor).astype(np.float32)
    prefix = f'fields/interface_{field}'
    arrays[f'{prefix}_local'] = local
    arrays[f'{prefix}_global'] = global_tensor.astype(np.float32)
    arrays[f'{prefix}_principal'] = principal
    arrays[f'{prefix}_valid'] = valid
