"""Campaign execution, statistical analysis, and publication figure generation."""
import concurrent.futures
import csv
import gzip
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from scipy import stats
import yaml

from .config import validate, digest
from .closed_loop import ClosedLoop


def sha(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_single_job(cfg_dict, seed, output_base):
    # Ensure independent run directory
    target_dir = Path(output_base) / cfg_dict["scenario"] / f"sources{cfg_dict['sources']}_verify{int(cfg_dict['verify_ms'])}" / cfg_dict["policy"] / f"{digest(cfg_dict)[:12]}-seed{seed}"
    if (target_dir / "manifest.json").exists():
        manifest_path = target_dir / "manifest.json"
        summary = json.loads((target_dir / "summary.json").read_text())
        return dict(status="reused", manifest=str(manifest_path), summary=summary, config=cfg_dict, seed=seed)

    config_path = target_dir.parent / f"cfg_{digest(cfg_dict)[:12]}_s{seed}.yaml"
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    cfg_copy = dict(cfg_dict)
    cfg_copy["output"] = str(target_dir.parent)
    config_path.write_text(yaml.safe_dump(cfg_copy))

    cmd = [sys.executable, "-m", "cpstudy", "run", "--config", str(config_path), "--seed", str(seed)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Run failed for {cfg_dict['policy']} seed {seed}: {res.stderr}\n{res.stdout}")
    
    manifest_str = res.stdout.strip().splitlines()[-1]
    manifest_path = Path(manifest_str)
    
    # Audit
    audit_cmd = [sys.executable, "-m", "cpstudy", "audit", "--manifest", str(manifest_path)]
    audit_res = subprocess.run(audit_cmd, capture_output=True, text=True)
    if audit_res.returncode != 0:
        raise RuntimeError(f"Audit failed for manifest {manifest_path}: {audit_res.stderr}\n{audit_res.stdout}")
    
    summary = json.loads((manifest_path.parent / "summary.json").read_text())
    return dict(status="completed", manifest=str(manifest_path), summary=summary, config=cfg_dict, seed=seed)


def run_campaign(manifest_path, max_workers=4):
    cfg = yaml.safe_load(Path(manifest_path).read_text())
    base = cfg["base_config"]
    matrix = cfg["matrix"]
    out_dir = Path(cfg["output"])
    out_dir.mkdir(parents=True, exist_ok=True)

    experiments = []
    for scenario in matrix["scenarios"]:
        for sources in matrix["sources"]:
            for verify_ms in matrix["verify_ms"]:
                for policy in matrix["policies"]:
                    for seed in matrix["seeds"]:
                        run_cfg = dict(base)
                        run_cfg.update({
                            "scenario": scenario,
                            "sources": sources,
                            "verify_ms": verify_ms,
                            "policy": policy,
                            "output": str(out_dir)
                        })
                        experiments.append((validate(run_cfg), seed))

    print(f"Starting evaluation campaign: {len(experiments)} total runs across {max_workers} workers.")
    t0 = time.time()
    results = []
    
    # Run in parallel using ProcessPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_single_job, c, s, out_dir): (c["scenario"], c["sources"], c["verify_ms"], c["policy"], s)
            for c, s in experiments
        }
        done_count = 0
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                res = future.result()
                results.append(res)
                done_count += 1
                if done_count % 10 == 0 or done_count == len(experiments):
                    elapsed = time.time() - t0
                    print(f"[{done_count}/{len(experiments)}] Completed in {elapsed:.1f}s - latest: {key}")
            except Exception as e:
                print(f"Error executing {key}: {e}", file=sys.stderr)
                raise e

    campaign_summary_file = out_dir / "campaign_manifest.json"
    campaign_summary_file.write_text(json.dumps({
        "manifest_path": str(manifest_path),
        "total_runs": len(results),
        "wall_seconds": time.time() - t0,
        "runs": results
    }, indent=2) + "\n")
    print(f"Campaign complete! Results saved to {campaign_summary_file}")
    return campaign_summary_file


def analyze_campaign(manifest_path):
    cfg = yaml.safe_load(Path(manifest_path).read_text())
    out_dir = Path(cfg["output"])
    proc_dir = Path("results/processed/evaluation")
    proc_dir.mkdir(parents=True, exist_ok=True)

    manifest_files = list(out_dir.glob("**/manifest.json"))
    if not manifest_files:
        raise ValueError(f"No run manifests found in {out_dir}")

    runs_data = []
    for mf in manifest_files:
        if mf.name != "manifest.json" or "campaign_manifest.json" in str(mf):
            continue
        try:
            m = json.loads(mf.read_text())
            root = mf.parent
            c = json.loads((root / "config.json").read_text())
            s = json.loads((root / "summary.json").read_text())
            terminals = s.get("terminal_counts", {})
            runs_data.append({
                "scenario": c["scenario"],
                "sources": c["sources"],
                "verify_ms": c["verify_ms"],
                "policy": c["policy"],
                "seed": m["seed"],
                "opp_success_rate": s.get("opportunity_success_rate", 0.0),
                "gen_success_rate": s.get("generated_success_rate", 0.0),
                "freshness_rate": s.get("opportunity_freshness_rate", 0.0),
                "mean_latency_ms": s.get("mean_success_latency_ms", 0.0),
                "feedback_sent": s.get("feedback_datagrams_sent", 0),
                "feedback_verified": s.get("feedback_verifications", 0),
                "term_success": terminals.get("success", 0),
                "term_radio_drop": terminals.get("radio_not_received", 0),
                "term_queue_overflow": terminals.get("queue_overflow", 0),
                "term_verify_expired": terminals.get("verification_expired", 0),
                "term_fusion_expired": terminals.get("fusion_expired", 0),
                "term_suppressed": terminals.get("suppressed", 0),
                "opportunity_pairs": s.get("opportunity_receiver_pairs", 0)
            })
        except Exception as e:
            print(f"Skipping {mf}: {e}")

    # Group by (scenario, sources, verify_ms, policy)
    groups = {}
    for r in runs_data:
        key = (r["scenario"], r["sources"], r["verify_ms"], r["policy"])
        groups.setdefault(key, []).append(r)

    rows = []
    for (scenario, sources, verify_ms, policy), items in sorted(groups.items()):
        n = len(items)
        opp_succ = [x["opp_success_rate"] for x in items]
        freshness = [x["freshness_rate"] for x in items]
        latency = [x["mean_latency_ms"] for x in items if x["mean_latency_ms"] > 0]
        radio_drops = [x["term_radio_drop"] for x in items]
        queue_overflows = [x["term_queue_overflow"] for x in items]
        suppressed = [x["term_suppressed"] for x in items]
        total_opps = [x["opportunity_pairs"] for x in items]

        mean_opp_succ = np.mean(opp_succ)
        std_opp_succ = np.std(opp_succ, ddof=1) if n > 1 else 0.0
        ci95_opp_succ = stats.t.ppf(0.975, n - 1) * (std_opp_succ / np.sqrt(n)) if n > 1 else 0.0

        mean_fresh = np.mean(freshness)
        std_fresh = np.std(freshness, ddof=1) if n > 1 else 0.0
        ci95_fresh = stats.t.ppf(0.975, n - 1) * (std_fresh / np.sqrt(n)) if n > 1 else 0.0

        mean_lat = np.mean(latency) if latency else 0.0
        std_lat = np.std(latency, ddof=1) if len(latency) > 1 else 0.0

        mean_radio_drop = np.mean(radio_drops)
        mean_queue_overflow = np.mean(queue_overflows)
        mean_suppressed = np.mean(suppressed)
        mean_total_opps = np.mean(total_opps)

        rows.append({
            "scenario": scenario,
            "sources": sources,
            "verify_ms": verify_ms,
            "policy": policy,
            "n_replications": n,
            "mean_opp_success_rate": float(mean_opp_succ),
            "std_opp_success_rate": float(std_opp_succ),
            "ci95_opp_success_rate": float(ci95_opp_succ),
            "mean_freshness_rate": float(mean_fresh),
            "std_freshness_rate": float(std_fresh),
            "ci95_freshness_rate": float(ci95_fresh),
            "mean_latency_ms": float(mean_lat),
            "std_latency_ms": float(std_lat),
            "mean_radio_drops": float(mean_radio_drop),
            "mean_queue_overflows": float(mean_queue_overflow),
            "mean_suppressed": float(mean_suppressed),
            "mean_total_opps": float(mean_total_opps)
        })

    # Paired differences: joint vs other policies for same seed
    paired_rows = []
    # Index by (scenario, sources, verify_ms, seed)
    by_condition_seed = {}
    for r in runs_data:
        key = (r["scenario"], r["sources"], r["verify_ms"], r["seed"])
        by_condition_seed.setdefault(key, {})[r["policy"]] = r

    for (scenario, sources, verify_ms, seed), pol_map in by_condition_seed.items():
        if "joint" not in pol_map:
            continue
        joint_r = pol_map["joint"]
        for other_pol in ["fixed", "radio", "receiver", "dcc"]:
            if other_pol in pol_map:
                other_r = pol_map[other_pol]
                paired_rows.append({
                    "scenario": scenario,
                    "sources": sources,
                    "verify_ms": verify_ms,
                    "seed": seed,
                    "comparison": f"joint_vs_{other_pol}",
                    "delta_opp_success": joint_r["opp_success_rate"] - other_r["opp_success_rate"],
                    "delta_freshness": joint_r["freshness_rate"] - other_r["freshness_rate"],
                    "delta_latency_ms": joint_r["mean_latency_ms"] - other_r["mean_latency_ms"]
                })

    # Save to CSV and JSON
    res_csv = proc_dir / "results.csv"
    with res_csv.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    paired_csv = proc_dir / "paired_differences.csv"
    if paired_rows:
        with paired_csv.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=list(paired_rows[0].keys()))
            writer.writeheader()
            writer.writerows(paired_rows)

    summary_json = proc_dir / "summary.json"
    summary_json.write_text(json.dumps({
        "aggregated_conditions": len(rows),
        "total_evaluated_runs": len(runs_data),
        "records": rows
    }, indent=2) + "\n")

    print(f"Analysis complete! Aggregated {len(rows)} conditions into {res_csv} and {summary_json}")
    return proc_dir


