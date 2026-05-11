from __future__ import annotations

from typing import Dict, List

from validator.runtime import ExperimentConfig

from scenarios.benchmark_generation.case_cg1_base_loss_clean import cfg_cg1
from scenarios.benchmark_generation.case_cg2_wrong_location_decoy import cfg_cg2
from scenarios.benchmark_generation.case_cg3_old_decoy import cfg_cg3
from scenarios.benchmark_generation.case_cg4_nurse_separated_clean import cfg_cg4
from scenarios.benchmark_generation.case_cg5_nurse_separated_wrong_location_decoy import cfg_cg5
from scenarios.benchmark_generation.case_cg6_nurse_separated_old_decoy import cfg_cg6


SCENARIO_REGISTRY: Dict[str, ExperimentConfig] = {
    "CG1_base_loss_clean": cfg_cg1,
    "CG2_wrong_location_decoy": cfg_cg2,
    "CG3_old_decoy": cfg_cg3,
    "CG4_nurse_separated_clean": cfg_cg4,
    "CG5_nurse_separated_wrong_location_decoy": cfg_cg5,
    "CG6_nurse_separated_old_decoy": cfg_cg6,
}


def get_case_config(case_id: str) -> ExperimentConfig:
    try:
        return SCENARIO_REGISTRY[case_id]
    except KeyError as exc:
        known = ", ".join(sorted(SCENARIO_REGISTRY.keys()))
        raise KeyError(f"Unknown benchmark case '{case_id}'. Known cases: {known}") from exc


def list_registered_case_ids() -> List[str]:
    return sorted(SCENARIO_REGISTRY.keys())