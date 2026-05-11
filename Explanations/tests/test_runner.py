from benchmark.runner import run_candidate_output


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


def test_run_candidate_output_valid():
    payload = make_valid_payload()
    result = run_candidate_output(payload)

    assert result.schema_valid is True
    assert result.parse_error is None
    assert result.case_id == "CG1_base_loss_clean"
    assert result.condition == "PC3"

    assert result.score.schema_valid is True
    assert result.score.candidate_count == 1
    assert result.score.average_grounding_rate == 1.0
    assert result.score.average_hallucination_rate == 0.0

    assert len(result.compiled_candidates) == 1
    assert result.compiled_candidates[0].event_id == "GeneratedEvent_CG1_base_loss_clean_R1"
    assert result.compiled_candidates[0].step.name == "GEN_CG1_base_loss_clean_R1"


def test_run_candidate_output_invalid():
    payload = {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": [],
    }

    result = run_candidate_output(payload)

    assert result.schema_valid is False
    assert result.parse_error is not None

    # Schema-invalid payloads may still preserve top-level identifiers.
    assert result.score.schema_valid is False
    assert result.score.candidate_count == 0
    assert result.score.average_existing_anchor_rate == 0.0
    assert result.score.average_novel_schema_rate == 0.0
    assert result.score.average_grounding_rate == 0.0
    assert result.score.average_hallucination_rate == 0.0
    assert result.compiled_candidates == []
