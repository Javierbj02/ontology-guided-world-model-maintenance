from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from benchmark.cohere_client import CohereCandidateGenerator, CohereGenerationConfig
from benchmark.generation_service import GenerationRunArtifacts, GenerationService
from benchmark.prompt_builder import build_prompt
from benchmark.results_io import (
    experiment_result_summary_row,
    save_experiment_result_json,
    save_summary_rows_jsonl,
)
from project_paths import resolve_project_path


@dataclass(frozen=True)
class PipelineRunArtifacts:
    run_id: str
    case_id: str
    condition: str
    prompt: str
    raw_output: str
    summary_row: dict
    output_dir: Optional[Path]
    call_metrics: Optional[dict]


def make_run_id(case_id: str, condition: str, run_index: int) -> str:
    return f"{case_id}__{condition}__run{run_index}"


def save_generation_artifacts(
    output_dir: str | Path,
    run_id: str,
    artifacts: GenerationRunArtifacts,
    call_metrics: Optional[dict],
) -> PipelineRunArtifacts:
    out_dir = resolve_project_path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = out_dir / f"{run_id}__prompt.txt"
    raw_output_path = out_dir / f"{run_id}__raw_output.txt"
    result_json_path = out_dir / f"{run_id}__result.json"
    summary_jsonl_path = out_dir / "summary.jsonl"
    metrics_json_path = out_dir / f"{run_id}__call_metrics.json"

    prompt_path.write_text(artifacts.prompt, encoding="utf-8")
    raw_output_path.write_text(artifacts.raw_output, encoding="utf-8")
    save_experiment_result_json(result_json_path, artifacts.experiment_result)

    summary_row = experiment_result_summary_row(artifacts.experiment_result)
    if call_metrics is not None:
        summary_row = {
            **summary_row,
            "provider": call_metrics.get("provider"),
            "model": call_metrics.get("model"),
            "api_latency_s": call_metrics.get("api_latency_s"),
            "input_tokens": call_metrics.get("input_tokens"),
            "output_tokens": call_metrics.get("output_tokens"),
            "total_tokens": call_metrics.get("total_tokens"),
            "prompt_chars": call_metrics.get("prompt_chars"),
            "response_chars": call_metrics.get("response_chars"),
        }
        metrics_json_path.write_text(
            json.dumps(call_metrics, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    save_summary_rows_jsonl(summary_jsonl_path, [summary_row])

    return PipelineRunArtifacts(
        run_id=run_id,
        case_id=artifacts.experiment_result.case_id or "UNKNOWN_CASE",
        condition=artifacts.experiment_result.condition or "UNKNOWN_CONDITION",
        prompt=artifacts.prompt,
        raw_output=artifacts.raw_output,
        summary_row=summary_row,
        output_dir=out_dir,
        call_metrics=call_metrics,
    )


def run_single_case_condition(
    case_id: str,
    condition: str,
    run_index: int = 1,
    output_dir: str | Path | None = None,
    generator=None,
) -> PipelineRunArtifacts:
    prompt = build_prompt(case_id, condition)

    if generator is None:
        generator = CohereCandidateGenerator(
            config=CohereGenerationConfig()
        )

    service = GenerationService(generator)
    artifacts = service.run_prompt(prompt)

    run_id = make_run_id(case_id, condition, run_index)

    raw_metrics = getattr(generator, "last_metrics", None)
    call_metrics = asdict(raw_metrics) if raw_metrics is not None else None

    if output_dir is None:
        summary_row = experiment_result_summary_row(artifacts.experiment_result)
        if call_metrics is not None:
            summary_row = {
                **summary_row,
                "provider": call_metrics.get("provider"),
                "model": call_metrics.get("model"),
                "api_latency_s": call_metrics.get("api_latency_s"),
                "input_tokens": call_metrics.get("input_tokens"),
                "output_tokens": call_metrics.get("output_tokens"),
                "total_tokens": call_metrics.get("total_tokens"),
                "prompt_chars": call_metrics.get("prompt_chars"),
                "response_chars": call_metrics.get("response_chars"),
            }

        return PipelineRunArtifacts(
            run_id=run_id,
            case_id=artifacts.experiment_result.case_id or "UNKNOWN_CASE",
            condition=artifacts.experiment_result.condition or "UNKNOWN_CONDITION",
            prompt=artifacts.prompt,
            raw_output=artifacts.raw_output,
            summary_row=summary_row,
            output_dir=None,
            call_metrics=call_metrics,
        )

    return save_generation_artifacts(output_dir, run_id, artifacts, call_metrics)
