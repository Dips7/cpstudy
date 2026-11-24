"""Recompute offered receiver verification load from preserved raw receptions.

Run from cpstudy:
python scripts/recompute_utilization.py

Only complete fixed-policy reception traces at 1 ms are used as the common
radio-arrival baseline. Fixed senders do not observe receiver verification
feedback. Available fixed-policy traces at other service budgets are checked
for identical reception tuples before the common baseline is reused.
"""
import csv
import gzip
import json
import statistics
from pathlib import Path


ROOT = Path("results/raw/major_revision")
SEEDS = (1, 2, 3)
VERIFY_MS = (1.0, 3.0, 6.0, 7.5, 10.0)
N_RECEIVERS = 48
ACTIVE_START_NS = 1_000_000_000
ACTIVE_STOP_NS = 5_000_000_000
ACTIVE_SECONDS = (ACTIVE_STOP_NS - ACTIVE_START_NS) / 1e9


def read_data_receptions(path):
    counts = [0] * N_RECEIVERS
    tuples = []
    with gzip.open(path, "rt", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["kind"] != "0" or row["event_type"] != "reception":
                continue
            event_ns = int(row["event_ns"])
            if not ACTIVE_START_NS <= event_ns < ACTIVE_STOP_NS:
                continue
            receiver = int(row["receiver_id"])
            if not 0 <= receiver < N_RECEIVERS:
                raise ValueError(f"receiver id out of range: {receiver}")
            counts[receiver] += 1
            tuples.append((event_ns, int(row["source_id"]), receiver,
                           int(row["sequence"])))
    return counts, tuples


def main():
    baseline_counts = {}
    baseline_tuples = {}
    for seed in SEEDS:
        path = ROOT / f"stress_v10_fixed_s{seed}" / "network-events.csv.gz"
        baseline_counts[seed], baseline_tuples[seed] = read_data_receptions(path)

    trace_checks = []
    for seed in SEEDS:
        for verify_ms in VERIFY_MS:
            path = ROOT / f"stress_v{int(verify_ms * 10)}_fixed_s{seed}" / "network-events.csv.gz"
            if not path.exists():
                trace_checks.append({
                    "seed": seed, "verify_ms": verify_ms,
                    "status": "event trace unavailable; baseline reused",
                })
                continue
            _, tuples = read_data_receptions(path)
            same = tuples == baseline_tuples[seed]
            trace_checks.append({
                "seed": seed, "verify_ms": verify_ms,
                "status": "identical" if same else "different",
                "baseline_receptions": len(baseline_tuples[seed]),
                "comparison_receptions": len(tuples),
            })
            if not same:
                raise ValueError(
                    f"fixed-policy reception trace changed with verify budget "
                    f"for seed={seed}, verify_ms={verify_ms}"
                )

    rates_by_seed = {
        seed: [count / ACTIVE_SECONDS for count in baseline_counts[seed]]
        for seed in SEEDS
    }
    all_rates = [rate for rates in rates_by_seed.values() for rate in rates]
    table = []
    per_receiver = []
    for verify_ms in VERIFY_MS:
        rho_values = [rate * verify_ms / 1000 for rate in all_rates]
        over_by_seed = {
            seed: sum(rate * verify_ms / 1000 > 1.0
                      for rate in rates_by_seed[seed])
            for seed in SEEDS
        }
        table.append({
            "verify_ms": verify_ms,
            "receivers_times_seeds": len(all_rates),
            "lambda_min_packets_s": min(all_rates),
            "lambda_mean_packets_s": statistics.mean(all_rates),
            "lambda_median_packets_s": statistics.median(all_rates),
            "lambda_max_packets_s": max(all_rates),
            "rho_min_offered": min(rho_values),
            "rho_mean_offered": statistics.mean(rho_values),
            "rho_median_offered": statistics.median(rho_values),
            "rho_max_offered": max(rho_values),
            "mean_receivers_over_one_of_48": statistics.mean(over_by_seed.values()),
            "receivers_over_one_by_seed": over_by_seed,
        })
        for seed in SEEDS:
            for receiver, rate in enumerate(rates_by_seed[seed]):
                per_receiver.append({
                    "seed": seed,
                    "receiver_id": receiver,
                    "data_receptions_active_window": baseline_counts[seed][receiver],
                    "active_window_seconds": ACTIVE_SECONDS,
                    "lambda_packets_s": rate,
                    "verify_ms": verify_ms,
                    "rho_offered": rate * verify_ms / 1000,
                })

    out = Path("results/processed/rework")
    out.mkdir(parents=True, exist_ok=True)
    with (out / "utilization_by_receiver.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(per_receiver[0]))
        writer.writeheader()
        writer.writerows(per_receiver)
    report = {
        "method": (
            "Counts data receptions (kind=0) in [1 s, 5 s), divided by the "
            "4 s active interval, for all 48 receivers and seeds 1-3. Offered "
            "rho is lambda times configured mean verification service time; "
            "it is not measured worker busy fraction."
        ),
        "baseline": "stress_v10_fixed_s{seed}/network-events.csv.gz",
        "verification_budgets_ms": list(VERIFY_MS),
        "trace_comparisons": trace_checks,
        "all_reception_traces_available_match": all(
            item["status"] != "different" for item in trace_checks
        ),
        "summary": table,
    }
    (out / "utilization_recomputed.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"output": str(out), "summary": table}, sort_keys=True))


if __name__ == "__main__":
    main()
