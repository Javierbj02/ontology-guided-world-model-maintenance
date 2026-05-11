import sys
from pathlib import Path
from owlready2 import *
import types

def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <input_ontology.owl> <output_instantiated.owl>")
        sys.exit(1)

    ont_path = sys.argv[1]
    if not ont_path.startswith("file://"):
        ontology_file = Path(ont_path)
        if not ontology_file.is_absolute():
            ontology_file = Path(__file__).resolve().parent / ontology_file
        ont_path = "file://" + ontology_file.resolve().as_posix()

    output_path = Path(sys.argv[2])
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path

    onto = get_ontology(ont_path).load()
    ontology_ns = types.SimpleNamespace()

    def apply_reasoner(message=""):
        print("\n" + "-"*40)
        print(f"Running reasoner... {message}")
        sync_reasoner()
        print("Reasoner applied.")
        print("-"*40 + "\n")

    with onto:
        for cls in onto.classes():
            setattr(ontology_ns, cls.name, cls)

        Agent_Nurse = ontology_ns.Agent("Agent_Nurse")
        Agent_Shadow = ontology_ns.Agent("Agent_Shadow")
        PhysicalPlace_Hospital = ontology_ns.PhysicalPlace("PhysicalPlace_Hospital")
        PhysicalPlace_Room101 = ontology_ns.PhysicalPlace("PhysicalPlace_Room101")
        PhysicalObject_Medicine1 = ontology_ns.PhysicalObject("PhysicalObject_Medicine1")
        Goal_DeliveryAssistance = ontology_ns.Goal("Goal_DeliveryAssistance")
        Plan_DeliverMedicine = ontology_ns.Plan("Plan_DeliverMedicine")
        Collaboration_Collaborate = ontology_ns.Collaboration("Collaboration_Collaborate")

        Plan_DeliverMedicine.hasComponent.append(Goal_DeliveryAssistance)
        Agent_Shadow.hasGoal.append(Goal_DeliveryAssistance)
        Agent_Shadow.hasPlan.append(Plan_DeliverMedicine)
        Agent_Shadow.hasLocation.append(PhysicalPlace_Hospital)
        Agent_Nurse.hasGoal.append(Goal_DeliveryAssistance)
        Agent_Nurse.hasPlan.append(Plan_DeliverMedicine)
        Agent_Nurse.hasLocation.append(PhysicalPlace_Hospital)
        PhysicalPlace_Room101.isPartOf.append(PhysicalPlace_Hospital)
        PhysicalObject_Medicine1.hasLocation.append(Agent_Shadow)
        Collaboration_Collaborate.executesPlan.append(Plan_DeliverMedicine)
        Collaboration_Collaborate.hasParticipant.append(Agent_Shadow)
        Collaboration_Collaborate.hasParticipant.append(Agent_Nurse)

        apply_reasoner("Instantiation created")

    onto.save(file=str(output_path), format="rdfxml")

if __name__ == "__main__":
    main()
