import pytest

from benchmark.scenario_registry import get_case_config, list_registered_case_ids


def test_list_registered_case_ids():
    case_ids = list_registered_case_ids()

    assert "CG1_base_loss_clean" in case_ids
    assert "CG2_wrong_location_decoy" in case_ids
    assert "CG3_old_decoy" in case_ids
    assert "CG4_nurse_separated_clean" in case_ids
    assert "CG5_nurse_separated_wrong_location_decoy" in case_ids
    assert "CG6_nurse_separated_old_decoy" in case_ids
    assert len(case_ids) == 6


def test_get_case_config():
    cfg = get_case_config("CG1_base_loss_clean")

    assert cfg.scenario_id == "CG1_base_loss_clean"
    assert cfg.enable_reasoner is False
    assert cfg.strict_object_loss_mode is True


def test_unknown_case_raises():
    with pytest.raises(KeyError):
        get_case_config("UNKNOWN_CASE")