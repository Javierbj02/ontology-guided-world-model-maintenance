from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from benchmark.experiment_runner import ExperimentRunResult, run_generation_experiment


class RawTextGenerator(Protocol):
    def generate_raw_json_text(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class GenerationRunArtifacts:
    prompt: str
    raw_output: str
    experiment_result: ExperimentRunResult


class GenerationService:
    def __init__(self, generator: RawTextGenerator) -> None:
        self.generator = generator

    def run_prompt(self, prompt: str) -> GenerationRunArtifacts:
        raw_output = self.generator.generate_raw_json_text(prompt)
        experiment_result = run_generation_experiment(raw_output)

        return GenerationRunArtifacts(
            prompt=prompt,
            raw_output=raw_output,
            experiment_result=experiment_result,
        )