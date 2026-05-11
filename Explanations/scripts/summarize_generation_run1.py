from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT / "outputs" / "generation_suite"
OUT_PATH = PROJECT_ROOT / "results" / "generation_suite" / "run1_candidate_summary.md"


def infer_family(case_id: str) -> str:
    if case_id in {"CG1_base_loss_clean", "CG2_wrong_location_decoy", "CG3_old_decoy"}:
        return "co-located"
    if case_id in {
        "CG4_nurse_separated_clean",
        "CG5_nurse_separated_wrong_location_decoy",
        "CG6_nurse_separated_old_decoy",
    }:
        return "nurse-separated"
    return "unknown"


def load_raw_output(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_run1_raw_outputs(root: Path) -> List[Path]:
    return sorted(root.glob("CG*/PC*/run_1/*__raw_output.txt"))


def has_symbol(participants: List[str], symbol: str) -> bool:
    return symbol in participants


def summarize_candidate(cand: Dict[str, Any]) -> Dict[str, Any]:
    proj = cand.get("operational_projection", {}) or {}
    participants = cand.get("participants", []) or []
    location = cand.get("location")
    event_type = proj.get("event_type")

    return {
        "rank": cand.get("rank"),
        "event_type_label": cand.get("event_type_label"),
        "event_type": event_type,
        "participants": participants,
        "location": location,
        "short_rationale": cand.get("short_rationale"),
        "has_shadow": has_symbol(participants, "Agent_Shadow"),
        "has_medicine": has_symbol(participants, "PhysicalObject_Medicine1"),
        "has_tray": has_symbol(participants, "PhysicalObject_ShadowTray"),
        "has_explicit_location": location is not None,
        "novel_symbols": [
            p for p in participants
            if p not in {
                "Agent_Shadow",
                "Agent_Nurse",
                "PhysicalObject_Medicine1",
                "PhysicalObject_ShadowTray",
                "PhysicalPlace_Corridor1",
                "PhysicalPlace_Room101",
            }
        ],
    }


def main() -> int:
    paths = find_run1_raw_outputs(ROOT)

    if not paths:
        raise FileNotFoundError(f"No run_1 raw outputs found under {ROOT}")

    rows: List[Dict[str, Any]] = []

    top1_by_condition = Counter()
    top1_by_family_condition = defaultdict(Counter)

    for path in paths:
        data = load_raw_output(path)
        case_id = data["case_id"]
        condition = data["condition"]
        family = infer_family(case_id)

        candidates = [summarize_candidate(c) for c in data.get("candidates", [])]
        candidates.sort(key=lambda x: x["rank"])

        top1 = candidates[0] if candidates else None
        if top1 is not None:
            label = top1["event_type_label"] or "UNKNOWN"
            top1_by_condition[condition, label] += 1
            top1_by_family_condition[family, condition][label] += 1

        rows.append(
            {
                "case_id": case_id,
                "condition": condition,
                "family": family,
                "candidates": candidates,
                "source_path": str(path),
            }
        )

    lines: List[str] = []
    lines.append("# Candidate-generation qualitative summary (run_1)")
    lines.append("")

    lines.append("## Top-1 hypothesis frequencies by condition")
    lines.append("")
    for condition in ["PC1", "PC2", "PC3"]:
        lines.append(f"### {condition}")
        items = [
            (label, count)
            for (cond, label), count in top1_by_condition.items()
            if cond == condition
        ]
        items.sort(key=lambda x: (-x[1], x[0]))
        for label, count in items:
            lines.append(f"- {label}: {count}")
        lines.append("")

    lines.append("## Top-1 hypothesis frequencies by family and condition")
    lines.append("")
    for family in ["co-located", "nurse-separated"]:
        lines.append(f"### {family}")
        for condition in ["PC1", "PC2", "PC3"]:
            lines.append(f"- {condition}:")
            items = list(top1_by_family_condition[family, condition].items())
            items.sort(key=lambda x: (-x[1], x[0]))
            if not items:
                lines.append("  - none")
            else:
                for label, count in items:
                    lines.append(f"  - {label}: {count}")
        lines.append("")

    lines.append("## Per-case summaries")
    lines.append("")

    rows.sort(key=lambda r: (r["case_id"], r["condition"]))
    for row in rows:
        lines.append(f"### {row['case_id']} — {row['condition']} ({row['family']})")
        lines.append(f"Source: `{row['source_path']}`")
        lines.append("")
        for cand in row["candidates"]:
            lines.append(f"- Rank {cand['rank']}: {cand['event_type_label']}")
            lines.append(f"  - event_type: `{cand['event_type']}`")
            lines.append(f"  - participants: {', '.join(cand['participants']) if cand['participants'] else '∅'}")
            lines.append(f"  - location: `{cand['location']}`")
            lines.append(f"  - rationale: {cand['short_rationale']}")
            lines.append(
                "  - flags: "
                f"shadow={cand['has_shadow']}, "
                f"medicine={cand['has_medicine']}, "
                f"tray={cand['has_tray']}, "
                f"explicit_location={cand['has_explicit_location']}"
            )
            if cand["novel_symbols"]:
                lines.append(f"  - novel_symbols: {', '.join(cand['novel_symbols'])}")
        lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved summary to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
