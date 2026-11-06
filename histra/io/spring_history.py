"""Capture committed spring responses at C# analysis save intervals."""
from __future__ import annotations

import numpy as np

from histra.io.results_snapshot import _spring_indices
from histra.io.spring_snapshot import add_spring_responses
from histra.solver.model_manager import ModelManager
from histra.solver.hysteretic_kernels import interface_coulomb as ic, quad_takeda as qt


class SpringHistoryCapture:
    """Keep saved steps separate from stage-end data and unsaved iterations."""

    def __init__(self, model):
        self.model = model
        self.steps = []
        self.records = []

    def capture(self, step, analysis):
        number = int(step['step'])
        if number % max(1, int(getattr(analysis, 'step_save', 1))):
            return
        runtime = ModelManager.hysteretic_batch_for(self.model)
        if runtime is None or not runtime.active:
            raise ValueError('Cannot capture saved spring states without the compiled runtime')
        interfaces = [i for _, i in sorted(self.model.collections.interfaces.items())]
        arrays = {'mesh/quad_keys': np.asarray(sorted(self.model.collections.quads), np.uint32)}
        transverse, sliding, _ = _spring_indices(runtime, interfaces, arrays)
        add_spring_responses(runtime, interfaces, transverse, sliding, arrays)
        self._add_native_state(runtime, interfaces, transverse, sliding, arrays)
        fields = ('displacement', 'plastic_displacement', 'plastic_displacement_valid',
                  'force', 'phase', 'yield_force', 'initial_stiffness', 'length', 'spring_type',
                  'strain', 'strain_valid', 'plastic_strain', 'plastic_strain_valid',
                  'native_strain_raw', 'native_plastic_strain_raw',
                  'derived_strain', 'derived_strain_valid',
                  'derived_plastic_strain', 'derived_plastic_strain_valid')
        self.records.append({f'{kind}_{name}': arrays[f'springs/{kind}_{name}']
                             for kind in ('transverse', 'sliding', 'quad')
                             for name in fields if f'springs/{kind}_{name}' in arrays})
        self.steps.append(number)

    @staticmethod
    def _add_native_state(runtime, interfaces, transverse, sliding, arrays):
        from histra.io.spring_snapshot import _transverse_definitions

        state = runtime.committed[transverse]
        arrays['springs/transverse_force'] = state[:, 6].copy()
        arrays['springs/transverse_phase'] = state[:, 8].astype(np.int8)
        arrays['springs/transverse_yield_force'] = _transverse_definitions(interfaces)[:, 3:5]
        state = runtime.coulomb_state[sliding]
        arrays['springs/sliding_force'] = state[:, ic.CCSTRESS].copy()
        arrays['springs/sliding_phase'] = state[:, ic.CCPHASE].astype(np.int8)
        arrays['springs/sliding_yield_force'] = state[:, [ic.CFY0, ic.CFY1]].copy()
        by_key = {quad.key: index for index, quad in enumerate(runtime.quad_records)}
        order = [by_key[int(key)] for key in arrays['mesh/quad_keys']]
        state = runtime.quad_state[order]
        arrays['springs/quad_force'] = state[:, qt.QCSTRESS].copy()
        arrays['springs/quad_yield_force'] = state[:, [qt.QFY0, qt.QFY1]].copy()

    def arrays(self):
        if not self.records:
            return {}
        return {'springs/history_step': np.asarray(self.steps, np.int32),
                **{f'springs/history_{key}': np.stack([record[key] for record in self.records])
                   for key in self.records[0]}}
