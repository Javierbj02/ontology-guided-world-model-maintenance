import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v2 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix(
        extra_types=[
            ("Task_AdjustTray", "SOMA.Task"),
        ],
        ) + [
        Step(
            name="Adjust_tray",
            types=[("Action_AdjustTray", "DUL.Action")],
            asserts=[
                ("Action_AdjustTray", "DUL.hasParticipant", "Agent_Shadow"),
                ("Action_AdjustTray", "DUL.hasParticipant", "PhysicalObject_ShadowTray"),
                ("Action_AdjustTray", "DUL.executesTask", "Task_AdjustTray"),
            ],
        ),

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
        
        Step(
            name="Observed_loss_of_medicine",
            types=[],
            asserts=[],
            retracts=[
                ("PhysicalObject_Medicine1", "DUL.hasLocation", "PhysicalObject_ShadowTray"),
            ],
            updates=[],
        ),
    ],
    enable_reasoner=False,
)
cfg_v2.scenario_id = "case_v2_supported_with_distractor"

if __name__ == "__main__":
    run_experiment(cfg_v2)
