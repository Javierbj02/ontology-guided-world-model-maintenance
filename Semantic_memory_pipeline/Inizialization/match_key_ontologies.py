import json
from pathlib import Path
from difflib import SequenceMatcher

from scenario_builder import ScenarioBuilder
from ontology_utils import load_ontology, initialize_ontology, relate_term_to_ontology, search_lov, search_ols, search_wikidata


def text_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()

def main():
    pipeline_root = Path(__file__).resolve().parents[1]
    owl_paths = [
        pipeline_root / "data" / "ocra.owl.xml",
        pipeline_root / "data" / "SOMA.owl.rdf",
    ]
    
    ontologies = []
    for path in owl_paths:
        initialize_ontology(path)
        ontologies.append(load_ontology(path))

    builder = ScenarioBuilder()
    input_terms = ['achieve', 'collaborate', 'deliver', 'destination', 'follow', 'goal', 'hospital', 'human', 'location', 'medicine', 'nurse', 'place', 'robot', 'supervisor', 'take', 'object']

    for term in input_terms:
            builder.add_term(term)
            
            found_locally = False
            for ontology in ontologies:
                matches = relate_term_to_ontology(term, ontology, False)
                if matches:
                    found_locally = True
                    for match in matches:
                        builder.add_relation(term, match)
            
            if not found_locally:
                suggestionsA = search_lov(term)
                suggestionsB = search_ols(term)
                suggestionsC = search_wikidata(term)            
                
                suggestions = suggestionsA + suggestionsB + suggestionsC
                
                for suggest in suggestions:
                    builder.add_relation(term, suggest)
                
    res = json.loads(json.dumps(builder.export(), indent=2))

    for term in input_terms:
        print(f'\n\n Term: {term} \n\n')
        for relation in res["relations"][term]:
            term_label_sim = text_similarity(term, relation.get("label", ""))
            term_desc_sim = text_similarity(term, relation.get("description", ""))
            relation["similarity_embedding"] = max(term_label_sim, term_desc_sim)
            print(relation)
            print(f'\n')
        print(f'\n\n ----------- \n\n')
            
    print(res)            
    

if __name__ == "__main__":
    main()
