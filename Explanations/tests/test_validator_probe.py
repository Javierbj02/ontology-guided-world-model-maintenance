from benchmark.candidate_schema import parse_candidate_output
from benchmark.compiler import compile_candidate_output
from benchmark.validator_probe import prepare_probe_config
from validator.runtime import ExperimentConfig, Step


def make_valid_payload():
    return {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": [
            {
                "rank": 1,
                "event_type_label": "TakeMedicine",
                "event_type_source": "T_op",
                "participants": ["Agent_Nurse", "PhysicalObject_Medicine1"],
                "location": "PhysicalPlace_Corridor1",
                "short_rationale": "The nurse may have taken the medicine.",
                "operational_projection": {
                    "event_class": "DUL.Action",
                    "event_type": "Task_TakeMedicine",
                    "participants": ["Agent_Nurse", "PhysicalObject_Medicine1"],
                    "location": "PhysicalPlace_Corridor1",
                },
            }
        ],
    }


def make_base_cfg():
    cfg = ExperimentConfig(
        ontology_path="data/ontologies/T_op.owl",
        steps=[
            Step(name="Init"),
            Step(name="Observed_loss_of_medicine"),
        ],
        enable_reasoner=False,
        strict_object_loss_mode=True,
    )
    cfg.scenario_id = "test_base_case"
    return cfg


def test_prepare_probe_config_inserts_candidate_before_last_step():
    parsed = parse_candidate_output(make_valid_payload())
    compiled = compile_candidate_output(parsed)[0]
    base_cfg = make_base_cfg()

    probe_cfg = prepare_probe_config(base_cfg, compiled)

    assert len(probe_cfg.steps) == 3
    assert probe_cfg.steps[0].name == "Init"
    assert probe_cfg.steps[1].name == compiled.step.name
    assert probe_cfg.steps[2].name == "Observed_loss_of_medicine"


def test_prepare_probe_config_preserves_basic_flags():
    parsed = parse_candidate_output(make_valid_payload())
    compiled = compile_candidate_output(parsed)[0]
    base_cfg = make_base_cfg()

    probe_cfg = prepare_probe_config(base_cfg, compiled)

    assert probe_cfg.ontology_path == "data/ontologies/T_op.owl"
    assert probe_cfg.enable_reasoner is False
    assert probe_cfg.strict_object_loss_mode is True


def test_prepare_probe_config_sets_probe_scenario_id():
    parsed = parse_candidate_output(make_valid_payload())
    compiled = compile_candidate_output(parsed)[0]
    base_cfg = make_base_cfg()

    probe_cfg = prepare_probe_config(base_cfg, compiled)

    assert probe_cfg.scenario_id == "test_base_case__probe_r1"
