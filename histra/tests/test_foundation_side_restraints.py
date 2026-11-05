"""Serialized Quad-face supports, using C# restraint afference conventions."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pytest

from histra import load_model
from histra.preprocessing import prepare_model
from histra.preprocessing.restraint_support import (
    scatter_restraint_resisting_force, update_restraint_domain,
)
from histra.solver.assembler import assemble_global_k
from histra.types.linear_system import LinearSystem
from histra.tests.test_elastic_restraint_support import _wall_tree

# Rectangular wall Quad 1 occupies x=0..100, y=-10..10, z=0..50.
# Explicit polygon ordering and frames make the input independent of the
# preprocessing routine whose output is being tested.
FACES = {
    1: ([(100,10,50),(100,10,0),(100,-10,0),(100,-10,50)], (-1,0,0)),
    3: ([(0,10,50),(0,10,0),(0,-10,0),(0,-10,50)], (-1,0,0)),
    4: ([(100,10,50),(100,10,0),(0,10,0),(0,10,50)], (0,1,0)),
    5: ([(0,-10,50),(0,-10,0),(100,-10,0),(100,-10,50)], (0,-1,0)),
}
INWARD = {1: (-1, 0, 0), 3: (1, 0, 0), 4: (0, -1, 0), 5: (0, 1, 0)}


def test_finalized_inclined_hrx_side_frames_match_regenerated_interfaces(tmp_path):
    from histra.elements.interface import Interface
    from histra.model.node import Node
    from histra.model.restraint import Restraint
    from histra.preprocessing.contact_geometry import _make_interface_geometry, _v

    fixture = Path(__file__).parent / "fixtures/csharp_finalized_inclined_side_restraints.json"
    records = json.loads(fixture.read_text())["records"]
    model = _face_hrx(tmp_path, 1, [-1] * 6)
    for record in records:
        restraint = Restraint.from_xml(ET.fromstring(record["restraint"]))
        for node_xml in record["nodes"]:
            node = Node.from_xml(ET.fromstring(node_xml))
            model.collections.nodes[node.key] = node
        interface = Interface(key=restraint.key)
        _make_interface_geometry(model, interface, [_v(p) for p in restraint.points],
                                 tuple(restraint.node_keys), None)
        for actual, native in zip((interface.reference_e1, interface.reference_e2, interface.reference_e3),
                                  (restraint.reference_e1, restraint.reference_e2, restraint.reference_e3)):
            assert abs(float(np.dot(actual, native))) == pytest.approx(1.0, abs=2e-5)
        assert restraint.k == [0, -1, 0, -1, 0, -1]


def test_serialized_nonunit_frame_is_preserved_then_rejected(tmp_path):
    model = _face_hrx(tmp_path, 1, [-1, 200, -1, -1, -1, -1])
    from histra.model.restraint import Restraint
    from histra.preprocessing.errors import ModelPreparationError
    parsed = Restraint.from_xml(ET.fromstring(
        '<Restraint K2="200"><ReferenceSystem E1="0;0;-1" '
        'E2="-2;0;0" E3="0;1;0"/></Restraint>'
    ))
    assert parsed.reference_e2 == (-2.0, 0.0, 0.0)
    model.collections.restraints[10].reference_e2 = parsed.reference_e2
    with pytest.raises(ModelPreparationError, match="orthonormal"):
        prepare_model(model, force=True)
    assert model.collections.restraints[10].reference_e2 == (-2.0, 0.0, 0.0)


def test_four_vertical_faces_can_coexist_with_distinct_stiffnesses(tmp_path):
    tree = _wall_tree()
    root = tree.getroot()
    for index, face in enumerate((1, 3, 4, 5)):
        side = _face_hrx(tmp_path, face, [-1, 100 * (index + 1), -1, -1, -1, -1])
        side_root = ET.parse(side.source_path).getroot()
        restraint = side_root.find("Restraint[@Key='10']")
        restraint.set("Key", str(10 + index))
        for offset in range(2):
            node = side_root.find(f"Node[@Key='{1001 + offset}']")
            node.set("Key", str(2000 + 2 * index + offset))
            restraint.set(f"NodeKey{offset + 1}", node.get("Key"))
            root.append(node)
        root.append(restraint)
    path = tmp_path / "four-sides.hrx"
    tree.write(path)
    model = load_model(path)
    prepare_model(model, force=True)
    side_restraints = [model.collections.restraints[key] for key in range(10, 14)]
    assert len({r.solver_gdls[1] for r in side_restraints}) == 4
    matrix = assemble_global_k(model)
    for restraint in side_restraints:
        interface = next(i for i in model.collections.interfaces.values()
                         if i.parent_type_element1 == "Restraint" and i.parent_element_key1 == restraint.key)
        dof = restraint.solver_gdls[1] - 1
        assert matrix[dof, dof] == pytest.approx(sum(s.k for s in interface.trasv_1) + restraint.k[1])


def _fmt(vector):
    return ";".join(str(float(value)) for value in vector)


def _face_hrx(tmp_path, face, stiffness, *, sign=1):
    tree = _wall_tree()
    root = tree.getroot()
    restraint = deepcopy(root.find("Restraint"))
    vertices, normal = FACES[face]
    p = np.asarray(vertices, dtype=float)
    endpoints = ((p[0] + p[3]) / 2, (p[1] + p[2]) / 2)
    e1 = np.array((0., 0., -1.))
    e2 = sign * np.asarray(normal, dtype=float)
    e3 = np.cross(e1, e2)
    for key, point in zip((1001, 1002), endpoints):
        root.append(ET.Element("Node", Key=str(key), Name=str(key), Point=_fmt(point)))
    restraint.attrib.update(Key="10", Name="10", NodeKey1="1001", NodeKey2="1002",
                            NodeCKey1="0", NodeCKey2="0", ComputationalElementEdge=str(face))
    for name, value in zip(("K1", "K2", "K3", "Kr1", "Kr2", "Kr3"), stiffness):
        restraint.set(name, str(value))
    for index, vertex in enumerate(vertices, 1):
        restraint.set(f"Point{index}", _fmt(vertex))
    restraint.find("ReferenceSystem").attrib.update(
        E1=_fmt(e1), E2=_fmt(e2), E3=_fmt(e3), Origin=_fmt(endpoints[0]))
    root.append(restraint)
    path = tmp_path / f"side-{face}-{sign}-{'-'.join(map(str, stiffness))}.hrx"
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return load_model(path)


@pytest.mark.parametrize("face", (1, 3, 4, 5))
@pytest.mark.parametrize("sign", (-1, 1))
def test_fixed_and_normal_elastic_contact_face_geometry_and_tangent(tmp_path, face, sign):
    fixed = _face_hrx(tmp_path, face, [-1]*6, sign=sign)
    elastic = _face_hrx(tmp_path, face, [-1, 200, -1, -1, -1, -1], sign=sign)
    prepare_model(fixed, force=True)
    prepare_model(elastic, force=True)
    intf = next(i for i in elastic.collections.interfaces.values()
                if i.parent_type_element1 == "Restraint" and i.parent_element_key1 == 10)
    fixed_intf = next(i for i in fixed.collections.interfaces.values()
                      if i.parent_type_element1 == "Restraint" and i.parent_element_key1 == 10)
    np.testing.assert_allclose(intf.reference_e2, INWARD[face], atol=1e-7)
    assert intf.face2 == face
    restraint = elastic.collections.restraints[10]
    dof = restraint.solver_gdls[1] - 1
    alignment = 1 if face == 1 else -1
    assert [(entry.gdl, entry.alfa) for entry in intf.aff[0]] == [(dof + 1, sign * alignment)]
    k_elastic = assemble_global_k(elastic).toarray()
    k_fixed = assemble_global_k(fixed).toarray()
    np.testing.assert_allclose(k_elastic[:-1, :-1], k_fixed, rtol=1e-12, atol=1e-9)
    assert sum(s.k for s in intf.trasv_1) == pytest.approx(sum(s.k for s in fixed_intf.trasv_1))
    contact = sum(s.k for s in intf.trasv_1)
    assert k_elastic[dof, dof] == pytest.approx(contact + 200)
    # Eliminating the support displacement yields the series reduction.
    condensed = k_elastic[:-1, :-1] - np.outer(k_elastic[:-1, dof], k_elastic[dof, :-1]) / (contact + 200)
    assert np.linalg.norm(condensed - k_fixed) > 0
    assert np.linalg.eigvalsh(k_fixed - condensed).min() >= -1e-7


@pytest.mark.parametrize("face", (1, 3, 4, 5))
def test_free_dofs_follow_csharp_mapping_and_have_no_support_stiffness(tmp_path, face):
    model = _face_hrx(tmp_path, face, [0, 200, 0, 0, 0, 0])
    prepare_model(model, force=True)
    restraint = model.collections.restraints[10]
    intf = next(i for i in model.collections.interfaces.values()
                if i.parent_type_element1 == "Restraint" and i.parent_element_key1 == 10)
    gdls = restraint.solver_gdls
    assert all(gdls)
    # Restraint.ComputeInterfaceAfference rows, including rotational lever arms.
    alignment = 1 if face == 1 else -1
    for row, direction, coefficient in ((6, 0, 1), (0, 1, alignment), (8, 2, alignment), (9, 2, alignment),
                                        (4, 3, 1), (8, 4, alignment * intf.length/2),
                                        (9, 4, -alignment * intf.length/2), (1, 5, alignment)):
        assert (gdls[direction], coefficient) in [(e.gdl, e.alfa) for e in intf.aff[row]]
    ls = LinearSystem(model.gdl)
    ls.x[np.asarray(gdls) - 1] = [1, 2, 3, 4, 5, 6]
    update_restraint_domain(model, ls)
    scatter_restraint_resisting_force(model, ls)
    np.testing.assert_array_equal(restraint.u, [1, 2, 3, 4, 5, 6])
    np.testing.assert_array_equal(ls.b[np.asarray(gdls) - 1], [0, -400, 0, 0, 0, 0])


def test_fully_free_side_exerts_no_condensed_stiffness(tmp_path):
    model = _face_hrx(tmp_path, 1, [0] * 6)
    reference = _face_hrx(tmp_path, 1, [0] * 6)
    del reference.collections.restraints[10]
    prepare_model(model, force=True)
    prepare_model(reference, force=True)
    matrix = assemble_global_k(model).toarray()
    base = assemble_global_k(reference).toarray()
    n = reference.gdl
    support = matrix[n:, n:]
    condensed = matrix[:n, :n] - matrix[:n, n:] @ np.linalg.solve(support, matrix[n:, :n])
    np.testing.assert_allclose(condensed, base, rtol=1e-10, atol=1e-7)


@pytest.mark.parametrize("face", (1, 3, 4, 5))
def test_normal_load_response_is_softer_than_fixed_support(tmp_path, face):
    fixed = _face_hrx(tmp_path, face, [-1] * 6)
    elastic = _face_hrx(tmp_path, face, [-1, 200, -1, -1, -1, -1])
    prepare_model(fixed, force=True)
    prepare_model(elastic, force=True)
    k_fixed = assemble_global_k(fixed).toarray()
    k_elastic = assemble_global_k(elastic).toarray()
    coupling = k_elastic[:-1, -1]
    load = coupling / np.linalg.norm(coupling)
    fixed_u = np.linalg.solve(k_fixed, load)
    elastic_u = np.linalg.solve(k_elastic, np.r_[load, 0.0])
    assert load @ elastic_u[:-1] > load @ fixed_u
    # The support DOF balances its contact force against K2 * U2.
    assert coupling @ elastic_u[:-1] + k_elastic[-1, -1] * elastic_u[-1] == pytest.approx(0, abs=1e-10)
