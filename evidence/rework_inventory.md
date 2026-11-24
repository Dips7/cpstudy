# Rework Inventory

Snapshot date: 2026-11-23.

## Repository and preservation state

- git -C cpstudy status --short --branch exited 128 with “not a git repository.” The folder contains no usable Git worktree metadata, so a commit or clean/dirty status cannot be recorded.
- Historical files under results/raw/ are preserve-only. This Phase 0 work did not modify those outputs or the manuscript exports.
- The expanded 24-claim ledger is now canonical at evidence/claim_evidence.csv. The prior file was preserved as evidence/claim_evidence_original.csv; evidence/claim_evidence_phase0.csv remains a duplicate working snapshot.
- evidence/rework_hashes.sha256 contains a file-by-file baseline for 4,178 files. The hash-list file excludes its own hash to avoid a self-referential checksum. Regenerate the list after any further Phase 0 edits.

## Primary artifact inventory

| Path | Role | Phase 0 handling |
|---|---|---|
| manuscript/manuscript.md | Working manuscript source | Preserve; scientific rewrite only after evidence audit |
| submission_package/MANUSCRIPT.md | Packaged markdown export | Preserve as historical; regenerate from canonical source later |
| submission_package/MANUSCRIPT.docx, .pdf, .tex | Submission exports | Preserve as historical; compare/rebuild in Phase 7 |
| submission_package.zip | Packaged submission archive | Preserve as historical; regenerate after final release review |
| configs/evaluation.yaml | Factorial design | Preserve and hash in run catalog |
| results/raw/evaluation/campaign_manifest.json | Factorial run-level manifest | Preserve; primary source for 180-run campaign |
| results/processed/evaluation/results.csv, summary.json, paired_differences.csv | Derived factorial summaries | Preserve as historical; independently recompute before use |
| results/raw/major_revision/*.json | Stress, DCC, utilization, attribution, and ablation summaries | Preserve; reconcile with raw run records and manuscript |
| results/raw/paired_intersection_n48_v30/paired_summary.json | 20-seed paired summary | Preserve; audit against run-level records |
| results/raw/closed-loop-checks3/ | Small common-demand/integration checks | Preserve; software evidence, not efficacy evidence |
| results/raw/queue-validation/ and results/processed/queue-validation/ | Queue-model validation fixtures | Preserve; internal validation evidence |
| scripts/ | Simulation and analysis source | Preserve; map scripts to result families |
| cpstudy/, simulator/, tests/ | Implementation and tests | Preserve; later audit metric behavior and provenance |
| model/specification.md, model/closed_loop_contract.md, model/parameters.csv | Model assumptions and parameter provenance | Preserve; authoritative limits for claim audit |
| evidence/claim_evidence.csv | Canonical expanded claim ledger (24 manuscript claims) | Working register; dispositions remain provisional pending later phases |
| evidence/claim_evidence_original.csv | Previous claim register snapshot | Preserve as historical archive |
| evidence/contribution_statement.md, status.md, logs | Research positioning and execution evidence | Preserve; reconcile status contradictions |
| references/ | Bibliography, search records, literature matrix, full-text copies | Preserve; citation and prior-art audit in Phase 5 |
| figures/ and submission_package/figures/ | Project and packaged figures | Preserve; identify generation source and regenerate after results audit |
| Autonomous Vehicles, Immersive Realities and Intelligent IoT/ | Original source materials and legacy drafts | Preserve; consult for provenance, not validated evidence |

## Known output families

See evidence/run_catalog.csv. The principal families are the 180-run factorial campaign, verification stress sweep, threshold ablation, 20-seed paired study, queue validation, closed-loop integration checks, and pilot/reproduction fixtures. They are not one pooled campaign.

## Open inventory items

1. Link each experiment family to exact script revision, simulator binary hash, and per-run manifest/config hashes.
2. Inspect package binaries and source exports for version identity after the scientific claim audit.
3. Locate authentic editorial/reviewer decision materials or omit the purported round-two rebuttal from the clean package. See evidence/reviewer_materials_provenance.md.
4. Complete run-level script/configuration/executable hash linkage; current table/figure mapping is in evidence/table_figure_provenance.md.
