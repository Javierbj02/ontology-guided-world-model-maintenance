from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from benchmark.candidate_schema import CandidateOutput, CandidateSchemaError, parse_candidate_output
from benchmark.case_context import get_case_context
from benchmark.compiler import CompiledCandidate, compile_candidate_output
from benchmark.scoring import OutputScore, score_candidate_output


@dataclass(frozen=True)
class BenchmarkRunResult:
    case_id: Optional[str]
    condition: Optional[str]
    schema_valid: bool
    parse_error: Optional[str]
    score: OutputScore
    compiled_candidates: List[CompiledCandidate]


def run_candidate_output(raw_output: str | Dict[str, Any]) -> BenchmarkRunResult:
    """
    Parse, score, and compile a candidate-generation output.

    If parsing fails, return a schema-invalid result with no compiled candidates.
    """
    try:
        parsed = parse_candidate_output(raw_output)
    except CandidateSchemaError as exc:
        invalid_score = OutputScore(
            case_id=None,
            condition=None,
            schema_valid=False,
            parse_error=str(exc),
            candidate_count=0,
            average_grounding_rate=0.0,
            average_hallucination_rate=0.0,
            average_existing_anchor_rate=0.0,
            average_novel_schema_rate=0.0,
            candidates=[],
        )
        return BenchmarkRunResult(
            case_id=None,
            condition=None,
            schema_valid=False,
            parse_error=str(exc),
            score=invalid_score,
            compiled_candidates=[],
        )

    return run_parsed_candidate_output(parsed)


def run_parsed_candidate_output(candidate_output: CandidateOutput) -> BenchmarkRunResult:
    """
    Score and compile a previously parsed candidate output.
    """
    case_ctx = get_case_context(candidate_output.case_id)
    score = score_candidate_output(candidate_output, case_ctx.known_entities)
    compiled = compile_candidate_output(candidate_output)

    return BenchmarkRunResult(
        case_id=candidate_output.case_id,
        condition=candidate_output.condition,
        schema_valid=True,
        parse_error=None,
        score=score,
        compiled_candidates=compiled,
    )