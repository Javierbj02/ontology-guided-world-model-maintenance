from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List

from rdflib import Graph, OWL, RDF, RDFS, URIRef


def initialize_ontology(path: str | Path) -> Path:
    ontology_path = Path(path)
    if not ontology_path.exists():
        raise FileNotFoundError(f"Ontology file not found: {ontology_path}")
    return ontology_path


def load_ontology(path: str | Path) -> Graph:
    ontology_path = initialize_ontology(path)
    graph = Graph()
    graph.parse(ontology_path)
    return graph


def _local_name(uri: URIRef) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    return text.rsplit("/", 1)[-1]


def _label(graph: Graph, subj: URIRef) -> str:
    for label in graph.objects(subj, RDFS.label):
        return str(label)
    return _local_name(subj)


def _description(graph: Graph, subj: URIRef) -> str:
    for comment in graph.objects(subj, RDFS.comment):
        return str(comment)
    return ""


def _score(term: str, text: str) -> float:
    term_norm = term.lower()
    text_norm = text.lower()
    if not text_norm:
        return 0.0
    if term_norm in text_norm:
        return 1.0
    return SequenceMatcher(None, term_norm, text_norm).ratio()


def relate_term_to_ontology(term: str, ontology: Graph, include_descriptions: bool = True) -> List[Dict[str, Any]]:
    candidates = set()
    resource_types = {
        OWL.Class,
        RDFS.Class,
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
    }
    for resource_type in resource_types:
        candidates.update(
            subj for subj in ontology.subjects(RDF.type, resource_type)
            if isinstance(subj, URIRef)
        )

    matches: List[Dict[str, Any]] = []
    for subj in sorted(candidates, key=str):
        label = _label(ontology, subj)
        description = _description(ontology, subj) if include_descriptions else ""
        score = max(_score(term, label), _score(term, description))
        if score >= 0.72:
            matches.append(
                {
                    "iri": str(subj),
                    "label": label,
                    "description": description,
                    "similarity": round(score, 4),
                    "source": "local_ontology",
                }
            )

    return sorted(matches, key=lambda item: item["similarity"], reverse=True)


def search_lov(term: str) -> List[Dict[str, Any]]:
    return []


def search_ols(term: str) -> List[Dict[str, Any]]:
    return []


def search_wikidata(term: str) -> List[Dict[str, Any]]:
    return []
