from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from benchmark.case_context import get_case_context


Triple = Tuple[str, str, str]


ANCHOR_ENTITIES = [
    "PhysicalObject_Medicine1",
    "PhysicalObject_ShadowTray",
    "Agent_Shadow",
    "Agent_Nurse",
]

RELEVANT_PROPS = {
    "DUL.hasLocation",
    "DUL.hasParticipant",
    "DUL.hasPart",
    "DUL.partOf",
    "SOMA.isOccurrenceOf",
    "DUL.executesTask",
}


@dataclass(frozen=True)
class LocalGraphContext:
    case_id: str
    anchors: List[str]
    triples: List[Triple]
    entities_seen: List[str]


def _safe_get_attr(obj, name: str, default):
    return getattr(obj, name, default)


def build_local_graph_context(case_id: str) -> LocalGraphContext:
    """
    Build a compact local graph context from the case context object.

    Expected case_context structure:
    - known_entities: iterable[str]
    - known_triples or triples or local_triples: iterable[(s, p, o)]   (optional)

    If no triples are available yet, the function falls back to an empty triple set
    plus the anchors that exist in known_entities.
    """
    case_ctx = get_case_context(case_id)

    known_entities = set(_safe_get_attr(case_ctx, "known_entities", set()) or set())

    raw_triples = (
        _safe_get_attr(case_ctx, "known_triples", None)
        or _safe_get_attr(case_ctx, "triples", None)
        or _safe_get_attr(case_ctx, "local_triples", None)
        or []
    )

    triples: List[Triple] = []
    for item in raw_triples:
        if not isinstance(item, (tuple, list)) or len(item) != 3:
            continue
        s, p, o = item
        if not all(isinstance(x, str) for x in (s, p, o)):
            continue
        if p not in RELEVANT_PROPS:
            continue
        triples.append((s, p, o))

    active_anchors = [a for a in ANCHOR_ENTITIES if a in known_entities]

    # Keep only triples touching at least one anchor directly
    filtered: List[Triple] = []
    entities_seen: Set[str] = set(active_anchors)

    for s, p, o in triples:
        if s in active_anchors or o in active_anchors:
            filtered.append((s, p, o))
            entities_seen.add(s)
            entities_seen.add(o)

    # One-hop expansion from already kept entities
    expanded: List[Triple] = list(filtered)
    for s, p, o in triples:
        if (s, p, o) in filtered:
            continue
        if s in entities_seen or o in entities_seen:
            expanded.append((s, p, o))
            entities_seen.add(s)
            entities_seen.add(o)

    expanded = sorted(set(expanded))
    entities_seen_sorted = sorted(entities_seen)

    return LocalGraphContext(
        case_id=case_id,
        anchors=active_anchors,
        triples=expanded,
        entities_seen=entities_seen_sorted,
    )


def format_local_graph_context(case_id: str) -> str:
    ctx = build_local_graph_context(case_id)

    lines = ["Retrieved local ABox context:"]
    lines.append(f"case_id: {ctx.case_id}")

    if ctx.anchors:
        lines.append(f"anchors: {', '.join(ctx.anchors)}")

    if not ctx.triples:
        if ctx.entities_seen:
            lines.append(f"entities: {', '.join(ctx.entities_seen)}")
        else:
            lines.append("- no local triples available")
        return "\n".join(lines)

    for idx, (s, p, o) in enumerate(ctx.triples, start=1):
        lines.append(f"[TRIPLE {idx}] {s} --{p}--> {o}")

    return "\n".join(lines)