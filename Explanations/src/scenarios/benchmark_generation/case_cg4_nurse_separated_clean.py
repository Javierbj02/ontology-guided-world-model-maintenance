from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step


cfg_cg4 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        Step(
            name="Nurse_moves_away",
            updates=[
                ("Agent_Nurse", "DUL.hasLocation", "PhysicalPlace_Corridor1", "PhysicalPlace_Room101"),
            ],
        ),
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
    strict_object_loss_mode=True,
)
cfg_cg4.scenario_id = "CG4_nurse_separated_clean"


if __name__ == "__main__":
    run_experiment(cfg_cg4)