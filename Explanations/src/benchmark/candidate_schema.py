from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


ALLOWED_CONDITIONS = {"PC1", "PC2", "PC3"}
ALLOWED_EVENT_TYPE_SOURCES = {"T_op", "inferred"}
ALLOWED_EVENT_CLASS_V1 = {"DUL.Event", "DUL.Action"}


class CandidateSchemaError(ValueError):
    """Raised when a candidate-generation JSON output does not satisfy the schema."""


def _require_type(value: Any, expected_type: type, field_name: str) -> None:
    if not isinstance(value, expected_type):
        raise CandidateSchemaError(
            f"Field '{field_name}' must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}."
        )


def _require_non_empty_string(value: Any, field_name: str) -> str:
    _require_type(value, str, field_name)
    cleaned = value.strip()
    if not cleaned:
        raise CandidateSchemaError(f"Field '{field_name}' cannot be empty.")
    return cleaned


def _normalize_string_list(value: Any, field_name: str) -> List[str]:
    _require_type(value, list, field_name)

    normalized: List[str] = []
    seen = set()

    for idx, item in enumerate(value):
        if not isinstance(item, str):
            raise CandidateSchemaError(
                f"Field '{field_name}[{idx}]' must be a string, got {type(item).__name__}."
            )
        cleaned = item.strip()
        if not cleaned:
            raise CandidateSchemaError(f"Field '{field_name}[{idx}]' cannot be empty.")
        if cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)

    return normalized


@dataclass(frozen=True)
class OperationalProjection:
    event_class: str
    event_type: str
    participants: List[str]
    location: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationalProjection":
        if not isinstance(data, dict):
            raise CandidateSchemaError(
                f"Field 'operational_projection' must be an object, got {type(data).__name__}."
            )

        event_class = _require_non_empty_string(
            data.get("event_class"),
            "operational_projection.event_class",
        )

        event_type = _require_non_empty_string(
            data.get("event_type"),
            "operational_projection.event_type",
        )

        participants = _normalize_string_list(
            data.get("participants"),
            "operational_projection.participants",
        )
        if len(participants) < 1:
            raise CandidateSchemaError(
                "Field 'operational_projection.participants' must contain at least one participant."
            )

        raw_location = data.get("location")
        if raw_location is None:
            location = None
        else:
            location = _require_non_empty_string(
                raw_location,
                "operational_projection.location",
            )

        if event_class not in ALLOWED_EVENT_CLASS_V1:
            raise CandidateSchemaError(
                f"Unsupported event_class '{event_class}'. Allowed values: {sorted(ALLOWED_EVENT_CLASS_V1)}."
            )

        return cls(
            event_class=event_class,
            event_type=event_type,
            participants=participants,
            location=location,
        )


@dataclass(frozen=True)
class Candidate:
    rank: int
    event_type_label: str
    event_type_source: str
    participants: List[str]
    location: Optional[str]
    short_rationale: str
    operational_projection: OperationalProjection

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candidate":
        if not isinstance(data, dict):
            raise CandidateSchemaError(
                f"Each candidate must be an object, got {type(data).__name__}."
            )

        raw_rank = data.get("rank")
        if not isinstance(raw_rank, int):
            raise CandidateSchemaError(
                f"Field 'rank' must be an integer, got {type(raw_rank).__name__}."
            )
        if raw_rank not in {1, 2, 3}:
            raise CandidateSchemaError("Field 'rank' must be one of {1, 2, 3}.")

        event_type_label = _require_non_empty_string(
            data.get("event_type_label"),
            "event_type_label",
        )
        event_type_source = _require_non_empty_string(
            data.get("event_type_source"),
            "event_type_source",
        )
        if event_type_source not in ALLOWED_EVENT_TYPE_SOURCES:
            raise CandidateSchemaError(
                f"Unsupported event_type_source '{event_type_source}'. "
                f"Allowed values: {sorted(ALLOWED_EVENT_TYPE_SOURCES)}."
            )

        participants = _normalize_string_list(data.get("participants"), "participants")
        if len(participants) < 1:
            raise CandidateSchemaError(
                "Field 'participants' must contain at least one participant."
            )

        raw_location = data.get("location")
        if raw_location is None:
            location = None
        else:
            location = _require_non_empty_string(raw_location, "location")

        short_rationale = _require_non_empty_string(
            data.get("short_rationale"),
            "short_rationale",
        )

        operational_projection = OperationalProjection.from_dict(
            data.get("operational_projection")
        )

        return cls(
            rank=raw_rank,
            event_type_label=event_type_label,
            event_type_source=event_type_source,
            participants=participants,
            location=location,
            short_rationale=short_rationale,
            operational_projection=operational_projection,
        )


@dataclass(frozen=True)
class CandidateOutput:
    case_id: str
    condition: str
    candidates: List[Candidate]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateOutput":
        if not isinstance(data, dict):
            raise CandidateSchemaError(
                f"Top-level output must be an object, got {type(data).__name__}."
            )

        case_id = _require_non_empty_string(data.get("case_id"), "case_id")
        condition = _require_non_empty_string(data.get("condition"), "condition")
        if condition not in ALLOWED_CONDITIONS:
            raise CandidateSchemaError(
                f"Unsupported condition '{condition}'. Allowed values: {sorted(ALLOWED_CONDITIONS)}."
            )

        raw_candidates = data.get("candidates")
        _require_type(raw_candidates, list, "candidates")

        if not (1 <= len(raw_candidates) <= 3):
            raise CandidateSchemaError(
                "Field 'candidates' must contain between 1 and 3 candidates."
            )

        candidates = [Candidate.from_dict(item) for item in raw_candidates]

        ranks = [cand.rank for cand in candidates]
        if len(set(ranks)) != len(ranks):
            raise CandidateSchemaError("Candidate ranks must be unique.")

        if ranks != sorted(ranks):
            raise CandidateSchemaError(
                "Candidates must be ordered by ascending rank (1, 2, 3)."
            )

        return cls(
            case_id=case_id,
            condition=condition,
            candidates=candidates,
        )


def parse_candidate_output(raw_output: str | Dict[str, Any]) -> CandidateOutput:
    if isinstance(raw_output, str):
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise CandidateSchemaError(f"Invalid JSON output: {exc}") from exc
    elif isinstance(raw_output, dict):
        data = raw_output
    else:
        raise CandidateSchemaError(
            f"raw_output must be a JSON string or a dict, got {type(raw_output).__name__}."
        )

    return CandidateOutput.from_dict(data)
