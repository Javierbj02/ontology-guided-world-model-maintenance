from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


Triple = Tuple[str, str, str]


@dataclass(frozen=True)
class CaseContext:
    case_id: str
    status: str
    description: str
    known_entities: Set[str]
    known_triples: List[Triple]


def _shared_transport_entities() -> Set[str]:
    return {
        "PhysicalObject_Medicine1",
        "PhysicalObject_ShadowTray",
        "Agent_Shadow",
        "Agent_Nurse",
        "PhysicalPlace_Corridor1",
    }


def _shared_transport_triples() -> List[Triple]:
    return [
        ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
        ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
        ("Agent_Shadow", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
        ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
    ]


CASE_CONTEXTS: Dict[str, CaseContext] = {
    "CG1_base_loss_clean": CaseContext(
        case_id="CG1_base_loss_clean",
        status="active",
        description=(
            "Base unresolved medicine-loss case. Nurse and medicine remain locally compatible. "
            "No admissible support event is present."
        ),
        known_entities=_shared_transport_entities(),
        known_triples=_shared_transport_triples(),
    ),
    "CG2_wrong_location_decoy": CaseContext(
        case_id="CG2_wrong_location_decoy",
        status="active",
        description=(
            "Object-loss case with a wrong-location decoy already present."
        ),
        known_entities=_shared_transport_entities() | {"PhysicalPlace_Room101"},
        known_triples=_shared_transport_triples(),
    ),
    "CG3_old_decoy": CaseContext(
        case_id="CG3_old_decoy",
        status="active",
        description=(
            "Object-loss case with an old/out-of-window decoy event in the recent history."
        ),
        known_entities=_shared_transport_entities(),
        known_triples=_shared_transport_triples(),
    ),
    "CG4_nurse_separated_clean": CaseContext(
        case_id="CG4_nurse_separated_clean",
        status="active",
        description=(
            "Object-loss case where the nurse has moved away from the robot transport context."
        ),
        known_entities={
            "PhysicalObject_Medicine1",
            "PhysicalObject_ShadowTray",
            "Agent_Shadow",
            "Agent_Nurse",
            "PhysicalPlace_Corridor1",
            "PhysicalPlace_Room101",
        },
        known_triples=[
            ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
            ("Agent_Shadow", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
            ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Room101"),
        ],
    ),
    "CG5_nurse_separated_wrong_location_decoy": CaseContext(
        case_id="CG5_nurse_separated_wrong_location_decoy",
        status="active",
        description=(
            "Object-loss case with nurse separated and a wrong-location decoy present."
        ),
        known_entities={
            "PhysicalObject_Medicine1",
            "PhysicalObject_ShadowTray",
            "Agent_Shadow",
            "Agent_Nurse",
            "PhysicalPlace_Corridor1",
            "PhysicalPlace_Room101",
        },
        known_triples=[
            ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
            ("Agent_Shadow", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
            ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Room101"),
        ],
    ),
    "CG6_nurse_separated_old_decoy": CaseContext(
        case_id="CG6_nurse_separated_old_decoy",
        status="active",
        description=(
            "Object-loss case with nurse separated and an old/out-of-window decoy present."
        ),
        known_entities={
            "PhysicalObject_Medicine1",
            "PhysicalObject_ShadowTray",
            "Agent_Shadow",
            "Agent_Nurse",
            "PhysicalPlace_Corridor1",
            "PhysicalPlace_Room101",
        },
        known_triples=[
            ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ("PhysicalObject_ShadowTray", "DUL.hasLocation", "Agent_Shadow"),
            ("Agent_Shadow", "DUL.hasLocation", "PhysicalPlace_Corridor1"),
            ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Room101"),
        ],
    ),
}


def get_case_context(case_id: str) -> CaseContext:
    return CASE_CONTEXTS[case_id]


def get_known_entities(case_id: str) -> Set[str]:
    return set(get_case_context(case_id).known_entities)


def list_active_case_ids() -> List[str]:
    return sorted(
        case_id
        for case_id, ctx in CASE_CONTEXTS.items()
        if ctx.status == "active"
    )