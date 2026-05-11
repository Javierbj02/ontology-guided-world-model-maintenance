import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v6 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        Step(
            name="Handle_medicine",
            types=[("Action_HandleMedicine", "DUL.Action")],
            asserts=[
                ("Action_HandleMedicine", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_HandleMedicine", "DUL.hasParticipant", "Agent_Shadow"),
                ("Action_HandleMedicine", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
)
cfg_v6.scenario_id = "case_v6_missing_operational_typing"

if __name__ == "__main__":
    run_experiment(cfg_v6)
