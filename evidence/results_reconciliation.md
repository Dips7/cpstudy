# Phase 3 Results Reconciliation

Updated: 2026-11-23. This reconciliation uses the preserved per-run `summary.json` records, the receiver event traces, and the independent run-level terminal audit. Analysis outputs are written under `results/processed/rework/`; no historical raw run or aggregate was overwritten.

## Audit scope and exclusions

The corrected corpus discovery found 370 run directories: 180 factorial, 80 paired, and 110 major-revision. Of these, 360 pass terminal conservation and match their saved summary counts (180, 80, and 100 by family). Ten major-revision stress runs have damaged raw traces. Their summary files remain preserved but are not included in the trace-supported stress aggregates. The complete list and error types are in `outcome_audit_summary.md` and `outcome_audit.json`.

The 75-run stress design comprised five verification budgets (1, 3, 6, 7.5, and 10 ms), five project policies, and three seeds. Sixty-five runs passed trace audit. Thus some stress cells have only one or two verified seeds; their means are descriptive, and t intervals are extremely wide for small n. An empty interval for n=1 is not evidence of certainty. The 35-run threshold ablation (seven conditions x five seeds) and the 80-run paired study are fully audited.

## Table 2: receiver offered load

The original receiver-utilization audit counted receptions over the full 5 s simulation and divided by the 4 s active interval, inflating arrival rates by 25%. Its retained output also did not establish actual worker busy time. The replacement `scripts/recompute_utilization.py` counts data receptions (`kind=0`) during `[1 s, 5 s)`, divides by the 4 s observation interval, and explicitly includes all 48 receivers for each of three seeds. It reports offered load, `rho = lambda * configured mean verification service time`; this is a queueing input estimate, not measured processor utilization.

The available fixed-policy reception traces were compared across service-time folders and were identical where present. For the 3 ms condition, the seed 1 and 3 trace folders were unavailable or truncated, so the matching baseline fixed-policy traces were reused; seed 2 was directly available and identical. The fixed policy does not adapt its source rate to receiver load. The source comparisons and method are recorded in `utilization_recomputed.json`.

| Configured service (ms) | Mean arrivals (packets/s/receiver) | Mean offered rho | Median rho | Max rho | Mean receivers/run with rho > 1 |
|---:|---:|---:|---:|---:|---:|
| 1.0 | 190.422 | 0.1904 | 0.2181 | 0.3038 | 0.00 |
| 3.0 | 190.422 | 0.5713 | 0.6544 | 0.9113 | 0.00 |
| 6.0 | 190.422 | 1.1425 | 1.3088 | 1.8225 | 29.67 |
| 7.5 | 190.422 | 1.4282 | 1.6359 | 2.2781 | 32.67 |
| 10.0 | 190.422 | 1.9042 | 2.1813 | 3.0375 | 38.00 |

The manuscript's former 3 ms row (mean 0.71, max 1.13, and receivers above one) is contradicted. The saved prior audit's 3 ms rho values were also inflated by its observation-window mismatch. The updated result places all measured offered loads below one at 3 ms and shows the transition to average offered load above one at 6 ms. This does not by itself establish queue stability, deadline success, or CPU utilization.

## Tables 4 and 5: stress and threshold ablation

`scripts/reconcile_results.py` re-aggregates each audited run's saved opportunity-success/freshness rates, success-conditioned latency, and terminal counts. The full estimates, standard deviations, 95% t-interval half-widths, and per-cell audited sample sizes are in `stress_recomputed.csv` and `ablation_recomputed.csv`. `run_summary_records.csv` preserves the run-level values feeding those aggregates.

Key corrections:

- The audited 3 ms calibrated stress cell has n=2, mean opportunity success 53.04% (95% t interval half-width 13.49 percentage points), not a verified three-seed estimate of 53.90%.
- At 6 ms, calibrated has n=1 (3.54%; no estimable interval) and joint has n=2 (2.74%; half-width 13.60 percentage points). These are incomplete exploratory observations, not valid three-seed cell comparisons.
- The 6 ms DCC-labeled policy has n=3 and mean success 43.26% (interval half-width 4.53 percentage points).
- All seven ablation cells have n=5 and pass audit. The Q-high 16 mean remains 55.31%; its recomputed 95% t interval half-width is 3.80 percentage points. The five-seed result is an exploratory threshold comparison, not independent validation of an optimal controller.

Policy labels are kept distinct. `radio` is the project's internal channel-busy-rate controller. `dcc` is the project's research single-service DCC mapping (`cpstudy/dcc.py` explicitly says it is not an ITS-G5 conformance implementation). It may be described as a DCC-inspired project comparator, not as standards-conformant ETSI DCC. The 20-seed paired design contains fixed, radio, joint, and calibrated policies; it contains no DCC comparator.

## Table 6: paired 20-seed comparison

All 80 paired run records pass terminal audit. Recomputed policy means and 95% t intervals over seed-level results are in `paired_policy_recomputed.csv`; paired deltas, intervals, Cohen's dz, and Wilcoxon p values are in `paired_contrasts_recomputed.csv`. The calibrated-minus-joint timely opportunity success difference is +40.07 percentage points (95% paired t interval half-width 4.18 points; dz=4.49). Calibrated remains below fixed by 38.83 points and below radio by 26.07 points at this specific simulated operating point. These estimates do not establish performance outside the tested configuration.

The saved paired aggregate's policy means and intervals agree with recomputation from the per-run records to rounding precision. Inference is reported through effect estimates and intervals; p values remain supplementary, and the original table's emphasis on a tiny p value is not needed to convey the result. The paired experiment is still exploratory because the repository does not contain dated pre-analysis registration showing that this exact comparison was selected independently of outcomes.

## Disposition and remaining limits

- Retain the 180-run factorial as its separate exploratory campaign; all 180 pass audit.
- Retain the paired 20-seed records as a distinct, fully audited study at one operating point.
- Retain the threshold ablation descriptively; all 35 records pass audit.
- Replace the utilization calculation and all derived Table 2 claims with offered-load estimates above.
- Do not present damaged stress-cell summaries as complete three-seed terminal-verified results. Preserve them, report verified n, or omit comparisons whose denominator is inadequate.
- Do not infer measured CPU busy fraction, cryptographic hardware throughput, physical safety, real-world efficacy, or standards conformance from these simulations.
- The preserved major-revision per-run summaries do not contain a source revision, full configuration snapshot/hash, or simulator binary hash. The run catalog records the script and design visible in the surviving folder structure, but these historical provenance fields cannot be reconstructed reliably from current code alone. This is an unresolved Phase 3 release-gate item; do not represent the major-revision results as fully config-hash lineage-complete.

## Reproduction

From the `cpstudy` directory, run `python3 scripts/recompute_utilization.py` and `python3 scripts/reconcile_results.py`. The outcome audit is regenerated with `python3 scripts/audit_outcome_corpus.py --output evidence/outcome_audit.json`. All three commands read historical source records and write audit/analysis products only to their designated evidence or processed-output locations.
