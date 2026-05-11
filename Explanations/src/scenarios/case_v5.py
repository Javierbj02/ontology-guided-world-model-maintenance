import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v5 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        Step(
            name="Take_medicine_in_room101",
            types=[("Action_TakeMedicine_Room101", "DUL.Action")],
            asserts=[
                ("Action_TakeMedicine_Room101", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_TakeMedicine_Room101", "DUL.hasParticipant", "Agent_Shadow"),
                ("Action_TakeMedicine_Room101", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
                ("Action_TakeMedicine_Room101", "DUL.executesTask", "Task_TakeMedicine"),
                ("Action_TakeMedicine_Room101", "DUL.hasLocation", "PhysicalPlace_Room101"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
)
cfg_v5.scenario_id = "case_v5_wrong_location"

if __name__ == "__main__":
    run_experiment(cfg_v5)
