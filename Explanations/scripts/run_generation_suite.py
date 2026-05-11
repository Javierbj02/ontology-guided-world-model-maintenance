from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from benchmark.case_context import list_active_case_ids
from benchmark.pipeline import run_single_case_condition
from project_paths import resolve_project_path


DEFAULT_CONDITIONS = ["PC1", "PC2", "PC3"]


def _iter_runs(case_ids: Iterable[str], conditions: Iterable[str], runs: int):
    for case_id in case_ids:
        for condition in conditions:
            for run_index in range(1, runs + 1):
                yield case_id, condition, run_index


def _append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the candidate-generation experiment suite over all active cases."
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=DEFAULT_CONDITIONS,
        help="Conditions to run (default: PC1 PC2 PC3)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per case/condition (default: 1)",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/generation_suite",
        help="Root output directory for the suite",
    )
    parser.add_argument(
        "--sleep-s",
        type=float,
        default=0.0,
        help="Optional sleep between API calls to reduce rate-limit pressure",
    )
    parser.add_argument(
        "--case-ids",
        nargs="*",
        default=None,
        help="Optional explicit list of case_ids. If omitted, all active cases are used.",
    )

    args = parser.parse_args()

    case_ids: List[str]
    if args.case_ids:
        case_ids = list(args.case_ids)
    else:
        case_ids = list_active_case_ids()

    conditions = list(args.conditions)
    output_root = resolve_project_path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    suite_summary_path = output_root / "suite_summary.jsonl"
    suite_errors_path = output_root / "suite_errors.jsonl"
    manifest_path = output_root / "suite_manifest.json"

    manifest = {
        "case_ids": case_ids,
        "conditions": conditions,
        "runs_per_condition": args.runs,
        "sleep_s": args.sleep_s,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    total = len(case_ids) * len(conditions) * args.runs
    completed = 0

    print("=" * 80)
    print("GENERATION SUITE")
    print("=" * 80)
    print(f"cases: {case_ids}")
    print(f"conditions: {conditions}")
    print(f"runs per condition: {args.runs}")
    print(f"output dir: {output_root}")
    print(f"total runs: {total}")
    print("=" * 80)

    for case_id, condition, run_index in _iter_runs(case_ids, conditions, args.runs):
        completed += 1
        run_dir = output_root / case_id / condition / f"run_{run_index}"

        print()
        print("-" * 80)
        print(f"[{completed}/{total}] case={case_id} | condition={condition} | run={run_index}")
        print(f"run_dir={run_dir}")
        print("-" * 80)

        try:
            artifacts = run_single_case_condition(
                case_id=case_id,
                condition=condition,
                run_index=run_index,
                output_dir=run_dir,
            )

            summary_row = dict(artifacts.summary_row)
            summary_row["run_id"] = artifacts.run_id
            summary_row["run_index"] = run_index
            summary_row["case_id"] = case_id
            summary_row["condition"] = condition
            summary_row["run_dir"] = str(run_dir)

            _append_jsonl(suite_summary_path, summary_row)

            print("OK")
            print(f"schema_valid={summary_row.get('schema_valid')}")
            print(f"any_strict_pass={summary_row.get('any_strict_pass')}")
            print(f"avg_existing_anchor={summary_row.get('average_existing_anchor_rate')}")
            print(f"avg_novel_schema={summary_row.get('average_novel_schema_rate')}")
            print(f"avg_hallucination={summary_row.get('average_hallucination_rate')}")
            print(f"api_latency_s={summary_row.get('api_latency_s')}")

        except Exception as exc:  # noqa: BLE001
            error_row = {
                "case_id": case_id,
                "condition": condition,
                "run_index": run_index,
                "error": repr(exc),
            }
            _append_jsonl(suite_errors_path, error_row)

            print("FAILED")
            print(repr(exc))

        if args.sleep_s > 0:
            time.sleep(args.sleep_s)

    print()
    print("=" * 80)
    print("SUITE FINISHED")
    print("=" * 80)
    print(f"summary: {suite_summary_path}")
    print(f"errors: {suite_errors_path}")
    print(f"manifest: {manifest_path}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
