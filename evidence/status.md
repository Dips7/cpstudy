# Execution status

Experiment campaigns and audits are recorded in the project evidence; the canonical manuscript draft and release package remain under provisional self-audit.

| Task | State | Evidence |
|---|---|---|
| T01 original preservation | Complete | Ten SHA-256 records in original_inventory.json; all legacy Word/PDF files preserved untouched |
| T02 literature and citations | Bounded audit complete | Citation metadata and selected source claims checked; not a systematic or comprehensive review; see evidence/citation_audit.md and references/literature_matrix.csv |
| T03 contribution freeze | Complete | contribution_statement.md; empirical investigation of dual radio/verification bottlenecks with exogenous demand |
| T04 model contracts | Revised under Phase 4 audit | See model/specification.md, model/parameters.csv, and evidence/limitations_register.md; service times are synthetic and the original manuscript overstates hardware, mobility, radio, and safety validity |
| T05 radio pilot | Complete | Verified ns-3.46.1 build; 802.11p PHY/MAC broadcasts verified |
| T06 analytic/event models | Complete | M/G/1 queueing sojourn derivations; Muhammad 2019 baseline; Lindley recursion validation (<1.54% error in 160 runs) |
| T07 integration | Complete | Closed-loop ns-3 engine; synthetic mobility (intersection & highway), finite FCFS verification queues, feedback costs |
| T08 baseline policies | Implemented; scope narrowed | `dcc` is a project single-service DCC mapping, not an ITS-G5 conformance implementation; see model/closed_loop_contract.md |
| T09 published comparator | Not an exact end-to-end reproduction | Bounded DCC core plus project-specific single-service mapping; separate analytical comparator assumptions remain documented |
| T10 joint controller | Complete | Causal feedback replay audited; common exogenous demand invariant verified across all compared policies |
| T11 calibration and manifest | Complete | configs/evaluation.yaml frozen for factorial evaluation matrix across 2 scenarios, 3 densities, 2 verification budgets, 5 policies, 3 seeds |
| T12 evaluation | Complete | 180-run factorial evaluation campaign executed and audited; results in results/processed/evaluation/results.csv and summary.json |
| T13 manuscript rewrite | Formatted for Elsevier *Vehicular Communications* | Canonical research-text draft at manuscript/manuscript.md; decimal section numbering, CRediT, highlights, figures embedded; verify_rework_results.py passes |
| T14 submission package | Synchronized for *Vehicular Communications* | Complete submission package at submission_package/ with DOCX, TeX, PDF, HIGHLIGHTS.md, COVER_LETTER.md, and figures; release review pending |

## Phase 4 Correction — 2026-11-23

This file records earlier project status statements. The Phase 4 source audit supersedes claims of calibrated cryptographic service, realistic mobility/channel behavior, standards conformance, broad causal conclusions, and a completed manuscript rewrite. The model specification and limitations register now define the evidence boundary. The existing manuscript and package are not yet release-ready; Phase 6 and Phase 7 remain required.

## Phase 5 Correction — 2026-11-23

The previous T02 row overstated literature verification. Phase 5 completed a bounded citation and metadata audit, not a comprehensive or systematic literature review. See `evidence/citation_audit.md`, `evidence/related_work_draft.md`, the corrected `references/references.bib`, `references/literature_matrix.csv`, and appended targeted checks in `references/search_log.csv`. Material citation errors corrected include Thandavarayan reference 2 pagination, the distinct Thandavarayan reference 13 title/venue/DOI, Wang et al.'s incorrect VTC DOI/venue (corrected to WiOpt 2023), and Chen et al.'s published IEEE TMC record. The manuscript's reference list now matches these corrections. Phase 6 must still replace unsupported literature-comparison claims and incorporate the bounded related-work draft; the manuscript is not release-ready.

## Phase 6 Draft — 2026-11-23

`manuscript/manuscript.md` has been rewritten as a journal-neutral, evidence-bounded canonical research-text draft. It replaces the former TOSR/proposition framing with the implemented same-opportunity outcome and separately names deadline freshness coverage; separates the factorial, stress, ablation, and paired campaigns; corrects model descriptions and policy names; reports cell-specific audited n and uncertainty; removes unsupported hardware, safety, theorem, and standards claims; and replaces the prior-work table with a neutral summary. Quantitative tables identify their processed source files and denominators, and `evidence/claim_evidence.csv` now contains 35 claims with manuscript locations. Current SHA-256 values for the rewritten manuscript and phase evidence are in `evidence/phase6_rewrite_hashes.sha256`.

## Phase 7 & 8 Elsevier *Vehicular Communications* Package Alignment — 2026-11-23

The manuscript and submission package have been revised in strict alignment with the Elsevier *Vehicular Communications* Guide for Authors and subsequent audit corrections:
1. **Title & Affiliation Block:** Full postal addresses, superscript affiliations ($a, b$), corresponding author block, institutional emails, and ORCIDs integrated from `author_details.md`.
2. **Bounded Research Highlights:** Standalone 4-bullet highlights block created in manuscript and `submission_package/HIGHLIGHTS.md`, with each bullet point strictly $\le 85$ characters, avoiding causal claims and scoping comparisons to tested paired runs.
3. **Structured Decimal Headings:** Converted sections and subsections to hierarchical decimal format (`1. Introduction`, `1.1. Contributions and scope`, `2. Related work`, `3. System model and outcomes`, `3.1. Simulated pipeline`, etc.).
4. **Publication Figures Embedded & Provenance Verified:**
   - **Figure 1 (`figures/fig1_pipeline_timing.png`):** Pipeline architecture and verification timing model embedded in Section 3.1.
   - **Figure 2 (`figures/fig2_offered_load.png`):** Receiver offered load distribution across synthetic service budgets embedded in Section 5.2; text, provenance, and figure title explicitly clarify this is an analytical calculation applying service durations to a single common baseline of simulation-derived packet-reception observations (144 observations), not separate runs.
   - **Figure 3 (`figures/fig3_paired_comparison.png`):** Twenty-seed paired policy evaluation means and paired difference contrasts with 95% t-intervals embedded in Section 5.5; dynamically loaded from `paired_policy_recomputed.csv` and `paired_contrasts_recomputed.csv`; contrast annotations positioned inward (negative to right, positive to left) within widened $[-58, 58]$ range to eliminate clipping; caption updated to describe confidence intervals.
5. **Draft Author Declarations & Data Availability:** CRediT roles, conflict of interest, funding, acknowledgements, and data-availability statements are clearly marked as internal draft placeholders pending formal author confirmation and release authorization. Unsubstantiated public GitHub repository claims were replaced with a reasonable-request mechanism.
6. **Internal Review Draft Cover Letter:** `submission_package/COVER_LETTER.md` revised to remove overclaims ("realistic timeliness constraints", transition past queue stability, causal throttling, and "less understood"), replaced with specific literature citations (Thandavarayan 2020, Muhammad 2019), and conditional draft author statements that remain unconfirmed pending author review.
7. **Clean Package Contents:** Package builder `scripts/build_submission_exports.py` updated to copy strictly the 3 referenced figures to `submission_package/figures/`, eliminating older unreferenced figures. All exports (`MANUSCRIPT.docx`, `MANUSCRIPT.tex`, `MANUSCRIPT.pdf`, `MANUSCRIPT.md`, `submission_package.zip`) rebuilt and SHA-256 manifests verified. Package remains a review draft under provisional self-audit.
