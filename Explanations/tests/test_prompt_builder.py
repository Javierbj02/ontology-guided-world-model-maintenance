import pytest

from benchmark.prompt_builder import build_prompt


def test_build_prompt_pc1():
    prompt = build_prompt("CG1_base_loss_clean", "PC1")

    assert "Case ID: CG1_base_loss_clean" in prompt
    assert "Condition: PC1" in prompt
    assert "Case description:" in prompt
    assert "hospital" in prompt.lower()
    assert "tray" in prompt.lower()
    assert "wheels" in prompt.lower()

    assert "Minimal symbolic anchors:" in prompt
    assert "PhysicalObject_Medicine1" in prompt
    assert "PhysicalObject_ShadowTray" in prompt
    assert "Agent_Shadow" in prompt
    assert "Agent_Nurse" in prompt

    assert "Retrieved TBox context from T_op:" not in prompt
    assert "Local case context:" not in prompt


def test_build_prompt_pc2():
    prompt = build_prompt("CG1_base_loss_clean", "PC2")

    assert "Condition: PC2" in prompt
    assert "Retrieved TBox context from T_op:" in prompt
    assert "[TBOX CHUNK 1]" in prompt
    assert "Local case context:" not in prompt


def test_build_prompt_pc3():
    prompt = build_prompt("CG2_wrong_location_decoy", "PC3")

    assert "Condition: PC3" in prompt
    assert "Retrieved TBox context from T_op:" in prompt
    assert "Retrieved local ABox context:" in prompt
    assert "Agent_Nurse" in prompt
    assert "PhysicalObject_Medicine1" in prompt


def test_build_prompt_invalid_condition():
    with pytest.raises(ValueError):
        build_prompt("CG1_base_loss_clean", "C99")