def generate_figures(manifest_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    proc_dir = Path("results/processed/evaluation")
    res_csv = proc_dir / "results.csv"
    if not res_csv.exists():
        analyze_campaign(manifest_path)

    with res_csv.open() as f:
        data = list(csv.DictReader(f))

    fig_dir = Path("figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Set overall aesthetic style
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 13,
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.family": "sans-serif"
    })

    palette = {
        "fixed": "#7f7f7f",       # Gray
        "radio": "#1f77b4",       # Blue
        "receiver": "#ff7f0e",    # Orange
        "dcc": "#2ca02c",         # Green
        "joint": "#d62728"        # Red
    }
    policy_labels = {
        "fixed": "Fixed 10 Hz",
        "radio": "Radio-Only CBR",
        "receiver": "Receiver-Only Backlog",
        "dcc": "ETSI DCC (Adaptive)",
        "joint": "Joint Radio-Receiver (Proposed)"
    }

    # -------------------------------------------------------------
    # Figure 1: Pipeline & Timing Contract Architecture (Conceptual/Structural)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 4.2), layout="constrained")
    ax.axis("off")

    boxes = [
        ("Sensor Acquisition\n(Exogenous t_acq)", 0.08, 0.65, 0.16, 0.22, "#e3f2fd"),
        ("Inference & Signing\n(10 ms + 1 ms)", 0.30, 0.65, 0.16, 0.22, "#e8f5e9"),
        ("Radio Broadcast\n(802.11p PHY/MAC)", 0.52, 0.65, 0.16, 0.22, "#fff3e0"),
        ("Receiver FCFS Queue\n& Verification (1-3 ms)", 0.74, 0.65, 0.18, 0.22, "#fce4ec"),
        ("Authenticated Fusion\nReadiness (<= Deadline)", 0.74, 0.18, 0.18, 0.22, "#e1f5fe"),
        ("Signed Feedback Channel\n(Queue Backlog)", 0.41, 0.18, 0.24, 0.22, "#fff9c4"),
    ]

    from matplotlib.patches import FancyBboxPatch
    for label, x, y, w, h, col in boxes:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", facecolor=col, edgecolor="#333333", linewidth=1.5,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", color="#111111", weight="bold",
                fontsize=8.5, transform=ax.transAxes)

    # Arrows
    arrowprops = dict(arrowstyle="->", lw=1.8, color="#222222")
    ax.annotate("", xy=(0.30, 0.76), xytext=(0.24, 0.76), xycoords="axes fraction", arrowprops=arrowprops)
    ax.annotate("", xy=(0.52, 0.76), xytext=(0.46, 0.76), xycoords="axes fraction", arrowprops=arrowprops)
    ax.annotate("", xy=(0.74, 0.76), xytext=(0.68, 0.76), xycoords="axes fraction", arrowprops=arrowprops)
    ax.annotate("", xy=(0.83, 0.40), xytext=(0.83, 0.65), xycoords="axes fraction", arrowprops=arrowprops)
    
    # Feedback arrows
    ax.annotate("", xy=(0.65, 0.29), xytext=(0.74, 0.29), xycoords="axes fraction", arrowprops=arrowprops)
    ax.annotate("Rate & Congestion Control", xy=(0.16, 0.65), xytext=(0.41, 0.29), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#d62728", connectionstyle="arc3,rad=0.3"),
                ha="center", va="bottom", color="#d62728", weight="bold", fontsize=8.5)

    ax.set_title("Figure 1: End-to-End System Timing, Processing Stages, and Causal Feedback Loop", pad=12)
    fig.savefig(fig_dir / "figure1_architecture.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 2: Timely Opportunity Success Rate vs. Vehicle Density (Intersection)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharey=True, layout="constrained")
    v_cases = [(1.0, axes[0], "Radio-Dominant Regime (tau_verify = 1.0 ms)"),
               (3.0, axes[1], "Verification-Stressed Regime (tau_verify = 3.0 ms)")]

    for v_val, ax, title in v_cases:
        subset = [r for r in data if r["scenario"] == "intersection" and float(r["verify_ms"]) == v_val]
        for pol in ["fixed", "radio", "receiver", "dcc", "joint"]:
            pol_data = sorted([r for r in subset if r["policy"] == pol], key=lambda x: int(x["sources"]))
            if not pol_data:
                continue
            x = [int(r["sources"]) for r in pol_data]
            y = [float(r["mean_opp_success_rate"]) for r in pol_data]
            err = [float(r["ci95_opp_success_rate"]) for r in pol_data]
            ax.errorbar(x, y, yerr=err, fmt="-o", label=policy_labels[pol], color=palette[pol],
                        capsize=4, linewidth=1.8, markersize=5)
        ax.set_title(title)
        ax.set_xlabel("Vehicle Density (Sources N)")
        ax.set_xticks([12, 24, 48])
        ax.grid(True, linestyle="--", alpha=0.5)

    axes[0].set_ylabel("Timely Opportunity Success Rate")
    axes[0].set_ylim(-0.02, 1.05)
    axes[1].legend(loc="upper right", framealpha=0.9)
    fig.suptitle("Figure 2: Timely Opportunity Success Rate vs. Vehicle Density (Urban Intersection)", fontsize=13)
    fig.savefig(fig_dir / "figure2_timeliness_vs_density.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 3: Bottleneck Shift - Failure Reason Decomposition (48 Sources)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharey=True, layout="constrained")
    panels = [(1.0, axes[0], "Light Verification (tau_verify = 1.0 ms)"),
              (3.0, axes[1], "Heavy Verification (tau_verify = 3.0 ms)")]

    policies = ["fixed", "radio", "receiver", "dcc", "joint"]
    x_indices = np.arange(len(policies))

    for v_val, ax, title in panels:
        subset = {r["policy"]: r for r in data if r["scenario"] == "intersection" and float(r["verify_ms"]) == v_val and int(r["sources"]) == 48}
        radio_pcts = []
        queue_pcts = []
        suppressed_pcts = []
        success_pcts = []

        for pol in policies:
            if pol in subset:
                r = subset[pol]
                tot = float(r["mean_total_opps"]) if float(r["mean_total_opps"]) > 0 else 1.0
                succ = float(r["mean_opp_success_rate"])
                rd = float(r["mean_radio_drops"]) / tot
                qo = float(r["mean_queue_overflows"]) / tot
                sp = float(r["mean_suppressed"]) / tot
                success_pcts.append(succ)
                radio_pcts.append(rd)
                queue_pcts.append(qo)
                suppressed_pcts.append(sp)
            else:
                success_pcts.append(0); radio_pcts.append(0); queue_pcts.append(0); suppressed_pcts.append(0)

        p1 = ax.bar(x_indices, success_pcts, color="#4caf50", label="Success (Timely & Verified)")
        p2 = ax.bar(x_indices, radio_pcts, bottom=success_pcts, color="#2196f3", label="Radio Loss (Collision/Propagation)")
        bottom2 = np.array(success_pcts) + np.array(radio_pcts)
        p3 = ax.bar(x_indices, queue_pcts, bottom=bottom2, color="#e91e63", label="Verification Queue Overflow")
        bottom3 = bottom2 + np.array(queue_pcts)
        p4 = ax.bar(x_indices, suppressed_pcts, bottom=bottom3, color="#ff9800", label="Rate-Controlled Suppression")

        ax.set_title(title)
        ax.set_xticks(x_indices)
        ax.set_xticklabels([policy_labels[p].split()[0] for p in policies], rotation=15)
        ax.set_xlabel("Policy")
        ax.grid(True, linestyle="--", alpha=0.4, axis="y")

    axes[0].set_ylabel("Fraction of Exogenous Demand")
    axes[0].set_ylim(0, 1.05)
    axes[1].legend(loc="upper right", framealpha=0.9, fontsize=8)
    fig.suptitle("Figure 3: Bottleneck Shift Across Operating Regimes (Intersection, N = 48 Sources)", fontsize=13)
    fig.savefig(fig_dir / "figure3_bottleneck_shift.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 4: End-to-End Latency Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 4.2), layout="constrained")
    subset_24 = [r for r in data if r["scenario"] == "intersection" and float(r["verify_ms"]) == 1.0 and int(r["sources"]) == 24]
    
    pols = []
    latencies = []
    errors = []
    colors = []
    for pol in ["fixed", "radio", "receiver", "dcc", "joint"]:
        r = next((x for x in subset_24 if x["policy"] == pol), None)
        if r and float(r["mean_latency_ms"]) > 0:
            pols.append(policy_labels[pol])
            latencies.append(float(r["mean_latency_ms"]))
            errors.append(float(r["std_latency_ms"]))
            colors.append(palette[pol])

    bars = ax.bar(pols, latencies, yerr=errors, capsize=5, color=colors, edgecolor="#222222", linewidth=1.2)
    ax.axhline(100.0, color="#d32f2f", linestyle="--", linewidth=1.5, label="Evaluation Deadline (100 ms)")
    ax.set_ylabel("Mean Delivery & Verification Latency (ms)")
    ax.set_title("Figure 4: Mean Successful Update Latency (Intersection, N = 24, tau_verify = 1.0 ms)")
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax.legend(loc="upper left")
    plt.xticks(rotation=20, ha="right")
    fig.savefig(fig_dir / "figure4_latency_cdf.png", dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------
    # Figure 5: Highway Mobility Generalization
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 4.5), layout="constrained")
    hw_subset = [r for r in data if r["scenario"] == "highway" and float(r["verify_ms"]) == 1.0]

    for pol in ["fixed", "radio", "receiver", "dcc", "joint"]:
        pol_data = sorted([r for r in hw_subset if r["policy"] == pol], key=lambda x: int(x["sources"]))
        if not pol_data:
            continue
        x = [int(r["sources"]) for r in pol_data]
        y = [float(r["mean_opp_success_rate"]) for r in pol_data]
        err = [float(r["ci95_opp_success_rate"]) for r in pol_data]
        ax.errorbar(x, y, yerr=err, fmt="-s", label=policy_labels[pol], color=palette[pol],
                    capsize=4, linewidth=1.8, markersize=5)

    ax.set_title("Figure 5: Policy Generalization to Highway Mobility (tau_verify = 1.0 ms)")
    ax.set_xlabel("Vehicle Density (Sources N)")
    ax.set_ylabel("Timely Opportunity Success Rate")
    ax.set_xticks([12, 24, 48])
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower left", framealpha=0.9)
    fig.savefig(fig_dir / "figure5_highway_generalization.png", dpi=300)
    plt.close(fig)

    print("All 5 figures generated successfully in figures/")
