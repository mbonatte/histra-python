"""Strict C# parity tests for load-combination and load-assembly boundaries."""
from __future__ import annotations

import pytest

from histra.model.load import (
    Analysis,
    LoadCombination,
    LoadCombinationItem,
    LoadCondition,
    LoadTemplateItem,
)
from histra.model.model import Collections, Model
from histra.solver import assembler
from histra.solver import load_assembly


@pytest.fixture
def condition() -> LoadCondition:
    return LoadCondition(
        id=7,
        gamma_fav_str=0.9,
        gamma_unfav_str=1.35,
        gamma_fav_geo=0.8,
        gamma_unfav_geo=1.25,
    )


@pytest.fixture
def template_item() -> LoadTemplateItem:
    return LoadTemplateItem(psi0=0.6, psi1=0.4, psi2=0.2)


@pytest.mark.parametrize(
    ("type_data", "expected"),
    [
        ("Number", 0.75),
        ("Psi0", 0.6),
        ("Psi1", 0.4),
        ("Psi2", 0.2),
        ("GammaFavSTR", 0.9),
        ("GammaUnfavSTR", 1.35),
        ("GammaFavGEO", 0.8),
        ("GammaUnfavGEO", 1.25),
        ("GammaFavSTR_Psi0", 0.9 * 0.6),
        ("GammaUnfavSTR_Psi0", 1.35 * 0.6),
        ("GammaFavGEO_Psi0", 0.8 * 0.6),
        ("GammaUnfavGEO_Psi0", 1.25 * 0.6),
    ],
)
def test_primary_coefficient_types_match_csharp_switch(
    type_data: str,
    expected: float,
    condition: LoadCondition,
    template_item: LoadTemplateItem,
) -> None:
    coefficient = LoadCombinationItem(type_data=type_data, val=0.75)

    actual = load_assembly._resolve_coefficient(
        coefficient, condition, template_item
    )

    assert actual == expected


@pytest.mark.parametrize(
    ("type_data", "secondary_type", "expected"),
    [
        ("GC", "Number", 0.75),
        ("Psi0_GC", "GammaUnfavSTR", 0.6 * 1.35),
        ("Psi1_GC", "Psi2", 0.4 * 0.2),
        ("Psi2_GC", "GammaFavGEO", 0.2 * 0.8),
        ("GammaFavSTR_GC", "Psi0", 0.9 * 0.6),
        ("GammaUnfavSTR_GC", "Psi1", 1.35 * 0.4),
        ("GammaFavGEO_GC", "Psi2", 0.8 * 0.2),
        ("GammaUnfavGEO_GC", "Number", 1.25 * 0.75),
        ("GammaFavSTR_Psi0_GC", "Psi1", 0.9 * 0.6 * 0.4),
        ("GammaUnfavSTR_Psi0_GC", "Psi2", 1.35 * 0.6 * 0.2),
        ("GammaFavGEO_Psi0_GC", "GammaFavSTR", 0.8 * 0.6 * 0.9),
        ("GammaUnfavGEO_Psi0_GC", "GammaUnfavSTR", 1.25 * 0.6 * 1.35),
    ],
)
def test_gc_coefficient_types_multiply_secondary_csharp_factor(
    type_data: str,
    secondary_type: str,
    expected: float,
    condition: LoadCondition,
    template_item: LoadTemplateItem,
) -> None:
    coefficient = LoadCombinationItem(
        type_data=type_data,
        secondary_type_data=secondary_type,
        val=0.75,
    )

    actual = load_assembly._resolve_coefficient(
        coefficient, condition, template_item
    )

    assert actual == expected


@pytest.mark.parametrize(
    "type_data",
    ["GammaFavSTR_Psi1_GC", "GammaUnfavSTR_Psi1_GC"],
)
def test_psi1_gc_preserves_csharp_unfavourable_gamma_dispatch(
    type_data: str,
    condition: LoadCondition,
    template_item: LoadTemplateItem,
) -> None:
    coefficient = LoadCombinationItem(
        type_data=type_data,
        secondary_type_data="Number",
        val=0.75,
    )

    actual = load_assembly._resolve_coefficient(
        coefficient, condition, template_item
    )

    assert actual == condition.gamma_unfav_str * template_item.psi1 * 0.75


def test_template_coefficient_resolves_through_model_collections(
    condition: LoadCondition,
    template_item: LoadTemplateItem,
) -> None:
    coefficient = LoadCombinationItem(
        row_key=3,
        column_key=condition.id,
        type_data="GammaUnfavSTR_Psi0",
    )
    model = Model(
        collections=Collections(
            analyses={11: Analysis(key=11, load_combination_key=5)},
            load_combinations={5: LoadCombination(key=5, items=[coefficient])},
            load_conditions={condition.id: condition},
        )
    )

    actual = load_assembly._get_load_template_coefficient(
        model, 11, 3, condition.id, template_item
    )

    assert actual == condition.gamma_unfav_str * template_item.psi0


def test_psi_coefficient_without_template_item_is_rejected(
    condition: LoadCondition,
) -> None:
    coefficient = LoadCombinationItem(type_data="Psi0")

    with pytest.raises(ValueError, match="requires a load-template item"):
        load_assembly._resolve_coefficient(coefficient, condition)


def test_unknown_coefficient_type_is_never_silently_zero(
    condition: LoadCondition,
    template_item: LoadTemplateItem,
) -> None:
    coefficient = LoadCombinationItem(type_data="UnknownFutureType")

    with pytest.raises(NotImplementedError, match="UnknownFutureType"):
        load_assembly._resolve_coefficient(
            coefficient, condition, template_item
        )


def test_legacy_assembler_api_reexports_load_module_implementations() -> None:
    assert assembler.assemble_load_vector is load_assembly.assemble_load_vector
    assert assembler.extract_displacements is load_assembly.extract_displacements
    assert assembler.generate_line_loads is load_assembly.generate_line_loads
    assert assembler.generate_self_weight_loads is load_assembly.generate_self_weight_loads
    assert (
        assembler._get_load_template_coefficient
        is load_assembly._get_load_template_coefficient
    )
