from benchmark.experiment_runner import run_generation_experiment


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


def test_run_generation_experiment_valid():
    payload = make_valid_payload()
    result = run_generation_experiment(payload)

    assert result.schema_valid is True
    assert result.parse_error is None
    assert result.case_id == "CG1_base_loss_clean"
    assert result.condition == "PC3"

    assert result.benchmark_result.score.schema_valid is True
    assert len(result.candidate_results) == 1

    cand_result = result.candidate_results[0]
    assert cand_result.compiled_candidate.rank == 1
    assert cand_result.probe_result.candidate_rank == 1

    assert result.any_strict_pass is True
    assert cand_result.probe_result.status == "explained"


def test_run_generation_experiment_invalid():
    payload = {
        "case_id": "CG1_base_loss_clean",
        "condition": "PC3",
        "candidates": [],
    }

    result = run_generation_experiment(payload)

    assert result.schema_valid is False
    assert result.parse_error is not None

    # Schema-invalid payloads may still preserve top-level identifiers.
    assert result.benchmark_result.schema_valid is False
    assert result.benchmark_result.score.schema_valid is False
    assert result.benchmark_result.score.candidate_count == 0
    assert result.benchmark_result.score.average_existing_anchor_rate == 0.0
    assert result.benchmark_result.score.average_novel_schema_rate == 0.0
    assert result.benchmark_result.score.average_grounding_rate == 0.0
    assert result.benchmark_result.score.average_hallucination_rate == 0.0

    assert result.candidate_results == []
    assert result.any_strict_pass is False
