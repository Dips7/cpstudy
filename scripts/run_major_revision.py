"""Execute the major revision statistical campaign, ablations, and stress sweep in parallel."""
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

def execute_single_run(cfg_dict, seed, run_dir):
    run_dir = Path(run_dir)
    summary_file = run_dir / "summary.json"
    if summary_file.exists():
        try:
            return json.loads(summary_file.read_text())
        except Exception:
            pass
    if run_dir.exists():
        shutil.rmtree(run_dir, ignore_errors=True)
    cfg = validate(cfg_dict)
    cl = ClosedLoop(cfg, seed)
    cl.run_radio(run_dir)
    cl.run()
    s = cl.summary()
    summary_file.write_text(json.dumps(s, indent=2))
    return s

def run_stress_sweep(out_dir, max_workers=4):
    v_list = [1.0, 3.0, 6.0, 7.5, 10.0]
    pols = ["fixed", "radio", "joint", "calibrated"]
    seeds = [1, 2, 3]
    
    tasks = []
    for v in v_list:
        for p in pols:
            for s in seeds:
                cfg_dict = {
                    "scenario": "intersection",
                    "sources": 48,
                    "verify_ms": v,
                    "policy": p,
                    "queue_high": 16 if p == "calibrated" else 8,
                    "queue_low": 6 if p == "calibrated" else 2,
                    "duration_s": 5.0,
                    "warmup_s": 1.0,
                    "output": str(out_dir / f"stress_v{int(v*10)}_{p}_s{s}")
                }
                run_dir = out_dir / f"stress_v{int(v*10)}_{p}_s{s}"
                tasks.append((v, p, s, cfg_dict, run_dir))

    print(f"Running stress sweep: {len(tasks)} runs across {max_workers} workers...")
    summaries = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        f_map = {
            executor.submit(execute_single_run, cfg, s, rd): (v, p, s)
            for v, p, s, cfg, rd in tasks
        }
        done = 0
        for f in concurrent.futures.as_completed(f_map):
            v, p, s = f_map[f]
            try:
                summaries[(v, p, s)] = f.result()
                done += 1
                if done % 10 == 0 or done == len(tasks):
                    print(f"[{done}/{len(tasks)}] Stress runs finished.")
            except Exception as e:
                print(f"Run failed {v} {p} {s}: {e}")
                raise e

    records = []
    for v in v_list:
        for p in pols:
            succs, lats, q_drops, exps, supps = [], [], [], [], []
            for s in seeds:
                summary = summaries[(v, p, s)]
                term = summary.get("terminal_counts", {})
                succs.append(summary.get("opportunity_success_rate", 0.0))
                if summary.get("mean_success_latency_ms"):
                    lats.append(summary["mean_success_latency_ms"])
                q_drops.append(term.get("queue_overflow", 0))
                exps.append(term.get("verification_expired", 0) + term.get("fusion_expired", 0))
                supps.append(term.get("suppressed", 0))
            records.append({
                "verify_ms": v,
                "policy": p,
                "mean_succ": float(np.mean(succs)),
                "std_succ": float(np.std(succs, ddof=1)) if len(succs) > 1 else 0.0,
                "mean_lat": float(np.mean(lats)) if lats else None,
                "mean_q_drop": float(np.mean(q_drops)),
                "mean_expired": float(np.mean(exps)),
                "mean_supp": float(np.mean(supps))
            })
    return records

def run_ablation_sweep(out_dir, max_workers=4):
    ablations = [
        {"name": "Q_thresh_4", "policy": "calibrated", "q_high": 4, "q_low": 2},
        {"name": "Q_thresh_8", "policy": "calibrated", "q_high": 8, "q_low": 3},
        {"name": "Q_thresh_16", "policy": "calibrated", "q_high": 16, "q_low": 6},
        {"name": "Q_thresh_24", "policy": "calibrated", "q_high": 24, "q_low": 8},
        {"name": "Uncalibrated_Joint", "policy": "joint", "q_high": 8, "q_low": 2},
        {"name": "Radio_Only", "policy": "radio", "q_high": 8, "q_low": 2},
        {"name": "Fixed_10Hz", "policy": "fixed", "q_high": 8, "q_low": 2},
    ]
    seeds = [1, 2, 3, 4, 5]
    tasks = []
    for ab in ablations:
        for s in seeds:
            cfg_dict = {
                "scenario": "intersection",
                "sources": 48,
                "verify_ms": 3.0,
                "policy": ab["policy"],
                "queue_high": ab["q_high"],
                "queue_low": ab["q_low"],
                "duration_s": 5.0,
                "warmup_s": 1.0,
                "output": str(out_dir / f"ab_{ab['name']}_s{s}")
            }
            run_dir = out_dir / f"ab_{ab['name']}_s{s}"
            tasks.append((ab["name"], ab["policy"], ab["q_high"], s, cfg_dict, run_dir))

    print(f"Running ablations: {len(tasks)} runs across {max_workers} workers...")
    summaries = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        f_map = {
            executor.submit(execute_single_run, cfg, s, rd): (name, pol, qh, s)
            for name, pol, qh, s, cfg, rd in tasks
        }
        done = 0
        for f in concurrent.futures.as_completed(f_map):
            name, pol, qh, s = f_map[f]
            summaries[(name, s)] = f.result()
            done += 1
            if done % 10 == 0 or done == len(tasks):
                print(f"[{done}/{len(tasks)}] Ablation runs finished.")

    records = []
    for ab in ablations:
        succs, lats, supps, q_drops = [], [], [], []
        for s in seeds:
            summary = summaries[(ab["name"], s)]
            term = summary.get("terminal_counts", {})
            succs.append(summary.get("opportunity_success_rate", 0.0))
            if summary.get("mean_success_latency_ms"):
                lats.append(summary["mean_success_latency_ms"])
            supps.append(term.get("suppressed", 0))
            q_drops.append(term.get("queue_overflow", 0))
        records.append({
            "ablation": ab["name"],
            "policy": ab["policy"],
            "q_high": ab["q_high"],
            "mean_succ": float(np.mean(succs)),
            "std_succ": float(np.std(succs, ddof=1)),
            "mean_lat": float(np.mean(lats)) if lats else None,
            "mean_supp": float(np.mean(supps)),
            "mean_q_drop": float(np.mean(q_drops))
        })
    return records

if __name__ == "__main__":
    out_base = Path("results/raw/major_revision")
    out_base.mkdir(parents=True, exist_ok=True)
    print("Executing Major Revision Experiments (Parallel)...")
    
    # 1. Stress sweep
    stress_res = run_stress_sweep(out_base, max_workers=4)
    (out_base / "stress_sweep.json").write_text(json.dumps(stress_res, indent=2))
    print("Stress sweep complete! Saved to stress_sweep.json")
    
    # 2. Ablations
    ablation_res = run_ablation_sweep(out_base, max_workers=4)
    (out_base / "ablations.json").write_text(json.dumps(ablation_res, indent=2))
    print("Ablations complete! Saved to ablations.json")
