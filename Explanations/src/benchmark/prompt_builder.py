from __future__ import annotations

from typing import List

from benchmark.case_context import get_case_context
from benchmark.retrieval_context_builder import format_tbox_context
from benchmark.local_graph_context_builder import format_local_graph_context

ALLOWED_CONDITIONS = {"PC1", "PC2", "PC3"}


def _task_instruction() -> str:
    return (
        "You are assisting a service robot operating in a hospital. "
        "The robot transports medicine on a tray while moving through the environment. "
        "It has wheels for mobility and does not manipulate the medicine with arms. "
        "A mission-critical discrepancy has occurred: the medicine is no longer where the robot expected it to be. "
        "Your task is to propose up to 3 plausible unobserved event hypotheses that could explain the loss. "
        "These hypotheses may go beyond the currently recorded event history. "
        "Assume that direct nurse pickup/removal of the medicine is already a known and reliably observable event pattern in the system. "
        "If such a direct nurse removal had occurred, it would normally have been detected. "
        "Therefore, prioritize alternative unobserved causes unless there is strong reason to involve the nurse in a different, non-standard way. "
        "Prefer hypotheses that describe concrete, reproducible situations that could later be simulated or tested. "
        "Because the discrepancy concerns medicine being transported by the robot, hypotheses should normally treat Agent_Shadow as part of the event context, and operational projections should include Agent_Shadow as a participant whenever the loss mechanism is related to transport, tray context, or removal from the robot's custody. "
    )

    
    
def _json_contract_summary() -> str:
    return (
        'Return a single JSON object with keys: "case_id", "condition", "candidates". '
        'Each candidate must contain: "rank", "event_type_label", "event_type_source", '
        '"participants", "location", "short_rationale", and "operational_projection". '
        'The operational_projection must contain: "event_class", "event_type", "participants", and "location". '
        '"event_class" should be "DUL.Event" or "DUL.Action". '
        '"event_type" must always be provided. It should name an ontology-grounded or plausibly inferred EventType-style identifier. '
        'If no exact ontology type is available, provide a concise inferred identifier such as EventType_AccidentalDisplacement. '
        '"event_type_source" must be exactly one of: "T_op" or "inferred". '
        'If uncertain, use "inferred". Do not invent any other values for event_type_source. '
        'The "location" field must be a physical place identifier or null. '
        'Do not use object identifiers, container identifiers, or placeholder strings like "Unknown" as locations.'
    )
    

def _minimal_symbolic_anchors() -> str:
    return (
        "Minimal symbolic anchors:\n"
        "- missing object id: PhysicalObject_Medicine1\n"
        "- expected tray/source id: PhysicalObject_ShadowTray\n"
        "- robot agent id: Agent_Shadow\n"
        "- main human collaborator id: Agent_Nurse"
    )


def _local_graph_fragment(case_id: str) -> str:
    case_ctx = get_case_context(case_id)
    entities = ", ".join(sorted(case_ctx.known_entities))

    return (
        "Local case context:\n"
        f"- case_id: {case_ctx.case_id}\n"
        f"- description: {case_ctx.description}\n"
        f"- known entities: {entities}"
    )


def build_prompt(case_id: str, condition: str) -> str:
    if condition not in ALLOWED_CONDITIONS:
        raise ValueError(
            f"Unsupported condition '{condition}'. Allowed conditions: {sorted(ALLOWED_CONDITIONS)}."
        )

    case_ctx = get_case_context(case_id)

    sections: List[str] = [
        _task_instruction(),
        f"Case ID: {case_ctx.case_id}",
        f"Condition: {condition}",
        f"Case description: {case_ctx.description}",
        _minimal_symbolic_anchors(),
        _json_contract_summary(),
    ]

    if condition in {"PC2", "PC3"}:
        sections.append(format_tbox_context())

    if condition == "PC3":
        sections.append(format_local_graph_context(case_id))

    sections.append(
        "Important:\n"
        "- return JSON only\n"
        "- do not use markdown fences\n"
        "- do not output explanatory text outside JSON\n"
        "- rank candidates from 1 to at most 3\n"
        "- keep short_rationale concise\n"
        "- do not restrict yourself only to the currently known recorded event history\n"
        "- reuse the provided symbolic IDs whenever possible\n"
        '- if uncertain about event_type_source, use "inferred"\n'
        "- if the location is unknown, use null\n"
        '- do not use placeholder strings such as "Unknown" as a location value\n'
        "- do not use object or tray identifiers as locations; locations should be physical places\n"
        "- prefer concrete and reproducible situations over abstract labels\n"
        "- do not use direct nurse pickup/removal as the default explanation unless the hypothesis clearly differs from the already known observed pattern\n"
        "- when the medicine loss happens from the robot transport context, include Agent_Shadow as a participant in the operational projection\n"
        "- do not leave operational_projection.event_type null; provide a concrete EventType-style identifier\n"
    )

    return "\n\n".join(sections)
