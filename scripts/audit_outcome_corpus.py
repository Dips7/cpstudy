"""Audit terminal conservation for saved factorial, paired, and stress runs.

Run from the project directory:
python scripts/audit_outcome_corpus.py --output evidence/outcome_audit.json
This script reads preserved traces only. It never repairs or overwrites run data.
"""
import argparse
import json
from pathlib import Path

from audit_outcomes import audit_run


def discover(root):
    specs = [
        ("factorial", root / "results/raw/evaluation", 6.0, 1.0, "**/summary.json"),
        ("paired20", root / "results/raw/paired_intersection_n48_v30", 5.0, 1.0,
         "*/summary.json"),
        ("major_revision", root / "results/raw/major_revision", 5.0, 1.0, "*/summary.json"),
    ]
    runs = []
    for family, base, duration, warmup, pattern in specs:
        for opportunities in base.glob(pattern):
            runs.append((family, opportunities.parent, duration, warmup))
    return sorted(runs, key=lambda item: str(item[1]))


def audit_corpus(root):
    runs = discover(Path(root))
    passed = []
    failures = []
    for family, run_dir, duration, warmup in runs:
        try:
            result = audit_run(run_dir, duration, warmup)
            comparison = result.get("summary_comparison", {})
            summary_match = (
                comparison.get("summary_generated_receiver_pairs")
                == comparison.get("recomputed_evaluated_generated_pairs")
                and comparison.get("summary_terminal_counts")
                == comparison.get("recomputed_evaluated_terminal_reasons")
            )
            record = {
                "family": family,
                "run": str(run_dir),
                "conservation_pass": all(result["conservation"].values()),
                "summary_match": summary_match,
                "evaluated_demand_pairs": result["evaluated_demand_pairs"],
                "generated_pairs_all_opportunities": result["generated_pairs_all_opportunities"],
            }
            if summary_match and record["conservation_pass"]:
                passed.append(record)
            else:
                failures.append({
                    "run": str(run_dir),
                    "issue": "conservation or summary mismatch",
                    "summary_comparison": comparison,
                    "conservation": result["conservation"],
                })
        except Exception as exc:
            failures.append({
                "run": str(run_dir),
                "issue": "raw audit error",
                "details": repr(exc),
            })

    return {
        "runs_discovered": len(runs),
        "runs_passed": len(passed),
        "runs_with_errors_or_summary_mismatch": len(failures),
        "families_passed": {
            family: sum(record["family"] == family for record in passed)
            for family in ("factorial", "paired20", "major_revision")
        },
        "passed_conservation": sum(record["conservation_pass"] for record in passed),
        "passed_summary_match": sum(record["summary_match"] for record in passed),
        "failures": failures,
        "passed_run_records": passed,
        "scope_note": (
            "Freshness coverage can credit a later update to multiple earlier demand queries; "
            "this audit checks terminal conservation for each generated pair separately."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_corpus(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("failures", "passed_run_records")}, sort_keys=True))


if __name__ == "__main__":
    main()
