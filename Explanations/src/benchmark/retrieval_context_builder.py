from __future__ import annotations

from functools import lru_cache
from typing import Dict, Iterable, List, Set, Tuple

from benchmark.ontology_chunk_builder import OntologyChunk, build_ontology_chunks
from project_paths import resolve_project_path


DEFAULT_T_OP_PATH = str(resolve_project_path("data/ontologies/T_op.ttl"))


CLASS_SEEDS = {
    "Agent",
    "Object",
    "PhysicalObject",
    "PhysicalPlace",
    "Event",
    "EventType",
}

PROPERTY_SEEDS = {
    "hasParticipant",
    "hasLocation",
    "isOccurrenceOf",
    "hasPart",
    "partOf",
    "hasComponent",
}


@lru_cache(maxsize=8)
def _load_t_op_chunks(ontology_path: str) -> Tuple[OntologyChunk, ...]:
    return tuple(build_ontology_chunks(ontology_path))


def _index_chunks(chunks: Iterable[OntologyChunk]) -> Dict[str, OntologyChunk]:
    return {chunk.local_name: chunk for chunk in chunks}


def _children_map(chunks: Iterable[OntologyChunk]) -> Dict[str, Set[str]]:
    children: Dict[str, Set[str]] = {}
    for chunk in chunks:
        for parent in chunk.parents:
            children.setdefault(parent, set()).add(chunk.local_name)
    return children


def _closure_from_seeds(
    seeds: Set[str],
    child_map: Dict[str, Set[str]],
) -> List[str]:
    visited: Set[str] = set()
    stack: List[str] = sorted(seeds)

    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for child in sorted(child_map.get(cur, set()), reverse=True):
            if child not in visited:
                stack.append(child)

    return sorted(visited)


def retrieve_validator_guided_tbox_chunks(
    ontology_path: str = DEFAULT_T_OP_PATH,
) -> List[OntologyChunk]:
    chunks = list(_load_t_op_chunks(ontology_path))
    by_name = _index_chunks(chunks)

    class_chunks = [c for c in chunks if c.kind == "class"]
    prop_chunks = [c for c in chunks if c.kind == "property"]

    class_child_map = _children_map(class_chunks)
    prop_child_map = _children_map(prop_chunks)

    selected_class_names = _closure_from_seeds(CLASS_SEEDS, class_child_map)
    selected_prop_names = _closure_from_seeds(PROPERTY_SEEDS, prop_child_map)

    selected: List[OntologyChunk] = []

    for name in selected_class_names:
        chunk = by_name.get(name)
        if chunk is not None and chunk.kind == "class":
            selected.append(chunk)

    for name in selected_prop_names:
        chunk = by_name.get(name)
        if chunk is not None and chunk.kind == "property":
            selected.append(chunk)

    return selected


def format_tbox_context(
    ontology_path: str = DEFAULT_T_OP_PATH,
) -> str:
    chunks = retrieve_validator_guided_tbox_chunks(ontology_path=ontology_path)

    if not chunks:
        return "Retrieved TBox context from T_op:\n- no relevant chunks found"

    lines = ["Retrieved TBox context from T_op:"]
    for idx, chunk in enumerate(chunks, start=1):
        lines.append(f"\n[TBOX CHUNK {idx}]")
        lines.append(chunk.text)

    return "\n".join(lines)
