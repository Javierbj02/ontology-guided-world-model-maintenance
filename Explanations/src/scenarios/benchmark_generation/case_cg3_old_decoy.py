from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step


cfg_cg3 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        Step(
            name="Old_Take_Decoy",
            types=[("Action_OldTake", "DUL.Action")],
            asserts=[
                ("Action_OldTake", "DUL.hasParticipant", "Agent_Nurse"),
                ("Action_OldTake", "DUL.hasParticipant", "PhysicalObject_Medicine1"),
                ("Action_OldTake", "DUL.executesTask", "Task_TakeMedicine"),
            ],
        ),
        Step(name="Padding_1"),
        Step(name="Padding_2"),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
    strict_object_loss_mode=True,
)
cfg_cg3.scenario_id = "CG3_old_decoy"


if __name__ == "__main__":
    run_experiment(cfg_cg3)