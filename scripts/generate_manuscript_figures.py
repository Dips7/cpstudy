#!/usr/bin/env python3
"""Generate clean, audited, publication-grade figures for the manuscript."""

from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)


def generate_fig1():
    """Generate a clean, publication-grade, human-designed architectural and timing diagram."""
    fig = plt.figure(figsize=(11.5, 6.2), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # -------------------------------------------------------------
    # 1. SUBSYSTEM ENCLOSING CONTAINERS (Top Half: y = 42 to 92)
    # -------------------------------------------------------------
    # Container 1: Sender Vehicle Subsystem (x = 3 to 34)
    p_sender = FancyBboxPatch((3, 44), 31, 48, boxstyle="round,pad=0.8", facecolor="#F8FAFC", edgecolor="#2563EB", linewidth=1.8, linestyle="--")
    ax.add_patch(p_sender)
    ax.text(18.5, 89.5, "SENDER VEHICLE PIPELINE", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E3A8A")

    # Container 2: Wireless Channel (x = 37 to 61)
    p_channel = FancyBboxPatch((37, 44), 24, 48, boxstyle="round,pad=0.8", facecolor="#F0FDF4", edgecolor="#059669", linewidth=1.8, linestyle="--")
    ax.add_patch(p_channel)
    ax.text(49, 89.5, "802.11p WIRELESS CHANNEL", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#065F46")

    # Container 3: Receiver Vehicle Subsystem (x = 64 to 97)
    p_receiver = FancyBboxPatch((64, 44), 33, 48, boxstyle="round,pad=0.8", facecolor="#FAF5FF", edgecolor="#7C3AED", linewidth=1.8, linestyle="--")
    ax.add_patch(p_receiver)
    ax.text(80.5, 89.5, "RECEIVER VERIFICATION PIPELINE", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#5B21B6")

    # -------------------------------------------------------------
    # 2. INNER PROCESSING STAGE BOXES
    # -------------------------------------------------------------
    # Sender Box 1: Opportunity Engine
    p_opp = FancyBboxPatch((5, 71), 27, 14, boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.3)
    ax.add_patch(p_opp)
    ax.text(18.5, 80, "1. Periodic Opportunity Demand", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E40AF")
    ax.text(18.5, 74.5, "10 Hz tick (Tint = 100 ms) | Range \u2264 150m\nDenominator: all evaluated demand pairs", ha="center", va="center", fontsize=7.2, color="#334155")

    # Sender Box 2: Transmission Controller
    p_ctrl = FancyBboxPatch((5, 48), 12.5, 17, boxstyle="round,pad=0.5", facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.3)
    ax.add_patch(p_ctrl)
    ax.text(11.25, 61.5, "2. Transmission Control", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#92400E")
    ax.text(11.25, 54, "Fixed 10 Hz / Radio CBR\nUncalibrated / Calibrated\nRate: 1\u201310 Hz (100ms)", ha="center", va="center", fontsize=6.8, color="#451A03")

    # Sender Box 3: Sensor & Crypto
    p_sign = FancyBboxPatch((19.5, 48), 12.5, 17, boxstyle="round,pad=0.5", facecolor="#DBEAFE", edgecolor="#2563EB", linewidth=1.3)
    ax.add_patch(p_sign)
    ax.text(25.75, 61.5, "3. Sensing & Signing", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#1E40AF")
    ax.text(25.75, 54, "Inference: 10 ms fixed\nSigning: 1 ms fixed\nPayload: 1200 bytes", ha="center", va="center", fontsize=6.8, color="#1E293B")

    # Channel Box: Radio Broadcast
    p_rad = FancyBboxPatch((39, 53), 20, 28, boxstyle="round,pad=0.5", facecolor="#DCFCE7", edgecolor="#16A34A", linewidth=1.3)
    ax.add_patch(p_rad)
    ax.text(49, 76.5, "4. ns-3 802.11p Broadcast", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#166534")
    ax.text(49, 66, "AdhocWifiMac | 6 Mbps\nCh 172 (5.86 GHz), 23 dBm\nLog-distance loss (n=2.5)\nCSMA/CA Contention", ha="center", va="center", fontsize=7.2, color="#14532D")
    ax.text(49, 56.5, "Terminal failure: Radio Drop\n(Collision or Pathloss)", ha="center", va="center", fontsize=6.8, fontweight="semibold", color="#B91C1C")

    # Receiver Box 1: Verification Queue
    p_q = FancyBboxPatch((66, 48), 14, 34, boxstyle="round,pad=0.5", facecolor="#F3E8FF", edgecolor="#9333EA", linewidth=1.3)
    ax.add_patch(p_q)
    ax.text(73, 78, "5. Verification Queue", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#6B21A8")
    ax.text(73, 67, "Non-preemptive FCFS\nWorker: 1 core\nQueue: 32 slots buffer\nDeterministic \u03c4 ms\n(1, 3, 6, 7.5, 10 ms)", ha="center", va="center", fontsize=7.0, color="#3B0764")
    ax.text(73, 53, "Drop: Buffer Overflow\nor Expiry (>100ms)", ha="center", va="center", fontsize=6.8, fontweight="semibold", color="#B91C1C")

    # Receiver Box 2: Fusion Readiness
    p_fus = FancyBboxPatch((82, 48), 13, 34, boxstyle="round,pad=0.5", facecolor="#E0E7FF", edgecolor="#4F46E5", linewidth=1.3)
    ax.add_patch(p_fus)
    ax.text(88.5, 78, "6. Fusion Readiness", ha="center", va="center", fontsize=8.2, fontweight="bold", color="#3730A3")
    ax.text(88.5, 68, "Fusion delay: 2 ms\nValid signatures\nReady check:\nready_time \u2264 deadline", ha="center", va="center", fontsize=7.0, color="#312E81")
    ax.text(88.5, 54, "TIMELY SUCCESS\n(Opportunity Rate)", ha="center", va="center", fontsize=7.2, fontweight="bold", color="#15803D")

    # -------------------------------------------------------------
    # 3. INTER-STAGE CONNECTING ARROWS
    # -------------------------------------------------------------
    arrow_main = dict(facecolor="#1E293B", edgecolor="#1E293B", width=1.5, headwidth=6, headlength=6, shrink=0.08)
    arrow_supp = dict(facecolor="#DC2626", edgecolor="#DC2626", width=1.2, headwidth=5, headlength=5, shrink=0.08)

    # Opportunity -> Controller
    ax.annotate("", xy=(11.25, 65), xytext=(11.25, 71), arrowprops=arrow_main)

    # Controller -> Sensing (Admitted)
    ax.annotate("", xy=(19.5, 56.5), xytext=(17.5, 56.5), arrowprops=arrow_main)
    ax.text(18.5, 58, "Admit", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color="#1E40AF")

    # Controller -> Suppressed (Terminal failure)
    ax.annotate("", xy=(11.25, 45.2), xytext=(11.25, 48), arrowprops=arrow_supp)
    ax.text(11.25, 43.5, "Suppressed (in denom.)", ha="center", va="top", fontsize=6.5, fontweight="semibold", color="#DC2626")

    # Sensing -> Channel
    ax.annotate("", xy=(39, 67), xytext=(32, 56.5), arrowprops=arrow_main)

    # Channel -> Verification Queue (Reception)
    ax.annotate("", xy=(66, 67), xytext=(59, 67), arrowprops=arrow_main)

    # Verification Queue -> Fusion Readiness
    ax.annotate("", xy=(82, 67), xytext=(80, 67), arrowprops=arrow_main)

    # Feedback Loop (Receiver Queue Backlog -> Sender Controller)
    ax.annotate(
        "",
        xy=(11.25, 48),
        xytext=(73, 44),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.25", color="#D97706", lw=1.6, ls=":"),
    )
    ax.text(42, 40, "Periodic Queue Feedback (200 ms interval; 600 ms staleness limit)", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#B45309", bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFBEB", edgecolor="#FCD34D"))

    # -------------------------------------------------------------
    # 4. TIMING BREAKDOWN GANTT TIMELINE (Bottom: y = 5 to 33)
    # -------------------------------------------------------------
    p_time_bg = FancyBboxPatch((3, 4), 94, 30, boxstyle="round,pad=0.8", facecolor="#F1F5F9", edgecolor="#64748B", linewidth=1.5)
    ax.add_patch(p_time_bg)
    ax.text(50, 31, "TIMELINE BREAKDOWN & PER-OPPORTUNITY DEADLINE BUDGET (100 ms WINDOW)", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#0F172A")

    # Timeline Bar Container (y = 15 to 24)
    # 0 to 100 ms mapped onto x = 8 to 92 (span = 84)
    # Scale: x_pos = 8 + (ms / 100.0) * 84
    def t_to_x(ms):
        return 8.0 + (ms / 100.0) * 84.0

    # Draw segments
    # Segment 1: Inference [0, 10] ms
    x0, x1 = t_to_x(0), t_to_x(10)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#3B82F6", edgecolor="#1E3A8A", linewidth=1)
    ax.text((x0 + x1) / 2, 19, "Inference\n10 ms", ha="center", va="center", fontsize=6.8, fontweight="bold", color="#FFFFFF")

    # Segment 2: Signing [10, 11] ms
    x0, x1 = t_to_x(10), t_to_x(11)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#60A5FA", edgecolor="#1E3A8A", linewidth=1)

    # Segment 3: Radio [11, 14] ms
    x0, x1 = t_to_x(11), t_to_x(14)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#10B981", edgecolor="#064E3B", linewidth=1)
    ax.text((x0 + x1) / 2, 23.5, "Radio\n~2 ms", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color="#065F46")

    # Segment 4: Queue Waiting [14, 45] ms (illustrative W_q)
    x0, x1 = t_to_x(14), t_to_x(45)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#DDD6FE", edgecolor="#5B21B6", linewidth=1)
    ax.text((x0 + x1) / 2, 19, "Receiver Verification Queue Waiting (Wq)\n[Contention & Backlog Dependent]", ha="center", va="center", fontsize=7.2, fontweight="semibold", color="#4C1D95")

    # Segment 5: Verification Service [45, 54] ms (illustrative tau = 3 to 9 ms)
    x0, x1 = t_to_x(45), t_to_x(54)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#A855F7", edgecolor="#3B0764", linewidth=1)
    ax.text((x0 + x1) / 2, 19, "Service\n\u03c4 ms", ha="center", va="center", fontsize=6.8, fontweight="bold", color="#FFFFFF")

    # Segment 6: Fusion Delay [54, 60] ms
    x0, x1 = t_to_x(54), t_to_x(60)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#4F46E5", edgecolor="#312E81", linewidth=1)
    ax.text((x0 + x1) / 2, 23.5, "Fusion\n2 ms", ha="center", va="bottom", fontsize=6.5, fontweight="bold", color="#3730A3")

    # Segment 7: Remaining Slack [60, 100] ms
    x0, x1 = t_to_x(60), t_to_x(100)
    ax.barh(19, x1 - x0, left=x0, height=7, color="#E2E8F0", edgecolor="#64748B", linewidth=1, linestyle=":")
    ax.text((x0 + x1) / 2, 19, "Remaining Slack Window before Deadline (Tready \u2264 100 ms \u2192 SUCCESS)", ha="center", va="center", fontsize=7.2, fontweight="bold", color="#0F766E")

    # Ticks along the timeline
    for ms_val in [0, 10, 20, 40, 60, 80, 100]:
        x_val = t_to_x(ms_val)
        ax.plot([x_val, x_val], [14.5, 15.5], color="#475569", lw=1.5)
        ax.text(x_val, 13.2, f"{ms_val} ms", ha="center", va="top", fontsize=7.2, fontweight="semibold", color="#334155")

    # Highlight deadline boundary (100 ms)
    x_dl = t_to_x(100)
    ax.plot([x_dl, x_dl], [12, 28], color="#DC2626", lw=2, linestyle="--")
    ax.text(x_dl, 29, "DEADLINE (100 ms)", ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#DC2626")

    # Timely Success Criterion Text
    ax.text(
        50,
        7.5,
        "Criterion: Eligible update must reach fusion readiness at or before deadline (ready_time \u2264 acquisition_time + 100 ms).\n"
        "Late updates (> 100 ms), queue buffer overflow drops, and radio transmission losses are recorded as non-success.",
        ha="center",
        va="center",
        fontsize=7.5,
        color="#1E293B",
        style="italic",
    )

    fig.savefig(FIG_DIR / "fig1_pipeline_timing.png", bbox_inches="tight")
    plt.close(fig)
    print("+ Saved Figure 1 (Reworked human-designed):", FIG_DIR / "fig1_pipeline_timing.png")


def generate_fig2():
    with open(ROOT / "results/processed/rework/utilization_recomputed.json") as f:
        summary_list = json.load(f)["summary"]

    util_data = {row["verify_ms"]: row for row in summary_list}

    v_ms = [1.0, 3.0, 6.0, 7.5, 10.0]
    mean_rho = [util_data[v]["rho_mean_offered"] for v in v_ms]
    median_rho = [util_data[v]["rho_median_offered"] for v in v_ms]
    max_rho = [util_data[v]["rho_max_offered"] for v in v_ms]

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)
    ax.plot(v_ms, mean_rho, marker="o", color="#2563EB", linewidth=2, label=r"Mean Offered Load $\rho$")
    ax.plot(v_ms, median_rho, marker="s", color="#059669", linewidth=1.8, linestyle="--", label=r"Median Offered Load $\rho$")
    ax.plot(v_ms, max_rho, marker="^", color="#DC2626", linewidth=1.5, linestyle=":", label=r"Max Receiver Offered Load $\rho$")
    ax.axhline(1.0, color="#64748B", linestyle="-.", linewidth=1.2, label=r"Nominal Saturation Boundary ($\rho = 1.0$)")

    rho_3 = util_data[3.0]["rho_mean_offered"]
    rho_6 = util_data[6.0]["rho_mean_offered"]
    gt1_3 = util_data[3.0]["mean_receivers_over_one_of_48"]
    gt1_6 = util_data[6.0]["mean_receivers_over_one_of_48"]
    pct_gt1_6 = (gt1_6 / 48.0) * 100.0

    ax.scatter([3.0], [rho_3], color="#2563EB", s=70, zorder=5)
    ax.annotate(
        f"3 ms: Mean $\\rho = {rho_3:.3f}$\n({int(gt1_3)} nodes > 1.0)",
        xy=(3.0, rho_3),
        xytext=(2.2, 0.95),
        arrowprops=dict(facecolor="#1E293B", shrink=0.08, width=1, headwidth=4),
        fontsize=8,
        fontweight="medium",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#F8FAFC", edgecolor="#CBD5E1"),
    )

    ax.scatter([6.0], [rho_6], color="#2563EB", s=70, zorder=5)
    ax.annotate(
        f"6 ms: Mean $\\rho = {rho_6:.3f}$\n({pct_gt1_6:.1f}% nodes > 1.0)",
        xy=(6.0, rho_6),
        xytext=(5.0, 1.55),
        arrowprops=dict(facecolor="#1E293B", shrink=0.08, width=1, headwidth=4),
        fontsize=8,
        fontweight="medium",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#F8FAFC", edgecolor="#CBD5E1"),
    )

    ax.set_xlabel(r"Synthetic Verification Service Duration $\tau$ (ms)", fontsize=9.5, fontweight="semibold")
    ax.set_ylabel(r"Offered Load $\rho = \lambda \tau$", fontsize=9.5, fontweight="semibold")
    ax.set_title("Figure 2. Receiver Offered Load across Synthetic Service Durations\n(Calculated from Common Fixed-Policy Baseline Trace)", fontsize=9.5, fontweight="bold", pad=10)
    ax.set_xticks(v_ms)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, fontsize=8, loc="upper left")
    ax.set_ylim(0, 3.2)

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig2_offered_load.png", bbox_inches="tight")
    plt.close(fig)
    print("+ Saved Figure 2:", FIG_DIR / "fig2_offered_load.png")


def generate_fig3():
    # Read verified analysis outputs dynamically
    import csv

    policy_csv = ROOT / "results/processed/rework/paired_policy_recomputed.csv"
    contrasts_csv = ROOT / "results/processed/rework/paired_contrasts_recomputed.csv"

    policy_data = {}
    with open(policy_csv, newline="") as f:
        for row in csv.DictReader(f):
            policy_data[row["policy"]] = {
                "mean": float(row["opportunity_success_rate_mean"]) * 100.0,
                "ci95_half": float(row["opportunity_success_rate_ci95_half"]) * 100.0,
            }

    contrasts_data = {}
    with open(contrasts_csv, newline="") as f:
        for row in csv.DictReader(f):
            if row["metric"] == "opportunity_success_rate":
                contrasts_data[row["contrast"]] = {
                    "mean_delta": float(row["mean_delta"]) * 100.0,
                    "ci95_half": float(row["ci95_half"]) * 100.0,
                }

    # Verified policies and values
    policies = ["Fixed 10 Hz", "Radio", "Calibrated", "Joint"]
    pol_keys = ["fixed", "radio", "calibrated", "joint"]
    means = [policy_data[k]["mean"] for k in pol_keys]
    ci_halves = [policy_data[k]["ci95_half"] for k in pol_keys]
    colors = ["#1D4ED8", "#0D9488", "#F59E0B", "#EF4444"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4), dpi=300)

    x_pos = np.arange(len(policies))
    bars = ax1.bar(x_pos, means, yerr=ci_halves, capsize=4, color=colors, alpha=0.85, edgecolor="#0F172A", linewidth=1.1)
    ax1.set_ylabel("Same-Opportunity Success Rate (%)", fontsize=9, fontweight="semibold")
    ax1.set_title("(a) Policy Means with 95% t-Intervals (n=20)", fontsize=9.5, fontweight="bold", pad=10)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(policies, fontsize=8.5, fontweight="medium")
    ax1.set_ylim(0, 105)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, m in zip(bars, means):
        ax1.text(bar.get_x() + bar.get_width() / 2, m + 4.5, f"{m:.2f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")

    contrasts = ["Calibrated \u2212 Joint", "Calibrated \u2212 Radio", "Calibrated \u2212 Fixed"]
    contrast_keys = ["calibrated_minus_joint", "calibrated_minus_radio", "calibrated_minus_fixed"]
    diffs = [contrasts_data[k]["mean_delta"] for k in contrast_keys]
    ci_diffs = [contrasts_data[k]["ci95_half"] for k in contrast_keys]
    c_colors = ["#10B981", "#E11D48", "#E11D48"]

    y_pos = np.arange(len(contrasts))
    ax2.axvline(0, color="#64748B", linestyle="--", linewidth=1.1)
    ax2.errorbar(diffs, y_pos, xerr=ci_diffs, fmt="o", color="#1E293B", ecolor="#475569", elinewidth=1.8, capsize=4, markersize=7, zorder=4)

    # Position negative contrast labels to the right of their points and positive contrast to the left
    # to orient labels inward toward the center and avoid clipping at the plot frame boundaries.
    for i, (d, ci, col) in enumerate(zip(diffs, ci_diffs, c_colors)):
        sign = "+" if d > 0 else ""
        if d > 0:
            x_txt = d - ci - 1.8
            ha = "right"
        else:
            x_txt = d + ci + 1.8
            ha = "left"
        ax2.text(x_txt, i, f"{sign}{d:.2f} pp (95% CI \u00b1{ci:.2f})", ha=ha, va="center", fontsize=7.5, fontweight="bold", color=col)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(contrasts, fontsize=8.5, fontweight="medium")
    ax2.set_xlabel("Paired Difference in Success Rate (pp)", fontsize=9, fontweight="semibold")
    ax2.set_title("(b) Paired Differences with 95% t-Intervals (n=20 pairs)", fontsize=9.5, fontweight="bold", pad=12)
    ax2.set_xlim(-58, 58)
    ax2.set_ylim(-0.6, 2.6)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("Figure 3. Twenty-Seed Paired Evaluation (48 Sources, Intersection, 3 ms Service)", fontsize=10.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(FIG_DIR / "fig3_paired_comparison.png", bbox_inches="tight")
    plt.close(fig)
    print("+ Saved Figure 3:", FIG_DIR / "fig3_paired_comparison.png")


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
