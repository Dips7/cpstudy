"""Audit per-receiver arrival rates, utilization, and trigger attribution across conditions."""
import gzip
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

def run_receiver_utilization_audit():
    raw_dir = Path("cpstudy/results/raw/major_revision")
    v_list = [1.0, 3.0, 6.0, 7.5, 10.0]
    audit_data = {}

    for v in v_list:
        v_runs = list(raw_dir.glob(f"stress_v{int(v*10)}_fixed_s*"))
        if not v_runs:
            continue
        
        all_rates = []
        all_rhos = []
        all_drops = []
        nodes_over_1_list = []

        for run in v_runs:
            ev_file = run / "network-events.csv.gz"
            if not ev_file.exists():
                continue
            receptions = defaultdict(int)
            drops = defaultdict(int)
            with gzip.open(ev_file, "rt") as f:
                r = csv.DictReader(f)
                for row in r:
                    if row["event_type"] == "reception" and row["kind"] == "0":
                        receptions[int(row["receiver_id"])] += 1
                    elif row["event_type"] == "terminal" and row["reason"] == "queue_overflow":
                        drops[int(row["receiver_id"])] += 1
            
            # Active evaluation window is 4.0s (5s duration - 1s warmup)
            rates = [cnt / 4.0 for cnt in receptions.values()]
            rhos = [rate * (v / 1000.0) for rate in rates]
            all_rates.extend(rates)
            all_rhos.extend(rhos)
            all_drops.append(sum(drops.values()))
            nodes_over_1_list.append(sum(1 for rho in rhos if rho > 1.0))

        audit_data[str(v)] = {
            "verify_ms": v,
            "rate_min": float(np.min(all_rates)),
            "rate_mean": float(np.mean(all_rates)),
            "rate_median": float(np.median(all_rates)),
            "rate_max": float(np.max(all_rates)),
            "rho_min": float(np.min(all_rhos)),
            "rho_mean": float(np.mean(all_rhos)),
            "rho_median": float(np.median(all_rhos)),
            "rho_max": float(np.max(all_rhos)),
            "mean_nodes_over_1": float(np.mean(nodes_over_1_list)),
            "mean_drops": float(np.mean(all_drops))
        }

    out_file = Path("cpstudy/results/raw/major_revision/utilization_audit.json")
    out_file.write_text(json.dumps(audit_data, indent=2))
    print(f"Saved utilization audit to {out_file}")
    return audit_data

def run_trigger_attribution():
    raw_dir = Path("cpstudy/results/raw/major_revision")
    policies = ["joint", "calibrated"]
    attr_summary = {}

    for pol in policies:
        runs = list(raw_dir.glob(f"stress_v30_{pol}_s*"))
        total_decisions = 0
        total_decreases = 0
        total_increases = 0
        total_holds = 0
        reasons = defaultdict(int)

        for run in runs:
            ctrl_file = run / "network-controls.csv.gz"
            if not ctrl_file.exists():
                continue
            prev_rates = {}
            with gzip.open(ctrl_file, "rt") as f:
                r = csv.DictReader(f)
                for row in r:
                    node = int(row["node_id"])
                    rate = float(row["rate_hz"])
                    busy = float(row["busy_fraction"])
                    backlog = float(row["remote_backlog"])
                    stale = int(row["feedback_stale"]) == 1
                    observed = int(row["observed_neighbors"])
                    
                    prev = prev_rates.get(node, 10.0)
                    prev_rates[node] = rate
                    total_decisions += 1

                    cbr_high = busy > 0.65
                    if pol == "joint":
                        q_cond = stale or (backlog > 8)
                    else:
                        q_cond = (observed > 0) and (backlog > 16)

                    if rate < prev:
                        total_decreases += 1
                        if cbr_high and q_cond:
                            reasons["both_cbr_and_backlog"] += 1
                        elif cbr_high:
                            reasons["cbr_only"] += 1
                        elif q_cond:
                            if stale and pol == "joint":
                                reasons["stale_only"] += 1
                            else:
                                reasons["backlog_only"] += 1
                        else:
                            reasons["other"] += 1
                    elif rate > prev:
                        total_increases += 1
                    else:
                        total_holds += 1

        attr_summary[pol] = {
            "total_decisions": total_decisions,
            "total_decreases": total_decreases,
            "total_increases": total_increases,
            "total_holds": total_holds,
            "reasons": dict(reasons),
            "pct_backlog_only": (reasons["backlog_only"] / total_decreases * 100) if total_decreases > 0 else 0,
            "pct_both": (reasons["both_cbr_and_backlog"] / total_decreases * 100) if total_decreases > 0 else 0,
            "pct_cbr_only": (reasons["cbr_only"] / total_decreases * 100) if total_decreases > 0 else 0,
        }

    out_file = Path("cpstudy/results/raw/major_revision/trigger_attribution.json")
    out_file.write_text(json.dumps(attr_summary, indent=2))
    print(f"Saved trigger attribution to {out_file}")
    return attr_summary

if __name__ == "__main__":
    run_receiver_utilization_audit()
    run_trigger_attribution()
