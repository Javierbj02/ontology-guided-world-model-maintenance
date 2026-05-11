import os
from validator.runtime import ExperimentConfig, Step, run_experiment
from scenarios.common_delivery_prefix import build_common_prefix, build_observed_loss_step

file_name = os.path.splitext(os.path.basename(__file__))[0]

cfg_v3 = ExperimentConfig(
    ontology_path="data/ontologies/T_op.owl",
    steps=build_common_prefix() + [build_observed_loss_step()],
    enable_reasoner=False,
)
cfg_v3.scenario_id = "case_v3_unsupported_loss"

if __name__ == "__main__":
    run_experiment(cfg_v3)
