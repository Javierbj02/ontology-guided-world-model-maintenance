from rdflib import Graph, RDF, OWL, RDFS
from pathlib import Path

g = Graph()
PIPELINE_ROOT = Path(__file__).resolve().parent
g.parse(PIPELINE_ROOT / "data" / "T_op.owl")

classes = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))
obj_props = set(g.subjects(RDF.type, OWL.ObjectProperty))
data_props = set(g.subjects(RDF.type, OWL.DatatypeProperty))

print("Classes:", len(classes))
print("Object properties:", len(obj_props))
print("Datatype properties:", len(data_props))
