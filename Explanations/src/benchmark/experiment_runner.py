from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from benchmark.compiler import CompiledCandidate
from benchmark.runner import BenchmarkRunResult, run_candidate_output
from benchmark.scenario_registry import get_case_config
from benchmark.validator_probe import ValidatorProbeResult, run_validator_probe


@dataclass(frozen=True)
class CandidateExperimentResult:
    compiled_candidate: CompiledCandidate
    probe_result: ValidatorProbeResult


@dataclass(frozen=True)
class ExperimentRunResult:
    case_id: Optional[str]
    condition: Optional[str]
    schema_valid: bool
    parse_error: Optional[str]
    benchmark_result: BenchmarkRunResult
    candidate_results: List[CandidateExperimentResult]
    any_strict_pass: bool


def run_generation_experiment(raw_output: str | Dict[str, Any]) -> ExperimentRunResult:
    """
    End-to-end local experiment runner:
    - parse and score output
    - compile candidates
    - probe each candidate against the corresponding unresolved benchmark case
    """
    benchmark_result = run_candidate_output(raw_output)

    if not benchmark_result.schema_valid:
        return ExperimentRunResult(
            case_id=None,
            condition=None,
            schema_valid=False,
            parse_error=benchmark_result.parse_error,
            benchmark_result=benchmark_result,
            candidate_results=[],
            any_strict_pass=False,
        )

    assert benchmark_result.case_id is not None
    case_cfg = get_case_config(benchmark_result.case_id)

    candidate_results: List[CandidateExperimentResult] = []
    for compiled_candidate in benchmark_result.compiled_candidates:
        probe_result = run_validator_probe(case_cfg, compiled_candidate)
        candidate_results.append(
            CandidateExperimentResult(
                compiled_candidate=compiled_candidate,
                probe_result=probe_result,
            )
        )

    any_strict_pass = any(
        cand_result.probe_result.status == "explained"
        for cand_result in candidate_results
    )

    return ExperimentRunResult(
        case_id=benchmark_result.case_id,
        condition=benchmark_result.condition,
        schema_valid=True,
        parse_error=None,
        benchmark_result=benchmark_result,
        candidate_results=candidate_results,
        any_strict_pass=any_strict_pass,
    )