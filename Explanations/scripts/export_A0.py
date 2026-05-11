import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from owlready2 import Thing, ThingClass
from validator.runtime import OntologyRuntime
from scenarios.nominal import cfg_nominal
from project_paths import resolve_project_path



TARGET_STEP = "Move_to_corridor"
OUTPUT_PATH = resolve_project_path("data/ontologies/A_0.owl")

def is_event_class(cls):
    name = getattr(cls, "name", "").lower()
    return (
        name == "action"
        or name == "event"
        or name.endswith("action")
        or name.endswith("event")
    )

def iter_values(prop, ind):
    vals = prop[ind]
    if isinstance(vals, list):
        return vals
    return [vals]

def main():
    cfg = cfg_nominal

    rt = OntologyRuntime(
        cfg.ontology_path,
        extra_paths=getattr(cfg, "extra_ontology_paths", []),
    )

    reached = False
    for step in cfg.steps:
        if step.types:
            rt.apply_types(step.types)

        rt.apply_triples(step.asserts, step.retracts, step.updates)

        if step.deletes:
            rt.delete_instances(step.deletes)

        print(f"[APPLIED] {step.name}")

        if step.name == TARGET_STEP:
            reached = True
            break

    if not reached:
        raise ValueError(f"Step '{TARGET_STEP}' not found in scenario.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rt.onto.save(file=str(OUTPUT_PATH), format="rdfxml")
    print(f"[OK] Snapshot saved to {OUTPUT_PATH}")

    individuals = list(rt.onto.individuals())
    n_individuals = len(individuals)

    n_type_assertions = 0
    n_obj_assertions = 0
    n_data_assertions = 0

    event_inds = set()
    has_goal = False
    has_plan = False
    has_collaboration = False

    event_assertions = 0

    for ind in individuals:
        real_types = [cls for cls in ind.is_a if isinstance(cls, ThingClass)]
        n_type_assertions += len(real_types)

        is_event_ind = False
        for cls in real_types:
            lname = cls.name.lower()
            if lname == "goal":
                has_goal = True
            if lname == "plan":
                has_plan = True
            if "collaboration" in lname:
                has_collaboration = True
            if is_event_class(cls):
                is_event_ind = True

        if is_event_ind:
            event_inds.add(ind)
            event_assertions += len(real_types)

        for prop in ind.get_properties():
            vals = iter_values(prop, ind)
            for v in vals:
                if isinstance(v, Thing):
                    n_obj_assertions += 1
                    if is_event_ind:
                        event_assertions += 1
                else:
                    n_data_assertions += 1
                    if is_event_ind:
                        event_assertions += 1

    n_abox_assertions = n_type_assertions + n_obj_assertions + n_data_assertions
    state_assertions = n_abox_assertions - event_assertions

    print("\n=== SNAPSHOT COUNTS ===")
    print(f"Named individuals: {n_individuals}")
    print(f"ABox assertions: {n_abox_assertions}")
    print(f"  - type assertions: {n_type_assertions}")
    print(f"  - object property assertions: {n_obj_assertions}")
    print(f"  - data property assertions: {n_data_assertions}")
    print(f"Event instances: {len(event_inds)}")
    print(f"Event-evidence assertions: {event_assertions}")
    print(f"State assertions: {state_assertions}")
    print(f"Has goal instance: {has_goal}")
    print(f"Has plan instance: {has_plan}")
    print(f"Has collaboration instance: {has_collaboration}")

if __name__ == "__main__":
    main()
