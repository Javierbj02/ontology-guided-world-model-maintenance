from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from benchmark.cohere_client import CohereCandidateGenerator  # noqa: E402
from benchmark.pipeline import run_single_case_condition  # noqa: E402
from project_paths import resolve_project_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one candidate-generation experiment.")
    parser.add_argument("--case-id", required=True, help="Benchmark case id, e.g. CG1_base_loss_clean")
    parser.add_argument("--condition", required=True, choices=["PC1", "PC2", "PC3"])
    parser.add_argument("--run-index", type=int, default=1)
    parser.add_argument(
        "--output-dir",
        default="outputs/manual_runs",
        help="Directory where artifacts will be saved",
    )
    args = parser.parse_args()

    generator = CohereCandidateGenerator()

    result = run_single_case_condition(
        case_id=args.case_id,
        condition=args.condition,
        run_index=args.run_index,
        output_dir=resolve_project_path(args.output_dir),
        generator=generator,
    )

    print("\n=== RUN FINISHED ===")
    print(f"run_id: {result.run_id}")
    print(f"case_id: {result.case_id}")
    print(f"condition: {result.condition}")
    print(f"output_dir: {result.output_dir}")
    print("summary:")
    for k, v in result.summary_row.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
