from pathlib import Path

from benchmark.ontology_chunk_builder import build_ontology_chunks


def test_build_ontology_chunks_from_ttl(tmp_path: Path):
    ttl = """
    @prefix ex: <http://example.org/> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    ex:Event a owl:Class ;
        rdfs:comment "A generic event." .

    ex:Action a owl:Class ;
        rdfs:subClassOf ex:Event .

    ex:hasParticipant a owl:ObjectProperty ;
        rdfs:domain ex:Event ;
        rdfs:range ex:Thing .
    """
    path = tmp_path / "mini.ttl"
    path.write_text(ttl, encoding="utf-8")

    chunks = build_ontology_chunks(path)

    locals_ = {c.local_name for c in chunks}
    assert "Event" in locals_
    assert "Action" in locals_
    assert "hasParticipant" in locals_

    action_chunk = next(c for c in chunks if c.local_name == "Action")
    assert "Event" in action_chunk.parents

    prop_chunk = next(c for c in chunks if c.local_name == "hasParticipant")
    assert "Event" in prop_chunk.domains