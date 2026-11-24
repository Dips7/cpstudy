"""Replay message/opportunity terminal accounting for one preserved run.

Example:
python scripts/audit_outcomes.py results/raw/.../run_dir \
  --duration-s 6 --warmup-s 1 --output /tmp/outcome-audit.json
The script reads compressed opportunity records and the normalized event stream.
ClosedLoop synthesizes terminal states for missing receptions in events.jsonl.gz;
the lower-level network-events.csv.gz contains only events observed by ns-3.
"""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path


def rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as stream:
        yield from csv.DictReader(stream)


def audit_run(run_dir, duration_s, warmup_s):
    run_dir = Path(run_dir)
    opportunity_path = run_dir / "network-opportunities.csv.gz"
    if not opportunity_path.exists():
        opportunity_path = run_dir / "network-opportunities.csv"
    if not opportunity_path.exists():
        raise FileNotFoundError(f"no opportunity trace in {run_dir}")
    opportunities = {}
    for row in rows(opportunity_path):
        required = ("source_id", "sequence", "acquisition_ns", "deadline_ns",
                    "generated", "receiver_ids")
        if any(row.get(field) is None for field in required):
            raise ValueError(f"malformed or truncated opportunity row: {row}")
        key = (int(row["source_id"]), int(row["sequence"]))
        if key in opportunities:
            raise ValueError(f"duplicate opportunity identity: {key}")
        receivers = [int(value) for value in row["receiver_ids"].split("|") if value]
        acquired = int(row["acquisition_ns"])
        deadline = int(row["deadline_ns"])
        opportunities[key] = {
            "generated": row["generated"] in ("1", "true", "True"),
            "receivers": set(receivers),
            "acquired_ns": acquired,
            "deadline_ns": deadline,
            "evaluated": round(warmup_s * 1e9) <= acquired and deadline <= round(duration_s * 1e9),
        }

    expected = set()
    demand_pairs = suppressed_pairs = 0
    evaluated_demand_pairs = evaluated_suppressed_pairs = 0
    for (source, sequence), opportunity in opportunities.items():
        n_receivers = len(opportunity["receivers"])
        demand_pairs += n_receivers
        if opportunity["evaluated"]:
            evaluated_demand_pairs += n_receivers
        if not opportunity["generated"]:
            suppressed_pairs += n_receivers
            if opportunity["evaluated"]:
                evaluated_suppressed_pairs += n_receivers
            continue
        for receiver in opportunity["receivers"]:
            expected.add((source, sequence, receiver))

    terminals = {}
    all_terminal_reasons = Counter()
    eligible_terminal_reasons = Counter()
    received_pairs = set()
    verified_pairs = set()
    with gzip.open(run_dir / "events.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            event_type = row["event_type"]
            if event_type not in ("reception", "verification_end", "terminal"):
                continue
            source, receiver = int(row["source_id"]), int(row["receiver_id"])
            opportunity_id = row["opportunity_id"]
            if not opportunity_id:
                continue
            try:
                sequence = int(opportunity_id.split(":", 1)[1])
            except (IndexError, ValueError):
                continue
            key = (source, sequence, receiver)
            if key not in expected:
                continue
            if event_type == "reception":
                received_pairs.add(key)
            elif event_type == "verification_end":
                verified_pairs.add(key)
            elif event_type == "terminal":
                reason = row["reason"]
                all_terminal_reasons[reason] += 1
                if key in terminals:
                    raise ValueError(f"duplicate terminal event for generated pair: {key}")
                terminals[key] = reason
                if opportunities[(source, sequence)]["evaluated"]:
                    eligible_terminal_reasons[reason] += 1

    missing = sorted(expected - terminals.keys())
    unexpected = sorted(terminals.keys() - expected)
    if unexpected:
        raise ValueError(f"unexpected terminal pairs: {unexpected[:5]}")
    if missing:
        raise ValueError(f"{len(missing)} generated pairs lack a terminal; examples: {missing[:5]}")

    evaluated_generated_pairs = sum(
        len(op["receivers"]) for (source, sequence), op in opportunities.items()
        if op["generated"] and op["evaluated"]
    )
    evaluated_terminal_total = sum(eligible_terminal_reasons.values())
    if evaluated_suppressed_pairs + evaluated_generated_pairs != evaluated_demand_pairs:
        raise AssertionError("demand partition does not conserve")
    if evaluated_terminal_total != evaluated_generated_pairs:
        raise AssertionError("generated evaluated pairs do not match terminal count")

    report = {
        "run_directory": str(run_dir),
        "opportunity_count": len(opportunities),
        "demand_pairs_all_opportunities": demand_pairs,
        "generated_pairs_all_opportunities": len(expected),
        "suppressed_pairs_all_opportunities": suppressed_pairs,
        "terminal_reasons_all_generated_pairs": dict(all_terminal_reasons),
        "received_generated_pairs": len(received_pairs),
        "verified_generated_pairs": len(verified_pairs),
        "evaluated_demand_pairs": evaluated_demand_pairs,
        "evaluated_suppressed_pairs": evaluated_suppressed_pairs,
        "evaluated_generated_pairs": evaluated_generated_pairs,
        "evaluated_terminal_reasons": dict(eligible_terminal_reasons),
        "conservation": {
            "demand_equals_suppressed_plus_generated": (
                evaluated_demand_pairs == evaluated_suppressed_pairs + evaluated_generated_pairs
            ),
            "generated_equals_terminal_partition": (
                evaluated_generated_pairs == evaluated_terminal_total
            ),
            "all_generated_pairs_have_exactly_one_terminal": len(terminals) == len(expected),
        },
        "note": (
            "Freshness coverage may credit one update to multiple earlier demand queries; "
            "this terminal partition instead accounts for each generated message-receiver pair once."
        ),
    }
    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        recomputed_summary_reasons = dict(eligible_terminal_reasons)
        if evaluated_suppressed_pairs:
            recomputed_summary_reasons["suppressed"] = evaluated_suppressed_pairs
        report["summary_comparison"] = {
            "summary_generated_receiver_pairs": summary.get("generated_receiver_pairs"),
            "recomputed_evaluated_generated_pairs": evaluated_generated_pairs,
            "summary_terminal_counts": summary.get("terminal_counts"),
            "recomputed_evaluated_terminal_reasons": recomputed_summary_reasons,
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--duration-s", type=float, required=True)
    parser.add_argument("--warmup-s", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_run(args.run_directory, args.duration_s, args.warmup_s)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["conservation"], sort_keys=True))


if __name__ == "__main__":
    main()
