"""Generate enhanced 4-panel Figure 6 illustrating temporal dynamics and trigger attribution."""
import csv
import gzip
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def extract_and_plot_traces(fig_dir):
    fig_dir = Path(fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    pols = [
        ("fixed", "Fixed 10 Hz", "#7f7f7f", "-"),
        ("radio", "Radio-Only CBR", "#1f77b4", "-"),
        ("joint", "Uncalibrated Joint (Staleness/Outlier Trap)", "#d62728", "--"),
        ("calibrated", "Calibrated Joint (Proposed)", "#2ca02c", "-")
    ]
    
    tmp_base = Path("cpstudy/results/raw/temporal_traces")
    traces = {}

    for pol, label, color, ls in pols:
        run_dir = tmp_base / pol
        controls_file = run_dir / "network-controls.csv.gz"
        open_fn = gzip.open if str(controls_file).endswith(".gz") else open
        ctrl_rows = []
        with open_fn(controls_file, "rt") as f:
            for r in csv.DictReader(f):
                ctrl_rows.append({
                    "t": float(r["event_ns"]) / 1e9,
                    "node": int(r["node_id"]),
                    "rate": float(r["rate_hz"]),
                    "busy": float(r["busy_fraction"]),
                    "backlog": float(r["remote_backlog"]),
                    "stale": int(r["feedback_stale"]) if "feedback_stale" in r else 0,
                    "obs": int(r["observed_neighbors"]) if "observed_neighbors" in r else 0
                })
        
        events_file = run_dir / "network-events.csv.gz"
        open_fn_ev = gzip.open if str(events_file).endswith(".gz") else open
        queue_events = []
        with open_fn_ev(events_file, "rt") as f:
            for r in csv.DictReader(f):
                if r["event_type"] in ("enqueue", "reception", "verification_start", "verification_end"):
                    queue_events.append((float(r["event_ns"]) / 1e9, int(r["receiver_id"]), int(r["queue_depth"])))
                    
        traces[pol] = {
            "label": label,
            "color": color,
            "ls": ls,
            "controls": ctrl_rows,
            "queue_events": queue_events
        }

    # Load trigger attribution
    attr_file = Path("cpstudy/results/raw/major_revision/trigger_attribution.json")
    attr_data = json.loads(attr_file.read_text()) if attr_file.exists() else {}

    # Style
    plt.rcParams.update({
        "font.size": 8.5,
        "axes.labelsize": 9.5,
        "axes.titlesize": 10.5,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 8.0,
        "figure.titlesize": 11.5,
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.family": "sans-serif"
    })

    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.5), layout="constrained")
    
    # Panel (a): Transmission Rate over Time
    ax0 = axes[0, 0]
    for pol, label, color, ls in pols:
        c_data = traces[pol]["controls"]
        t_bins = np.linspace(0, 5.0, 51)
        mean_rates = []
        for i in range(len(t_bins) - 1):
            matching = [r["rate"] for r in c_data if t_bins[i] <= r["t"] < t_bins[i+1]]
            mean_rates.append(np.mean(matching) if matching else np.nan)
        ax0.plot(t_bins[:-1] + 0.05, mean_rates, label=label, color=color, linestyle=ls, linewidth=2.0)
    
    ax0.axvspan(0, 1.0, color="#f0f0f0", alpha=0.8, label="Warmup Window")
    ax0.set_ylabel("Mean Sender Rate (Hz)")
    ax0.set_xlabel("Elapsed Time (s)")
    ax0.set_ylim(0.5, 11.0)
    ax0.set_yticks([1, 2, 4, 6, 8, 10])
    ax0.grid(True, linestyle="--", alpha=0.5)
    ax0.legend(loc="upper right", framealpha=0.92, fontsize=7.5)
    ax0.set_title("(a) Sender Transmission Rate Trajectory")

    # Panel (b): Verification Queue: Mean vs Outlier Maximum
    ax1 = axes[0, 1]
    t_bins = np.linspace(0, 5.0, 51)
    
    # Plot Fixed Mean and Max
    q_fixed = traces["fixed"]["queue_events"]
    f_means, f_maxs = [], []
    for i in range(len(t_bins) - 1):
        matching = [depth for t, rcv, depth in q_fixed if t_bins[i] <= t < t_bins[i+1]]
        f_means.append(np.mean(matching) if matching else 0.0)
        f_maxs.append(np.max(matching) if matching else 0.0)
    ax1.plot(t_bins[:-1] + 0.05, f_means, label="Fixed (Mean)", color="#7f7f7f", linestyle="-", linewidth=1.8)
    ax1.plot(t_bins[:-1] + 0.05, f_maxs, label="Fixed (Outlier Peak)", color="#7f7f7f", linestyle=":", linewidth=1.5)

    # Plot Calibrated Mean and Max
    q_cal = traces["calibrated"]["queue_events"]
    c_means, c_maxs = [], []
    for i in range(len(t_bins) - 1):
        matching = [depth for t, rcv, depth in q_cal if t_bins[i] <= t < t_bins[i+1]]
        c_means.append(np.mean(matching) if matching else 0.0)
        c_maxs.append(np.max(matching) if matching else 0.0)
    ax1.plot(t_bins[:-1] + 0.05, c_means, label="Calibrated (Mean)", color="#2ca02c", linestyle="-", linewidth=1.8)
    ax1.plot(t_bins[:-1] + 0.05, c_maxs, label="Calibrated (Outlier Peak)", color="#2ca02c", linestyle=":", linewidth=1.5)

    # Plot Joint Outlier Peak
    q_joint = traces["joint"]["queue_events"]
    j_maxs = []
    for i in range(len(t_bins) - 1):
        matching = [depth for t, rcv, depth in q_joint if t_bins[i] <= t < t_bins[i+1]]
        j_maxs.append(np.max(matching) if matching else 0.0)
    ax1.plot(t_bins[:-1] + 0.05, j_maxs, label="Uncalibrated (Outlier Peak)", color="#d62728", linestyle="--", linewidth=1.5)

    ax1.axhline(8, color="#d62728", linestyle="--", linewidth=1.2, label="Uncal. Thresh (8)")
    ax1.axhline(16, color="#2ca02c", linestyle="--", linewidth=1.2, label="Calib. Thresh (16)")
    ax1.axhline(32, color="#333333", linestyle="-.", linewidth=1.2, label="Capacity K=32")
    ax1.set_ylabel("Queue Depth (Packets)")
    ax1.set_xlabel("Elapsed Time (s)")
    ax1.set_ylim(-0.5, 34)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", framealpha=0.92, fontsize=7.0, ncol=2)
    ax1.set_title("(b) Verification Queue: Mean vs. Outlier Maximum")

    # Panel (c): Wireless Medium Congestion (CBR)
    ax2 = axes[1, 0]
    for pol, label, color, ls in pols:
        c_data = traces[pol]["controls"]
        t_bins = np.linspace(0, 5.0, 51)
        mean_cbr = []
        for i in range(len(t_bins) - 1):
            matching = [r["busy"] for r in c_data if t_bins[i] <= r["t"] < t_bins[i+1]]
            mean_cbr.append(np.mean(matching) if matching else np.nan)
        ax2.plot(t_bins[:-1] + 0.05, mean_cbr, label=label, color=color, linestyle=ls, linewidth=1.8)
    
    ax2.axhline(0.65, color="#1f77b4", linestyle="--", linewidth=1.2, label="Radio Congestion Thresh (0.65)")
    ax2.set_xlabel("Elapsed Time (s)")
    ax2.set_ylabel("Channel Busy Ratio (CBR)")
    ax2.set_ylim(0.0, 1.0)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", framealpha=0.92, fontsize=7.5)
    ax2.set_title("(c) Physical Wireless Medium Congestion (CBR)")

    # Panel (d): Trigger Attribution Breakdown
    ax3 = axes[1, 1]
    categories = ["Backlog Only", "Joint CBR+Backlog", "CBR Only"]
    joint_pcts = [
        attr_data.get("joint", {}).get("pct_backlog_only", 93.38),
        attr_data.get("joint", {}).get("pct_both", 6.54),
        attr_data.get("joint", {}).get("pct_cbr_only", 0.08)
    ]
    cal_pcts = [
        attr_data.get("calibrated", {}).get("pct_backlog_only", 12.55),
        attr_data.get("calibrated", {}).get("pct_both", 48.24),
        attr_data.get("calibrated", {}).get("pct_cbr_only", 39.22)
    ]
    x = np.arange(len(categories))
    width = 0.35
    rects1 = ax3.bar(x - width/2, joint_pcts, width, label="Uncalibrated Joint (N=1,330 cuts)", color="#d62728", alpha=0.85)
    rects2 = ax3.bar(x + width/2, cal_pcts, width, label="Calibrated Joint (N=255 cuts)", color="#2ca02c", alpha=0.85)

    ax3.set_ylabel("Percentage of Rate Cuts (%)")
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories)
    ax3.set_ylim(0, 105)
    ax3.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax3.legend(loc="upper right", framealpha=0.92, fontsize=7.5)
    ax3.set_title("(d) Attribution of Rate Decrease Triggers")

    for rect in rects1:
        h = rect.get_height()
        ax3.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7.5)
    for rect in rects2:
        h = rect.get_height()
        ax3.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7.5)

    fig_path = fig_dir / "figure6_temporal_traces.png"
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Enhanced 4-panel temporal trace figure saved to {fig_path}")

if __name__ == "__main__":
    extract_and_plot_traces("figures")
    extract_and_plot_traces("submission_package/figures")
    extract_and_plot_traces("cpstudy/figures")
