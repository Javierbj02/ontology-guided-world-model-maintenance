from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from rdflib import Graph, RDF, RDFS, OWL, URIRef

from project_paths import resolve_project_path

@dataclass(frozen=True)
class OntologyChunk:
    chunk_id: str
    source_ontology: str
    kind: str  # "class" | "property"
    iri: str
    local_name: str
    label: Optional[str]
    parents: List[str]
    domains: List[str]
    ranges: List[str]
    text: str


def _local_name(uri: URIRef) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    return text.rsplit("/", 1)[-1]


def _first_literal(graph: Graph, subj: URIRef, pred: URIRef) -> Optional[str]:
    for obj in graph.objects(subj, pred):
        return str(obj).strip()
    return None


def _all_uri_locals(graph: Graph, subj: URIRef, pred: URIRef) -> List[str]:
    vals: List[str] = []
    for obj in graph.objects(subj, pred):
        if isinstance(obj, URIRef):
            vals.append(_local_name(obj))
    return sorted(set(vals))


def _is_named_resource(node) -> bool:
    return isinstance(node, URIRef)


def _iter_named_classes(graph: Graph) -> Iterable[URIRef]:
    class_types = {OWL.Class, RDFS.Class}
    seen: Set[URIRef] = set()

    for class_type in class_types:
        for subj in graph.subjects(RDF.type, class_type):
            if _is_named_resource(subj) and subj not in seen:
                seen.add(subj)
                yield subj


def _iter_named_properties(graph: Graph) -> Iterable[URIRef]:
    prop_types = {
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
    }
    seen: Set[URIRef] = set()

    for prop_type in prop_types:
        for subj in graph.subjects(RDF.type, prop_type):
            if _is_named_resource(subj) and subj not in seen:
                seen.add(subj)
                yield subj


def _make_class_chunk(graph: Graph, subj: URIRef, source_ontology: str) -> OntologyChunk:
    local = _local_name(subj)
    label = _first_literal(graph, subj, RDFS.label)
    parents = _all_uri_locals(graph, subj, RDFS.subClassOf)

    lines = [f"[CLASS] {local}"]
    if label:
        lines.append(f"label: {label}")
    if parents:
        lines.append(f"parents: {', '.join(parents)}")

    text = "\n".join(lines)

    return OntologyChunk(
        chunk_id=f"class::{local}",
        source_ontology=source_ontology,
        kind="class",
        iri=str(subj),
        local_name=local,
        label=label,
        parents=parents,
        domains=[],
        ranges=[],
        text=text,
    )


def _make_property_chunk(graph: Graph, subj: URIRef, source_ontology: str) -> OntologyChunk:
    local = _local_name(subj)
    label = _first_literal(graph, subj, RDFS.label)
    parents = _all_uri_locals(graph, subj, RDFS.subPropertyOf)
    domains = _all_uri_locals(graph, subj, RDFS.domain)
    ranges = _all_uri_locals(graph, subj, RDFS.range)

    lines = [f"[PROPERTY] {local}"]
    if label:
        lines.append(f"label: {label}")
    if parents:
        lines.append(f"parents: {', '.join(parents)}")
    if domains:
        lines.append(f"domains: {', '.join(domains)}")
    if ranges:
        lines.append(f"ranges: {', '.join(ranges)}")

    text = "\n".join(lines)

    return OntologyChunk(
        chunk_id=f"property::{local}",
        source_ontology=source_ontology,
        kind="property",
        iri=str(subj),
        local_name=local,
        label=label,
        parents=parents,
        domains=domains,
        ranges=ranges,
        text=text,
    )


def build_ontology_chunks(ontology_path: str | Path) -> List[OntologyChunk]:
    path = resolve_project_path(ontology_path)
    if not path.exists():
        raise FileNotFoundError(f"Ontology file not found: {path}")

    graph = Graph()
    graph.parse(path)

    chunks: List[OntologyChunk] = []
    source_name = path.name

    for subj in _iter_named_classes(graph):
        chunks.append(_make_class_chunk(graph, subj, source_name))

    for subj in _iter_named_properties(graph):
        chunks.append(_make_property_chunk(graph, subj, source_name))

    chunks.sort(key=lambda c: (c.kind, c.local_name.lower()))
    return chunks


def save_ontology_chunks_jsonl(chunks: List[OntologyChunk], output_path: str | Path) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def load_ontology_chunks_jsonl(path: str | Path) -> List[OntologyChunk]:
    in_path = Path(path)
    chunks: List[OntologyChunk] = []

    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data: Dict[str, object] = json.loads(line)
            chunks.append(OntologyChunk(**data))

    return chunks
