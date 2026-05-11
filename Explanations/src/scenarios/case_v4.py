import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v4 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix(
        extra_types=[
            ("Task_TakeClipboard", "SOMA.Task"),
            ("PhysicalObject_Clipboard1", "DUL.PhysicalObject"),            
        ],
        extra_asserts=[
            ("PhysicalObject_Clipboard1", "DUL.hasLocation", "PhysicalPlace_Hall"),
        ],
        ) + [
        Step(
            name="Take_clipboard",
            types=[("Action_TakeClipboard", "DUL.Action")],
            asserts=[
                ("Action_TakeClipboard", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_TakeClipboard", "DUL.hasParticipant", "Agent_Shadow"),
                ("Action_TakeClipboard", "DUL.hasParticipant", "PhysicalObject_Clipboard1"),
                ("Action_TakeClipboard", "DUL.executesTask", "Task_TakeClipboard"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
)
cfg_v4.scenario_id = "case_v4_wrong_participant"

if __name__ == "__main__":
    run_experiment(cfg_v4)
