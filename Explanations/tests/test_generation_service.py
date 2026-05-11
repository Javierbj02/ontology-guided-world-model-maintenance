from benchmark.generation_service import GenerationService


class FakeGenerator:
    def __init__(self, raw_output: str) -> None:
        self.raw_output = raw_output

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


def test_generation_service_run_prompt():
    prompt = "Generate top-3 candidate events as JSON."
    generator = FakeGenerator(make_valid_raw_output())
    service = GenerationService(generator)

    artifacts = service.run_prompt(prompt)

    assert artifacts.prompt == prompt
    assert '"case_id": "CG1_base_loss_clean"' in artifacts.raw_output

    result = artifacts.experiment_result
    assert result.schema_valid is True
    assert result.case_id == "CG1_base_loss_clean"
    assert result.condition == "PC3"
    assert result.any_strict_pass is True
    assert len(result.candidate_results) == 1
