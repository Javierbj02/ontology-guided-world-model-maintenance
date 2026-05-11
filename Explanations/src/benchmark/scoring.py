from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from benchmark.candidate_schema import (
    Candidate,
    CandidateOutput,
    CandidateSchemaError,
    parse_candidate_output,
)


ALLOWED_NOVEL_ENTITY_PREFIXES = (
    "Agent_",
    "PhysicalObject_",
    "PhysicalPlace_",
    "EventType_",
)


@dataclass(frozen=True)
class CandidateScore:
    rank: int
    referenced_entities: List[str]
    grounded_entities: List[str]
    novel_schema_entities: List[str]
    invalid_entities: List[str]
    existing_anchor_rate: float
    novel_schema_rate: float
    grounding_rate: float
    hallucination_rate: float


@dataclass(frozen=True)
class OutputScore:
    case_id: Optional[str]
    condition: Optional[str]
    schema_valid: bool
    parse_error: Optional[str]
    candidate_count: int
    average_existing_anchor_rate: float
    average_novel_schema_rate: float
    average_grounding_rate: float
    average_hallucination_rate: float
    candidates: List[CandidateScore]


def _unique_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _is_novel_schema_entity(symbol: str) -> bool:
    return any(symbol.startswith(prefix) for prefix in ALLOWED_NOVEL_ENTITY_PREFIXES)


def _candidate_referenced_entities(candidate: Candidate) -> List[str]:
    refs: List[str] = []

    # Candidate-level entities
    refs.extend(candidate.participants)
    if candidate.location is not None:
        refs.append(candidate.location)

    # Operational projection entities
    refs.extend(candidate.operational_projection.participants)
    if candidate.operational_projection.location is not None:
        refs.append(candidate.operational_projection.location)

    return _unique_preserve_order(refs)


def score_candidate(candidate: Candidate, known_entities: Set[str]) -> CandidateScore:
    refs = _candidate_referenced_entities(candidate)

    grounded: List[str] = []
    novel_schema: List[str] = []
    invalid: List[str] = []

    for ent in refs:
        if ent in known_entities:
            grounded.append(ent)
        elif _is_novel_schema_entity(ent):
            novel_schema.append(ent)
        else:
            invalid.append(ent)

    total = len(refs)
    if total == 0:
        existing_anchor_rate = 0.0
        novel_schema_rate = 0.0
        grounding_rate = 0.0
        hallucination_rate = 0.0
    else:
        existing_anchor_rate = len(grounded) / total
        novel_schema_rate = len(novel_schema) / total
        grounding_rate = (len(grounded) + len(novel_schema)) / total
        hallucination_rate = len(invalid) / total

    return CandidateScore(
        rank=candidate.rank,
        referenced_entities=refs,
        grounded_entities=grounded,
        novel_schema_entities=novel_schema,
        invalid_entities=invalid,
        existing_anchor_rate=existing_anchor_rate,
        novel_schema_rate=novel_schema_rate,
        grounding_rate=grounding_rate,
        hallucination_rate=hallucination_rate,
    )


def score_candidate_output(
    candidate_output: CandidateOutput,
    known_entities: Set[str],
) -> OutputScore:
    candidate_scores = [
        score_candidate(candidate, known_entities)
        for candidate in candidate_output.candidates
    ]

    if candidate_scores:
        avg_existing_anchor = (
            sum(c.existing_anchor_rate for c in candidate_scores) / len(candidate_scores)
        )
        avg_novel_schema = (
            sum(c.novel_schema_rate for c in candidate_scores) / len(candidate_scores)
        )
        avg_grounding = (
            sum(c.grounding_rate for c in candidate_scores) / len(candidate_scores)
        )
        avg_hallucination = (
            sum(c.hallucination_rate for c in candidate_scores) / len(candidate_scores)
        )
    else:
        avg_existing_anchor = 0.0
        avg_novel_schema = 0.0
        avg_grounding = 0.0
        avg_hallucination = 0.0

    return OutputScore(
        case_id=candidate_output.case_id,
        condition=candidate_output.condition,
        schema_valid=True,
        parse_error=None,
        candidate_count=len(candidate_output.candidates),
        average_existing_anchor_rate=avg_existing_anchor,
        average_novel_schema_rate=avg_novel_schema,
        average_grounding_rate=avg_grounding,
        average_hallucination_rate=avg_hallucination,
        candidates=candidate_scores,
    )


def score_raw_output(
    raw_output: str | Dict[str, Any],
    known_entities: Set[str],
) -> OutputScore:
    """
    Parse and score a raw model output.

    If parsing fails, return a schema-invalid score object instead of raising.
    """
    try:
        parsed = parse_candidate_output(raw_output)
    except CandidateSchemaError as exc:
        return OutputScore(
            case_id=None,
            condition=None,
            schema_valid=False,
            parse_error=str(exc),
            candidate_count=0,
            average_existing_anchor_rate=0.0,
            average_novel_schema_rate=0.0,
            average_grounding_rate=0.0,
            average_hallucination_rate=0.0,
            candidates=[],
        )

    return score_candidate_output(parsed, known_entities)