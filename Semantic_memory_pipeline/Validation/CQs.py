from pathlib import Path

from owlready2 import *
from rdflib import Graph

VALIDATION_DIR = Path(__file__).resolve().parent
ontology_file = (VALIDATION_DIR / "data" / "T_op_instantiated.owl").resolve()
onto = get_ontology("file://" + ontology_file.as_posix()).load()
g = default_world.as_rdflib_graph()

g.bind("dul", "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
g.bind("ocra", "http://www.iri.upc.edu/groups/perception/OCRA/ont/ocra.owl#")
g.bind("soma", "http://www.ease-crc.org/ont/SOMA.owl#")

def run_sparql(name, sparql):
    print("\n" + "-" * 60)
    print(name)
    results = list(g.query(sparql))
    if not results:
        print("(no results)")
    else:
        for row in results:
            print(tuple(row))

cq1 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT DISTINCT ?goal WHERE {
  ?goal a dul:Goal .
}
ORDER BY ?goal
"""
run_sparql("CQ1 - What is the operational goal pursued in the current hospital-assistance episode?", cq1)

cq2 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT DISTINCT ?plan WHERE {
  ?goal a dul:Goal .
  ?plan a dul:Plan ;
        dul:hasComponent ?goal .
}
ORDER BY ?plan
"""
run_sparql("CQ2 - Which plan is used to achieve that goal?", cq2)

cq3 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT DISTINCT ?agent ?location WHERE {
  ?agent a dul:Agent ;
         dul:hasLocation ?location .
}
ORDER BY ?agent ?location
"""
run_sparql("CQ3 - Which agents participate in the episode, and where are they currently located?", cq3)

cq4 = """
PREFIX ocra: <http://www.iri.upc.edu/groups/perception/OCRA/ont/ocra.owl#>
PREFIX dul:  <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT DISTINCT ?collab ?agent WHERE {
  ?collab a ocra:Collaboration ;
          dul:hasParticipant ?agent .
  ?agent a dul:Agent .
}
ORDER BY ?collab ?agent
"""
run_sparql("CQ4 - Which collaboration is currently active, and which agents take part in it?", cq4)

cq5 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT DISTINCT ?object ?placeOrHolder WHERE {
  ?object a dul:PhysicalObject ;
          dul:hasLocation ?placeOrHolder .
}
ORDER BY ?object ?placeOrHolder
"""
run_sparql("CQ5 - Which task-relevant physical object is currently present, and where is it situated?", cq5)
