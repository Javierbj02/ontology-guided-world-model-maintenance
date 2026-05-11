from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step


cfg_cg2 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        Step(
            name="Decoy_Take_WrongLocation",
            types=[("Action_DecoyWrongLoc", "DUL.Action")],
            asserts=[
                ("Action_DecoyWrongLoc", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_DecoyWrongLoc", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
                ("Action_DecoyWrongLoc", "DUL.executesTask", "Task_TakeMedicine"),
                ("Action_DecoyWrongLoc", "DUL.hasLocation", "PhysicalPlace_Room101"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
    strict_object_loss_mode=True,
)
cfg_cg2.scenario_id = "CG2_wrong_location_decoy"


if __name__ == "__main__":
    run_experiment(cfg_cg2)