from validator.runtime import ExperimentConfig, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step


cfg_cg1 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [
        build_observed_loss_step(),
    ],
    enable_reasoner=False,
    strict_object_loss_mode=True,
)
cfg_cg1.scenario_id = "CG1_base_loss_clean"


if __name__ == "__main__":
    run_experiment(cfg_cg1)