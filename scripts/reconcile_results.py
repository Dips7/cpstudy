"""Recompute Phase 3 stress, ablation, and paired results from audited summaries.

This reads historical run summaries and the independent outcome audit. It writes
only to results/processed/rework and never modifies preserved raw runs.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/processed/rework"
AUDIT = ROOT / "evidence/outcome_audit.json"
RAW_MAJOR = ROOT / "results/raw/major_revision"
RAW_PAIRED = ROOT / "results/raw/paired_intersection_n48_v30"
METRICS = ("opportunity_success_rate", "opportunity_freshness_rate", "mean_success_latency_ms")


def ci(values):
    if not values:
        return None, None, None
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, None, None
    half = stats.t.ppf(0.975, len(values) - 1) * stats.sem(values)
    return mean, statistics.stdev(values), float(half)


def load_summary(path):
    return json.loads(path.read_text())


def summarize_group(rows, keys):
    result = {key: rows[0][key] for key in keys}
    result["n"] = len(rows)
    for metric in METRICS:
        vals = [float(row[metric]) for row in rows if row.get(metric) is not None]
        result[f"{metric}_n"] = len(vals)
        mean, sd, half = ci(vals)
        result[f"{metric}_mean"] = mean
        result[f"{metric}_sd"] = sd
        result[f"{metric}_ci95_half"] = half
    for metric in ("suppressed", "queue_overflow", "verification_expired", "fusion_expired", "radio_not_received"):
        vals = [row[metric] for row in rows]
        result[f"{metric}_mean"] = sum(vals) / len(vals)
    return result


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        fields = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads(AUDIT.read_text())
    passed = {Path(r["run"]).name for r in audit["passed_run_records"]}
    run_rows = []
    for family, base in (("stress", RAW_MAJOR), ("paired20", RAW_PAIRED), ("ablation", RAW_MAJOR)):
        for path in sorted(base.glob("*/summary.json")):
            name = path.parent.name
            if name not in passed:
                continue
            if family == "stress" and not name.startswith("stress_v"):
                continue
            if family == "paired20" and not re.match(r"^(fixed|radio|joint|calibrated)_s\d+$", name):
                continue
            if family == "ablation" and not name.startswith("ab_"):
                continue
            m = load_summary(path)
            tc = m.get("terminal_counts", {})
            row = {"family": family, "run": name, "seed": int(m["seed"]),
                   "opportunity_receiver_pairs": m.get("opportunity_receiver_pairs"),
                   "generated_receiver_pairs": m.get("generated_receiver_pairs")}
            for metric in METRICS:
                row[metric] = m.get(metric)
            for metric in ("suppressed", "queue_overflow", "verification_expired", "fusion_expired", "radio_not_received"):
                row[metric] = tc.get(metric, 0)
            if family == "stress":
                sm = re.match(r"stress_v([\d.]+)_(.+)_s(\d+)$", name)
                if not sm:
                    continue
                row.update(verify_ms=float(sm.group(1)) / 10 if int(float(sm.group(1))) >= 10 else float(sm.group(1)), policy=sm.group(2))
                # Folder tags encode milliseconds in tenths: v10=1ms, v75=7.5ms, v100=10ms.
                tag = sm.group(1)
                row["verify_ms"] = float(tag) / 10.0
                row["policy"] = sm.group(2)
            elif family == "paired20":
                pm = re.match(r"(fixed|radio|joint|calibrated)_s(\d+)$", name)
                row.update(policy=pm.group(1), seed=int(pm.group(2)))
            else:
                row["ablation"] = name[3:].rsplit("_s", 1)[0]
            run_rows.append(row)

    stress = [r for r in run_rows if r["family"] == "stress" and r["verify_ms"] in (1, 3, 6, 7.5, 10)]
    stress_groups = {}
    for row in stress:
        stress_groups.setdefault((row["verify_ms"], row["policy"]), []).append(row)
    stress_summary = [summarize_group(v, ("verify_ms", "policy")) for _, v in sorted(stress_groups.items())]
    write_csv(OUT / "stress_recomputed.csv", stress_summary)

    ablation = [r for r in run_rows if r["family"] == "ablation"]
    ablation_groups = {}
    for row in ablation:
        ablation_groups.setdefault(row["ablation"], []).append(row)
    ablation_summary = [summarize_group(v, ("ablation",)) for _, v in sorted(ablation_groups.items())]
    write_csv(OUT / "ablation_recomputed.csv", ablation_summary)

    paired = [r for r in run_rows if r["family"] == "paired20"]
    paired_groups = {}
    for row in paired:
        paired_groups.setdefault(row["policy"], []).append(row)
    paired_summary = [summarize_group(v, ("policy",)) for _, v in sorted(paired_groups.items())]
    contrasts = []
    by_policy_seed = {(r["policy"], r["seed"]): r for r in paired}
    for treatment, reference in (("calibrated", "fixed"), ("calibrated", "radio"), ("calibrated", "joint"), ("fixed", "joint")):
        common = sorted({s for p, s in by_policy_seed if p == treatment} & {s for p, s in by_policy_seed if p == reference})
        for metric in METRICS:
            deltas = [by_policy_seed[(treatment, s)][metric] - by_policy_seed[(reference, s)][metric] for s in common]
            mean, sd, half = ci(deltas)
            dz = mean / sd if sd else None
            contrasts.append({"contrast": f"{treatment}_minus_{reference}", "metric": metric,
                             "n_pairs": len(common), "mean_delta": mean, "sd_delta": sd,
                             "ci95_half": half, "paired_cohens_dz": dz,
                             "wilcoxon_p": float(stats.wilcoxon(deltas).pvalue) if any(deltas) else 1.0})
    write_csv(OUT / "paired_policy_recomputed.csv", paired_summary)
    write_csv(OUT / "paired_contrasts_recomputed.csv", contrasts)
    write_csv(OUT / "run_summary_records.csv", run_rows)
    payload = {"audit_passed_run_count": len(passed), "stress_runs": len(stress),
               "stress_cells": stress_summary, "ablation_runs": len(ablation),
               "ablation_cells": ablation_summary, "paired_runs": len(paired),
               "paired_policies": paired_summary, "paired_contrasts": contrasts,
               "stress_exclusions": [x for x in audit["failures"] if "/stress_" in x["run"]]}
    (OUT / "results_reconciliation.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps({"stress_runs": len(stress), "stress_cells": len(stress_summary),
                      "ablation_runs": len(ablation), "ablation_cells": len(ablation_summary),
                      "paired_runs": len(paired), "paired_policies": len(paired_summary),
                      "paired_contrasts": len(contrasts)}, indent=2))


if __name__ == "__main__":
    main()
