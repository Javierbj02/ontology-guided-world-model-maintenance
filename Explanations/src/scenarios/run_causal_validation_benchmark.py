import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scenarios.case_v1 import cfg_v1
from scenarios.case_v2 import cfg_v2
from scenarios.case_v3 import cfg_v3
from scenarios.case_v4 import cfg_v4
from scenarios.case_v5 import cfg_v5
from scenarios.case_v6 import cfg_v6
from validator.runtime import run_experiment
from project_paths import resolve_project_path

CASES = [
    {
        "case_id": "V1",
        "scenario": "case_v1_supported_loss",
        "description": "Supported medicine loss with correct prior taking event",
        "expected": "explained",
        "cfg": cfg_v1,
    },
    {
        "case_id": "V2",
        "scenario": "case_v2_supported_with_distractor",
        "description": "Supported medicine loss with distractor event and correct prior taking event",
        "expected": "explained",
        "cfg": cfg_v2,
    },
    {
        "case_id": "V3",
        "scenario": "case_v3_unsupported_loss",
        "description": "Observed medicine loss without any supporting prior event",
        "expected": "unexplained",
        "cfg": cfg_v3,
    },
    {
        "case_id": "V4",
        "scenario": "case_v4_wrong_participant",
        "description": "Prior event exists but involves a different object",
        "expected": "unexplained",
        "cfg": cfg_v4,
    },
    {
        "case_id": "V5",
        "scenario": "case_v5_wrong_location",
        "description": "Prior event involves the medicine but in an incompatible location",
        "expected": "unexplained",
        "cfg": cfg_v5,
    },
    {
        "case_id": "V6",
        "scenario": "case_v6_missing_operational_typing",
        "description": "Prior event involves the medicine but lacks operational typing/task anchoring",
        "expected": "unexplained",
        "cfg": cfg_v6,
    },
]

def extract_step_total(timing):
    vals = [dt for label, dt in timing if label.endswith(":step_total")]
    return round(sum(vals), 4) if vals else None

def main():
    rows = []

    for case in CASES:
        result = run_experiment(case["cfg"])

        actual = result["status"]
        passed = actual == case["expected"]

        if result["explanations"]:
            selected_event = result["explanations"][0].event_name
        else:
            selected_event = "-"

        if result["errors"]:
            failure = " | ".join(result["errors"])
        else:
            failure = "-"

        rows.append({
            "Case": case["case_id"],
            "Scenario": case["scenario"],
            "Description": case["description"],
            "Expected": case["expected"],
            "Actual": actual,
            "Pass": "yes" if passed else "no",
            "Selected event": selected_event,
            "Failure reason": failure,
            "Runtime (s)": extract_step_total(result["timing"]),
        })

    out_dir = resolve_project_path("results")
    out_dir.mkdir(exist_ok=True)

    csv_path = out_dir / "causal_validation_benchmark.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = out_dir / "causal_validation_benchmark.md"
    with md_path.open("w", encoding="utf-8") as f:
        headers = list(rows[0].keys())
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(row[h]) for h in headers) + " |\n")

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {md_path}")

if __name__ == "__main__":
    main()
