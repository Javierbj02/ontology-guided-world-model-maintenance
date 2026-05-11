from pathlib import Path

from benchmark.experiment_runner import run_generation_experiment
from benchmark.results_io import (
    experiment_result_summary_row,
    experiment_result_to_dict,
    save_experiment_result_json,
    save_summary_rows_jsonl,
)


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


def test_experiment_result_to_dict():
    result = run_generation_experiment(make_valid_payload())
    data = experiment_result_to_dict(result)

    assert data["case_id"] == "CG1_base_loss_clean"
    assert data["condition"] == "PC3"
    assert data["schema_valid"] is True
    assert data["any_strict_pass"] is True
    assert len(data["candidate_results"]) == 1

    bench = data["benchmark_result"]
    assert bench["average_existing_anchor_rate"] == 1.0
    assert bench["average_novel_schema_rate"] == 0.0
    assert bench["average_grounding_rate"] == 1.0
    assert bench["average_hallucination_rate"] == 0.0

    cand = bench["candidates"][0]
    assert cand["existing_anchor_rate"] == 1.0
    assert cand["novel_schema_rate"] == 0.0


def test_experiment_result_summary_row():
    result = run_generation_experiment(make_valid_payload())
    row = experiment_result_summary_row(result)

    assert row["case_id"] == "CG1_base_loss_clean"
    assert row["condition"] == "PC3"
    assert row["schema_valid"] is True
    assert row["candidate_count"] == 1
    assert row["any_strict_pass"] is True
    assert row["strict_pass_count"] == 1
    assert row["top1_status"] == "explained"
    assert row["average_existing_anchor_rate"] == 1.0
    assert row["average_novel_schema_rate"] == 0.0


def test_save_experiment_result_json(tmp_path: Path):
    result = run_generation_experiment(make_valid_payload())
    out_path = tmp_path / "result.json"

    save_experiment_result_json(out_path, result)

    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert "CG1_base_loss_clean" in text
    assert "TakeMedicine" in text
    assert "average_existing_anchor_rate" in text
    assert "average_novel_schema_rate" in text


def test_save_summary_rows_jsonl(tmp_path: Path):
    result = run_generation_experiment(make_valid_payload())
    row = experiment_result_summary_row(result)
    out_path = tmp_path / "summary.jsonl"

    save_summary_rows_jsonl(out_path, [row])

    assert out_path.exists()
    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "CG1_base_loss_clean" in lines[0]
    assert "average_existing_anchor_rate" in lines[0]
    assert "average_novel_schema_rate" in lines[0]
