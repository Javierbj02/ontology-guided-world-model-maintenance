from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(f"JSONL file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _deduplicate_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Keep only the latest row for each (case_id, condition, run_index).
    This removes stale rows left in suite_summary.jsonl from previous executions.
    """
    latest: Dict[tuple, Dict[str, Any]] = {}

    for row in rows:
        key = (row["case_id"], row["condition"], row["run_index"])
        latest[key] = row

    dedup_rows = list(latest.values())
    dedup_rows.sort(key=lambda r: (r["case_id"], r["condition"], r["run_index"]))
    return dedup_rows


def _safe_mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(mean(values))


def aggregate_by_condition(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)

    out: List[Dict[str, Any]] = []
    for condition, items in sorted(groups.items()):
        out.append(
            {
                "condition": condition,
                "n_runs": len(items),
                "schema_valid_rate": _safe_mean(
                    [1.0 if item.get("schema_valid") else 0.0 for item in items]
                ),
                "any_strict_pass_rate": _safe_mean(
                    [1.0 if item.get("any_strict_pass") else 0.0 for item in items]
                ),
                "avg_candidate_count": _safe_mean(
                    [float(item.get("candidate_count", 0)) for item in items]
                ),
                "avg_existing_anchor_rate": _safe_mean(
                    [float(item.get("average_existing_anchor_rate", 0.0)) for item in items]
                ),
                "avg_novel_schema_rate": _safe_mean(
                    [float(item.get("average_novel_schema_rate", 0.0)) for item in items]
                ),
                "avg_grounding_rate": _safe_mean(
                    [float(item.get("average_grounding_rate", 0.0)) for item in items]
                ),
                "avg_hallucination_rate": _safe_mean(
                    [float(item.get("average_hallucination_rate", 0.0)) for item in items]
                ),
                "avg_api_latency_s": _safe_mean(
                    [float(item.get("api_latency_s", 0.0)) for item in items]
                ),
                "avg_input_tokens": _safe_mean(
                    [float(item.get("input_tokens", 0.0)) for item in items]
                ),
                "avg_output_tokens": _safe_mean(
                    [float(item.get("output_tokens", 0.0)) for item in items]
                ),
                "avg_total_tokens": _safe_mean(
                    [float(item.get("total_tokens", 0.0)) for item in items]
                ),
            }
        )

    return out


def aggregate_by_case_and_condition(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["case_id"], row["condition"])
        groups[key].append(row)

    out: List[Dict[str, Any]] = []
    for (case_id, condition), items in sorted(groups.items()):
        out.append(
            {
                "case_id": case_id,
                "condition": condition,
                "n_runs": len(items),
                "schema_valid_rate": _safe_mean(
                    [1.0 if item.get("schema_valid") else 0.0 for item in items]
                ),
                "any_strict_pass_rate": _safe_mean(
                    [1.0 if item.get("any_strict_pass") else 0.0 for item in items]
                ),
                "avg_existing_anchor_rate": _safe_mean(
                    [float(item.get("average_existing_anchor_rate", 0.0)) for item in items]
                ),
                "avg_novel_schema_rate": _safe_mean(
                    [float(item.get("average_novel_schema_rate", 0.0)) for item in items]
                ),
                "avg_grounding_rate": _safe_mean(
                    [float(item.get("average_grounding_rate", 0.0)) for item in items]
                ),
                "avg_hallucination_rate": _safe_mean(
                    [float(item.get("average_hallucination_rate", 0.0)) for item in items]
                ),
                "avg_api_latency_s": _safe_mean(
                    [float(item.get("api_latency_s", 0.0)) for item in items]
                ),
                "avg_total_tokens": _safe_mean(
                    [float(item.get("total_tokens", 0.0)) for item in items]
                ),
            }
        )

    return out


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def save_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate generation suite results.")
    parser.add_argument(
        "--summary-path",
        default="outputs/generation_suite/suite_summary.jsonl",
        help="Path to suite_summary.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        default="results/generation_suite/aggregates",
        help="Directory to save aggregate outputs",
    )
    args = parser.parse_args()

    summary_path = _project_path(args.summary_path)
    output_dir = _project_path(args.output_dir)

    rows_raw = _read_jsonl(summary_path)
    rows = _deduplicate_rows(rows_raw)

    by_condition = aggregate_by_condition(rows)
    by_case_condition = aggregate_by_case_and_condition(rows)

    save_json(output_dir / "by_condition.json", by_condition)
    save_jsonl(output_dir / "by_condition.jsonl", by_condition)

    save_json(output_dir / "by_case_condition.json", by_case_condition)
    save_jsonl(output_dir / "by_case_condition.jsonl", by_case_condition)

    print("=" * 80)
    print("AGGREGATION FINISHED")
    print("=" * 80)
    print(f"input: {summary_path}")
    print(f"output dir: {output_dir}")
    print(f"rows read (raw):   {len(rows_raw)}")
    print(f"rows kept (dedup): {len(rows)}")
    print("-" * 80)
    print("By condition:")
    for row in by_condition:
        print(row)
    print("=" * 80)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
