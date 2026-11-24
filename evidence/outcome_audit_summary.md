# Outcome Audit Summary

## Result

The independent replay audited 370 preserved run directories across the factorial, paired, and major-revision output families. The initial discovery pass missed six major-revision directories because they had uncompressed opportunity CSVs; corpus discovery now enumerates run directories from their summary records and supports both CSV encodings.

- 360 runs passed generated-pair terminal conservation and matched summary.json counts exactly, including suppressed demand.
- 10 runs could not be validated because their preserved raw traces are incomplete.
- Raw run files were not changed. The complete machine-readable record is evidence/outcome_audit.json.

| Family | Passing runs |
|---|---:|
| Factorial campaign | 180 |
| 20-seed paired study | 80 |
| Major-revision outputs | 100 |

## Incomplete preserved runs

1. results/raw/major_revision/stress_v30_calibrated_s3 — opportunity CSV ends in an incomplete row.
2. results/raw/major_revision/stress_v30_fixed_s1 — normalized event stream ends before its gzip end marker.
3. results/raw/major_revision/stress_v30_fixed_s3 — normalized event stream ends before its gzip end marker.
4. results/raw/major_revision/stress_v60_calibrated_s1 — normalized event stream ends before its gzip end marker.
5. results/raw/major_revision/stress_v60_calibrated_s3 — opportunity CSV ends in an incomplete row.
6. results/raw/major_revision/stress_v60_fixed_s1 — opportunity CSV ends in an incomplete row.
7. results/raw/major_revision/stress_v60_joint_s3 — 3,872 generated pairs have no normalized terminal record.
8. results/raw/major_revision/stress_v60_radio_s2 — normalized event stream ends before its gzip end marker.
9. results/raw/major_revision/stress_v60_radio_s3 — normalized event stream ends before its gzip end marker.
10. results/raw/major_revision/stress_v75_radio_s3 — normalized event stream ends before its gzip end marker.

These errors mean the corresponding stress-sweep summaries are not independently reconstructable from the surviving trace files. Preserve the artifacts and exclude those runs from claims that require terminal-level audit unless another complete, provenance-matched source is found. Do not silently rerun into these historical directories or replace their records.

## Interpretation

For the 360 complete runs, each emitted eligible message-receiver pair has exactly one terminal state, and the evaluated demand partition is:

evaluated demand pairs = suppressed pairs + generated evaluated pairs

generated evaluated pairs = terminal reasons for those pairs

The summary comparison includes the summary’s suppressed count separately from generated-pair terminal reasons. The audit does not assert one-to-one freshness credit: the secondary deadline-freshness measure may let one later update cover multiple earlier opportunities.

## Verification limits

- The focused tests for deadline equality, multi-opportunity freshness credit, and outcome audit passed: 7 passed under system Python 3.9.
- The full project suite could not be collected under that interpreter because the project requires Python >=3.12 and its local .venv is absent in this checkout. The recorded project clean-environment log remains historical evidence, not a rerun in this session.
- The replay validates saved accounting records. It does not validate cryptographic correctness, simulator fidelity, or physical deployment behavior.
