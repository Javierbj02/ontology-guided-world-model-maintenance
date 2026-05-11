import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v1 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [ 
        Step(
            name="Nurse_takes_medicine",
            types=[("Action_TakeMedicine", "DUL.Action")],
            asserts=[
                ("Action_TakeMedicine", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_TakeMedicine", "DUL.hasParticipant", "Agent_Shadow"),
                ("Action_TakeMedicine", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
                ("Action_TakeMedicine", "DUL.executesTask", "Task_TakeMedicine"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
)
cfg_v1.scenario_id = "case_v1_supported_loss"

if __name__ == "__main__":
    run_experiment(cfg_v1)
