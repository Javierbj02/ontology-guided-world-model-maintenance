from pathlib import Path

from benchmark.pipeline import make_run_id, run_single_case_condition
from benchmark.cohere_client import CohereCallMetrics


class FakeGenerator:
    def __init__(self, raw_output: str) -> None:
        self.raw_output = raw_output
        self.last_metrics = CohereCallMetrics(
            provider="cohere",
            model="command-a-03-2025",
            api_latency_s=0.42,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            prompt_chars=500,
            response_chars=len(raw_output),
        )

    def generate_raw_json_text(self, prompt: str) -> str:
        return self.raw_output


def make_valid_raw_output() -> str:
    return """
    {
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
            "location": "PhysicalPlace_Corridor1"
          }
        }
      ]
    }
    """.strip()


def test_make_run_id():
    assert make_run_id("CG1_base_loss_clean", "PC3", 3) == "CG1_base_loss_clean__PC3__run3"


def test_run_single_case_condition_without_saving():
    generator = FakeGenerator(make_valid_raw_output())

    result = run_single_case_condition(
        case_id="CG1_base_loss_clean",
        condition="PC3",
        run_index=1,
        output_dir=None,
        generator=generator,
    )

    assert result.run_id == "CG1_base_loss_clean__PC3__run1"
    assert result.case_id == "CG1_base_loss_clean"
    assert result.condition == "PC3"
    assert result.output_dir is None
    assert result.summary_row["schema_valid"] is True


def test_run_single_case_condition_with_saving(tmp_path: Path):
    generator = FakeGenerator(make_valid_raw_output())

    result = run_single_case_condition(
        case_id="CG1_base_loss_clean",
        condition="PC3",
        run_index=2,
        output_dir=tmp_path,
        generator=generator,
    )

    assert result.run_id == "CG1_base_loss_clean__PC3__run2"
    assert result.output_dir == tmp_path

    prompt_path = tmp_path / "CG1_base_loss_clean__PC3__run2__prompt.txt"
    raw_path = tmp_path / "CG1_base_loss_clean__PC3__run2__raw_output.txt"
    result_path = tmp_path / "CG1_base_loss_clean__PC3__run2__result.json"
    summary_path = tmp_path / "summary.jsonl"

    assert prompt_path.exists()
    assert raw_path.exists()
    assert result_path.exists()
    assert summary_path.exists()

    assert "CG1_base_loss_clean" in result_path.read_text(encoding="utf-8")
    
    assert result.call_metrics is not None
    assert result.summary_row["api_latency_s"] == 0.42
    assert result.summary_row["input_tokens"] == 100
    assert result.summary_row["output_tokens"] == 50
    assert result.summary_row["total_tokens"] == 150
    
    
