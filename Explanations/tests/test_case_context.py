import pytest

from benchmark.case_context import (
    get_case_context,
    get_known_entities,
    list_active_case_ids,
)


def test_get_case_context():
    ctx = get_case_context("CG1_base_loss_clean")

    assert ctx.case_id == "CG1_base_loss_clean"
    assert ctx.status == "active"
    assert "Agent_Nurse" in ctx.known_entities
    assert "PhysicalObject_Medicine1" in ctx.known_entities
    assert "PhysicalPlace_Corridor1" in ctx.known_entities


def test_get_known_entities():
    ents = get_known_entities("CG2_wrong_location_decoy")

    assert "Agent_Nurse" in ents
    assert "PhysicalObject_ShadowTray" in ents
    assert "PhysicalPlace_Room101" in ents


def test_list_active_case_ids():
    case_ids = list_active_case_ids()

    assert "CG1_base_loss_clean" in case_ids
    assert "CG6_nurse_separated_old_decoy" in case_ids
    assert len(case_ids) == 6


def test_unknown_case_raises():
    with pytest.raises(KeyError):
        get_case_context("UNKNOWN_CASE")