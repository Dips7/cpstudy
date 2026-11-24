"""Run 20-seed paired comparisons across policies in parallel."""
import concurrent.futures
import csv
import json
import math
import shutil
from pathlib import Path
import numpy as np
from scipy import stats

from cpstudy.closed_loop import ClosedLoop
from cpstudy.config import validate

POLICIES = ["fixed", "radio", "joint", "calibrated"]

def run_single(scenario, sources, verify_ms, policy, seed, out_dir):
    q_high = 16 if policy == "calibrated" else 8
    q_low = 6 if policy == "calibrated" else 2
    cfg_dict = {
        "scenario": scenario,
        "sources": sources,
        "verify_ms": verify_ms,
        "policy": policy,
        "queue_high": q_high,
        "queue_low": q_low,
        "duration_s": 5.0,
        "warmup_s": 1.0,
        "output": str(out_dir)
    }
    cfg = validate(cfg_dict)
    run_dir = out_dir / f"{policy}_s{seed}"
    if (run_dir / "summary.json").exists():
        try:
            return json.loads((run_dir / "summary.json").read_text())
        except Exception:
            pass
    if run_dir.exists():
        shutil.rmtree(run_dir, ignore_errors=True)
    cl = ClosedLoop(cfg, seed)
    cl.run_radio(run_dir)
    cl.run()
    s = cl.summary()
    (run_dir / "summary.json").write_text(json.dumps(s, indent=2))
    return s

def run_paired_campaign(scenario="intersection", sources=48, verify_ms=3.0, num_seeds=20, max_workers=4):
    out_dir = Path(f"results/raw/paired_{scenario}_n{sources}_v{int(verify_ms*10)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    tasks = []
    for seed in range(1, num_seeds + 1):
        for pol in POLICIES:
            tasks.append((scenario, sources, verify_ms, pol, seed, out_dir))
            
    print(f"Launching {len(tasks)} paired simulation tasks across {max_workers} workers...")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(run_single, sc, so, vm, pol, s, od): (pol, s)
            for sc, so, vm, pol, s, od in tasks
        }
        for future in concurrent.futures.as_completed(future_map):
            pol, s = future_map[future]
            try:
                res = future.result()
                results.setdefault(pol, {})[s] = res
            except Exception as e:
                print(f"Failed {pol} seed {s}: {e}")
                raise e

    # Paired Statistical Analysis
    analysis = []
    for pol in POLICIES:
        succs = [results[pol][s].get("opportunity_success_rate", 0.0) for s in range(1, num_seeds + 1)]
        lats = [results[pol][s].get("mean_success_latency_ms") or 0.0 for s in range(1, num_seeds + 1)]
        supps = [results[pol][s].get("terminal_counts", {}).get("suppressed", 0) for s in range(1, num_seeds + 1)]
        q_drops = [results[pol][s].get("terminal_counts", {}).get("queue_overflow", 0) for s in range(1, num_seeds + 1)]
        
        n = len(succs)
        mean_succ = np.mean(succs)
        std_succ = np.std(succs, ddof=1)
        ci95_succ = stats.t.ppf(0.975, n - 1) * (std_succ / np.sqrt(n))
        
        analysis.append({
            "policy": pol,
            "n_seeds": n,
            "mean_success": float(mean_succ),
            "std_success": float(std_succ),
            "ci95_success": float(ci95_succ),
            "mean_latency": float(np.mean(lats)),
            "std_latency": float(np.std(lats, ddof=1)),
            "mean_suppressed": float(np.mean(supps)),
            "mean_q_drops": float(np.mean(q_drops))
        })
        
    # Paired comparisons against fixed and calibrated
    paired_tests = []
    for p1, p2 in [("calibrated", "fixed"), ("calibrated", "radio"), ("calibrated", "joint"), ("fixed", "joint")]:
        d_succ = [results[p1][s].get("opportunity_success_rate", 0.0) - results[p2][s].get("opportunity_success_rate", 0.0)
                  for s in range(1, num_seeds + 1)]
        d_lat = [(results[p1][s].get("mean_success_latency_ms") or 0.0) - (results[p2][s].get("mean_success_latency_ms") or 0.0)
                 for s in range(1, num_seeds + 1)]
        
        mean_d = np.mean(d_succ)
        std_d = np.std(d_succ, ddof=1)
        t_stat, p_val_t = stats.ttest_rel(
            [results[p1][s].get("opportunity_success_rate", 0.0) for s in range(1, num_seeds + 1)],
            [results[p2][s].get("opportunity_success_rate", 0.0) for s in range(1, num_seeds + 1)]
        )
        try:
            w_stat, p_val_w = stats.wilcoxon(d_succ)
        except Exception:
            w_stat, p_val_w = np.nan, np.nan
            
        ci95_d = stats.t.ppf(0.975, num_seeds - 1) * (std_d / np.sqrt(num_seeds))
        paired_tests.append({
            "comparison": f"{p1}_minus_{p2}",
            "mean_delta_succ": float(mean_d),
            "ci95_delta_succ": float(ci95_d),
            "t_statistic": float(t_stat),
            "p_value_t": float(p_val_t),
            "wilcoxon_stat": float(w_stat) if not np.isnan(w_stat) else None,
            "wilcoxon_p": float(p_val_w) if not np.isnan(p_val_w) else None,
            "mean_delta_latency": float(np.mean(d_lat))
        })

    summary_file = out_dir / "paired_summary.json"
    summary_file.write_text(json.dumps({
        "scenario": scenario,
        "sources": sources,
        "verify_ms": verify_ms,
        "num_seeds": num_seeds,
        "policy_metrics": analysis,
        "paired_tests": paired_tests
    }, indent=2))
    print(f"Paired 20-seed analysis saved to {summary_file}")
    return summary_file

if __name__ == "__main__":
    run_paired_campaign(scenario="intersection", sources=48, verify_ms=3.0, num_seeds=20, max_workers=4)
