from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from benchmark.experiment_runner import ExperimentRunResult


def _serialize_probe_result(probe_result) -> Dict[str, Any]:
    raw_result = probe_result.raw_result or {}
    explanations = raw_result.get("explanations", []) or []

    serialized_explanations = []
    for exp in explanations:
        serialized_explanations.append(
            {
                "event_name": getattr(exp, "event_name", None),
                "event_iri": getattr(exp, "event_iri", None),
                "reason": getattr(exp, "reason", None),
            }
        )

    return {
        "scenario_id": probe_result.scenario_id,
        "candidate_rank": probe_result.candidate_rank,
        "candidate_event_id": probe_result.candidate_event_id,
        "status": probe_result.status,
        "failed_step": probe_result.failed_step,
        "selected_support_event": probe_result.selected_support_event,
        "errors": list(probe_result.errors),
        "raw_result": {
            "scenario_id": raw_result.get("scenario_id"),
            "status": raw_result.get("status"),
            "failed_step": raw_result.get("failed_step"),
            "errors": list(raw_result.get("errors", []) or []),
            "explanations": serialized_explanations,
        },
    }


def experiment_result_to_dict(result: ExperimentRunResult) -> Dict[str, Any]:
    return {
        "case_id": result.case_id,
        "condition": result.condition,
        "schema_valid": result.schema_valid,
        "parse_error": result.parse_error,
        "any_strict_pass": result.any_strict_pass,
        "benchmark_result": {
            "case_id": result.benchmark_result.case_id,
            "condition": result.benchmark_result.condition,
            "schema_valid": result.benchmark_result.schema_valid,
            "parse_error": result.benchmark_result.parse_error,
            "candidate_count": result.benchmark_result.score.candidate_count,
            "average_existing_anchor_rate": result.benchmark_result.score.average_existing_anchor_rate,
            "average_novel_schema_rate": result.benchmark_result.score.average_novel_schema_rate,
            "average_grounding_rate": result.benchmark_result.score.average_grounding_rate,
            "average_hallucination_rate": result.benchmark_result.score.average_hallucination_rate,
            "candidates": [
                {
                    "rank": cand.rank,
                    "referenced_entities": list(cand.referenced_entities),
                    "grounded_entities": list(cand.grounded_entities),
                    "novel_schema_entities": list(cand.novel_schema_entities),
                    "invalid_entities": list(cand.invalid_entities),
                    "grounding_rate": cand.grounding_rate,
                    "hallucination_rate": cand.hallucination_rate,
                    "existing_anchor_rate": cand.existing_anchor_rate,
                    "novel_schema_rate": cand.novel_schema_rate,
                }
                for cand in result.benchmark_result.score.candidates
            ],
        },
        "candidate_results": [
            {
                "compiled_candidate": {
                    "case_id": cand_result.compiled_candidate.case_id,
                    "rank": cand_result.compiled_candidate.rank,
                    "event_id": cand_result.compiled_candidate.event_id,
                    "step_name": cand_result.compiled_candidate.step_name,
                    "step": {
                        "name": cand_result.compiled_candidate.step.name,
                        "types": list(cand_result.compiled_candidate.step.types),
                        "asserts": list(cand_result.compiled_candidate.step.asserts),
                    },
                },
                "probe_result": _serialize_probe_result(cand_result.probe_result),
            }
            for cand_result in result.candidate_results
        ],
    }


def experiment_result_summary_row(result: ExperimentRunResult) -> Dict[str, Any]:
    strict_pass_count = sum(
        1 for cand_result in result.candidate_results
        if cand_result.probe_result.status == "explained"
    )

    top1_probe = result.candidate_results[0].probe_result if result.candidate_results else None

    return {
        "case_id": result.case_id,
        "condition": result.condition,
        "schema_valid": result.schema_valid,
        "parse_error": result.parse_error,
        "candidate_count": result.benchmark_result.score.candidate_count,
        "average_grounding_rate": result.benchmark_result.score.average_grounding_rate,
        "average_hallucination_rate": result.benchmark_result.score.average_hallucination_rate,
        "any_strict_pass": result.any_strict_pass,
        "strict_pass_count": strict_pass_count,
        "top1_status": None if top1_probe is None else top1_probe.status,
        "top1_selected_support_event": None if top1_probe is None else top1_probe.selected_support_event,
        "average_existing_anchor_rate": result.benchmark_result.score.average_existing_anchor_rate,
        "average_novel_schema_rate": result.benchmark_result.score.average_novel_schema_rate,
    }


def save_experiment_result_json(path: str | Path, result: ExperimentRunResult) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(experiment_result_to_dict(result), f, indent=2, ensure_ascii=False)


def save_summary_rows_jsonl(path: str | Path, rows: List[Dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")