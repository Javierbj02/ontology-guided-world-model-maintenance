from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from benchmark.candidate_schema import Candidate, CandidateOutput
from validator.runtime import Step


Triple = Tuple[str, str, str]


@dataclass(frozen=True)
class CompiledCandidate:
    case_id: str
    rank: int
    event_id: str
    step_name: str
    step: Step


def _safe_token(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", text.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "X"


def make_generated_event_id(case_id: str, rank: int) -> str:
    return f"GeneratedEvent_{_safe_token(case_id)}_R{rank}"


def make_step_name(case_id: str, rank: int) -> str:
    return f"GEN_{_safe_token(case_id)}_R{rank}"


def compile_candidate_to_step(case_id: str, candidate: Candidate) -> CompiledCandidate:
    """
    Compile a validated Candidate into a deterministic runtime Step.

    Compilation rules:
    - one generated event instance per candidate
    - event instance is typed via projection.event_class
    - event_type instance is typed as SOMA.EventType
    - SOMA.isOccurrenceOf is always asserted
    - participant assertions sorted alphabetically
    - location assertion added last if present
    """
    projection = candidate.operational_projection
    event_id = make_generated_event_id(case_id, candidate.rank)
    step_name = make_step_name(case_id, candidate.rank)

    asserts: List[Triple] = [
        (event_id, "SOMA.isOccurrenceOf", projection.event_type),
    ]

    for participant in sorted(projection.participants):
        asserts.append((event_id, "DUL.hasParticipant", participant))

    if projection.location is not None:
        asserts.append((event_id, "DUL.hasLocation", projection.location))

    step = Step(
        name=step_name,
        types=[
            (event_id, projection.event_class),
            (projection.event_type, "SOMA.EventType"),
        ],
        asserts=asserts,
        retracts=[],
        updates=[],
        tags=[],
        deletes=[],
    )

    return CompiledCandidate(
        case_id=case_id,
        rank=candidate.rank,
        event_id=event_id,
        step_name=step_name,
        step=step,
    )


def compile_candidate_output(candidate_output: CandidateOutput) -> List[CompiledCandidate]:
    compiled: List[CompiledCandidate] = []
    for candidate in candidate_output.candidates:
        compiled.append(compile_candidate_to_step(candidate_output.case_id, candidate))
    return compiled