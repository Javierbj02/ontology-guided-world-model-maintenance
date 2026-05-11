from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from benchmark.compiler import CompiledCandidate
from validator.runtime import ExperimentConfig, run_experiment


@dataclass(frozen=True)
class ValidatorProbeResult:
    scenario_id: Optional[str]
    candidate_rank: int
    candidate_event_id: str
    status: str
    failed_step: Optional[str]
    selected_support_event: Optional[str]
    errors: List[str]
    raw_result: Dict[str, Any]


def prepare_probe_config(
    base_cfg: ExperimentConfig,
    compiled_candidate: CompiledCandidate,
) -> ExperimentConfig:
    """
    Create a new ExperimentConfig by inserting the compiled candidate step
    immediately before the final step of the base scenario.

    Assumption:
    - the final step is the observed-loss step or the final validation-triggering step.
    """
    if not base_cfg.steps:
        raise ValueError("Base ExperimentConfig has no steps.")

    new_steps = deepcopy(base_cfg.steps)
    insert_index = max(len(new_steps) - 1, 0)
    new_steps.insert(insert_index, deepcopy(compiled_candidate.step))

    new_cfg = ExperimentConfig(
        ontology_path=base_cfg.ontology_path,
        steps=new_steps,
        extra_ontology_paths=deepcopy(getattr(base_cfg, "extra_ontology_paths", [])),
        enable_reasoner=getattr(base_cfg, "enable_reasoner", True),
        strict_object_loss_mode=getattr(base_cfg, "strict_object_loss_mode", False),
    )

    base_scenario_id = getattr(base_cfg, "scenario_id", "probe_base")
    new_cfg.scenario_id = f"{base_scenario_id}__probe_r{compiled_candidate.rank}"

    return new_cfg


def run_validator_probe(
    base_cfg: ExperimentConfig,
    compiled_candidate: CompiledCandidate,
) -> ValidatorProbeResult:
    """
    Prepare a probe config, run the experiment, and summarize the validator result.
    """
    probe_cfg = prepare_probe_config(base_cfg, compiled_candidate)
    raw_result = run_experiment(probe_cfg)

    selected_support_event: Optional[str] = None
    explanations = raw_result.get("explanations", []) or []
    if explanations:
        first_exp = explanations[0]
        selected_support_event = getattr(first_exp, "event_name", None)

    return ValidatorProbeResult(
        scenario_id=raw_result.get("scenario_id"),
        candidate_rank=compiled_candidate.rank,
        candidate_event_id=compiled_candidate.event_id,
        status=raw_result.get("status", "unknown"),
        failed_step=raw_result.get("failed_step"),
        selected_support_event=selected_support_event,
        errors=list(raw_result.get("errors", []) or []),
        raw_result=raw_result,
    )