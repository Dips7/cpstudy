# Full Rework Instructions

## Purpose

Rebuild the manuscript and submission package from verified project evidence. Treat the existing manuscript as source material only. Preserve original experiment outputs and raw records; do not overwrite them to make numbers fit the prose.

The desired outcome is a scientifically defensible, internally consistent, reproducible journal-neutral manuscript. Do not claim deployment validity, vehicle safety benefit, standards compliance, hardware calibration, or novelty beyond what the reworked evidence establishes.

## Governing rules

1. Every quantitative result must trace to a named configuration, run manifest, raw output, analysis script, and denominator.
2. Do not manually edit generated tables or figures. Correct the analysis source and regenerate them.
3. If raw data do not support a claim, remove or narrow the claim. Do not infer missing results.
4. Clearly separate exploratory stress tests, the factorial campaign, paired replications, analytic checks, and software validation.
5. State assumptions where introduced and repeat the highest-impact limits in the abstract, discussion, and conclusion.
6. Keep original source artifacts and historical runs intact. New runs must use new, uniquely named output directories.
7. Do not add author, reviewer, ethics, funding, conflict, or publication-status statements without verification from the authors or source documents.
8. Do not call an analysis systematic, calibrated, validated, realistic, or standards-compliant unless the documented method meets that description.

## Phase 0 — Preserve and inventory

### Tasks

- Record the current Git/status state and hashes of source manuscript, package exports, configurations, code, scripts, and results.
- Inventory all experiment families and distinguish raw outputs from derived summaries.
- Locate the exact source and transformation path for every manuscript table, figure, and headline number.
- Check whether actual editor/reviewer comments exist before keeping a response-to-reviewers document.
- Record missing inputs rather than filling gaps from memory.

### Deliverables

- evidence/rework_inventory.md: file, role, provenance, status, and preserve/regenerate decision.
- evidence/run_catalog.csv: run family, question, configuration/hash, policies, seeds, scenario, outputs, and limitations.
- evidence/claim_evidence.csv: expanded to include every manuscript claim, source locator, denominator, calculation, and disposition.

### Exit gate

No result family is described as part of another campaign unless its run records show identical protocol and configuration. No original raw result is changed.

## Phase 1 — Freeze the research question and scope

Use the conservative framing in evidence/contribution_statement.md as the starting point. The core question is whether delayed receiver-load feedback changes timely authenticated update availability under common exogenous demand in this particular simulated system.

### Tasks

- Write one primary research question and at most three supporting questions.
- Identify primary outcome, its unit of analysis, numerator, denominator, eligibility geometry, censoring rule, and deadline boundary.
- Identify which campaign answers each question: 180-run factorial study; 3-seed verification stress sweep; 5-seed policy-threshold ablation; 20-seed paired comparison; analytical queue checks and software tests.
- Designate confirmatory versus exploratory work based on when each question and analysis were selected. If that timing cannot be established, label the analyses exploratory.
- Remove the claim that the controller is a novel algorithm unless a complete prior-art review supports it.
- Do not make deployment, safety, or standard-revision recommendations from simulation-only outcomes.

### Deliverables

- evidence/research_scope.md: frozen scope, questions, outcomes, and claim boundaries.
- Revised contribution statement accurately describing the study as a characterization/comparative extension if supported.

### Exit gate

An independent reader can tell what the study tests, what it does not test, and which data answer each question.

## Phase 2 — Audit outcome definitions and implementation

### Tasks

- Read metrics.py, engine.py, closed_loop.py, network_audit.py, and relevant tests.
- Map implementation states and event timestamps to the manuscript’s definitions of opportunity, source update, receipt, verification, fusion readiness, freshness, suppression, loss, expiry, and censoring.
- Resolve whether an opportunity can be satisfied by a later update; implement or document the exact rule.
- Resolve deadline equality (< versus <=) and half-open versus closed intervals consistently.
- Verify whether one delivered update can satisfy multiple opportunities in the code. Do not assume the answer from periodic timing alone.
- Reconcile the terminal-state partition with generated message-receiver pairs and opportunity-receiver pairs; those are different populations and must not be conflated.
- Recompute all conservation identities from raw logs and retain a machine-readable audit.
- Remove Proposition 1 unless its assumptions and proof match implementation exactly. A tested metric contract is preferable to an unnecessary theorem.

### Deliverables

- model/outcome_contract.md: formal definitions, timestamps, boundaries, units, censoring, terminal states, and denominators.
- Added/updated tests for each definition and boundary.
- evidence/outcome_audit.json and a readable audit summary.

### Exit gate

Every outcome in prose, tables, and code has one unambiguous operational definition, and automated audits verify the mapping.

## Phase 3 — Reconcile experiments and statistics

For every experiment family, record purpose and exploratory/confirmatory status; source revision and simulator binary hash; config and hash; policy definitions; scenario, source count, service budget, duration, warm-up, and seeds; independent-run count and pairing design; raw and processed output locations; exclusions, failures, reruns, and stopping decisions.

### Specific reconciliation

- Recompute the utilization audit from underlying receiver-level observations. Resolve the Table 2 discrepancy, including inconsistent values across service-time rows. Show the aggregation over nodes and seeds.
- Recompute Tables 4–6 from raw stress, ablation, and paired records. Label seed counts and avoid presenting them as one experiment.
- Confirm the 20-seed analysis contains only fixed, radio, joint, and calibrated policies. Do not imply ETSI DCC was included in these paired tests.
- Identify whether “radio-only DCC” means the project’s radio policy or ETSI dcc. Use distinct names everywhere.
- Recalculate all percentages, confidence intervals, paired differences, test statistics, and p-values using one documented analysis script.
- Verify assumptions for paired tests and report paired seed-level differences. Avoid p-value emphasis when effect size and uncertainty are more informative.
- Report n and uncertainty for the 3-seed factorial conditions. Show individual seed outcomes where useful; do not imply broad population generality.
- Use consistent rounding and units. Keep full precision in machine-readable outputs.
- Reproduce figures from audited datasets, with source data and scripts retained.

### Deliverables

- evidence/run_catalog.csv and completed evidence/claim_evidence.csv.
- One documented analysis pipeline with named outputs.
- Regenerated processed tables and figures, each with provenance sidecars.
- evidence/results_reconciliation.md listing every changed, removed, or retained result and why.

### Exit gate

All numbers in the manuscript can be regenerated from preserved raw outputs. There are no unexplained differences between tables, summaries, and claims.

## Phase 4 — Audit model assumptions and causal interpretations

### Verification and cryptography

- Describe the implementation as a configurable verification service-time model. The code assumes valid signatures; it does not implement ECDSA, certificate validation, a VPKI, or a measured HSM.
- Call service-time values synthetic unless a properly scoped benchmark and hardware/software provenance are added.
- Separate cryptographic verification time from certificate-chain validation, queueing, and other security costs.
- Remove claims that an ECU or standard mandates the exact modeled behavior unless an authoritative source establishes it.

### Radio, mobility, and traffic

- Describe the ns-3 model exactly: controlled synthetic mobility, IEEE 802.11p PHY/MAC setup, propagation assumptions, interference, no building blockage/NLOS, and omitted traffic or channel effects.
- Do not call it a realistic deployment scenario absent calibration against measured mobility/channel traces.
- Distinguish the 802.11p test setup from current deployment recommendations.
- Describe object/perception payloads as synthetic fixtures unless generated by an encoder conforming to a pinned CPM specification.
- Distinguish broadcast airtime from per-receiver packet/verification arrival load.

### Queueing and feedback interpretation

- State that one FCFS verification worker is modeled, with no shared fusion/GPU queue and no valid-signature failures.
- Explain that finite queues can stay bounded by dropping work and that stability does not imply deadline reliability.
- State arrival-process and service assumptions; do not apply M/G/1 formulas as validated predictions for non-Poisson synthetic traffic without checking assumptions.
- The claimed 100% wasted CPU behavior requires direct instrumentation of service intervals spent on already-expired messages. If not instrumented, remove the empirical statement.
- The claimed 66.7% TOSR limit must either be removed or restated as a conditional arithmetic bound with explicit equal-reception, capacity-allocation, demand-credit, loss, and scheduling assumptions. Do not call it a general theorem.
- Use “backlog-only trigger” when that is all the attribution output supports. Do not say “isolated outlier” unless receiver-level traces establish isolation and the calculation is supplied.
- Report suppression with a declared numerator and denominator. Do not call modeled update opportunities “safety updates.”

### Sensitivity work

Before making claims beyond the fixture, evaluate sensitivity to verification service budget and variability; queue capacity and worker count; radio range, propagation, blockage, and packet size; feedback rate, delay, loss, staleness, and overhead; opportunity rate, deadline, and density; inference, signing, and fusion delay.

If resources prevent these experiments, narrow conclusions and list the untested dimensions.

### Deliverables

- Revised model/specification.md, parameter/provenance table, and limitations register.
- Reproducible sensitivity analysis or explicitly narrowed scope.
- Claim-to-evidence decisions for all causal statements.

### Exit gate

Every causal explanation is directly instrumented, analytically derived under stated assumptions, or labeled as a hypothesis.

## Phase 5 — Complete and accurately describe related work

### Tasks

- Reconcile each citation in the manuscript with references.bib and the literature matrix.
- Verify bibliographic metadata, version/date, DOI or stable locator, and the exact proposition supported by each citation.
- Inspect full texts of closest related works where lawful and available. Keep preview-only/abstract-only status explicit for anything not fully inspected.
- Do not claim “systematic review” unless databases, search terms, date, inclusion/exclusion rules, screening, and citation chasing are documented.
- Compare only method details actually observed in source papers.
- Do not claim novelty based solely on combining queues, adding feedback, or including AoI/freshness.

### Deliverables

- Updated literature_matrix.csv, search_log.csv, and references.bib.
- Concise related-work section focused on closest methods and defensible difference.

### Exit gate

No unsupported negative statement about prior work remains, and every citation has been checked against its source.

## Phase 6 — Rewrite the scientific manuscript

Use one canonical editable source. Recommended structure: title and abstract; introduction and bounded contributions; related work; system model and assumptions; outcome definitions and experiment design; implementation and reproducibility; results separated by campaign; discussion and validity boundary; limitations; conclusion; verified author statements and references.

### Writing rules

- The abstract must identify this as a simulation study and state tested scenario, key assumptions, primary result, and major limitation.
- Use one canonical name for each policy. Distinguish radio from ETSI dcc.
- State sample size beside each result.
- Separate simulation outcomes from calculations and interpretation.
- Avoid “proves,” “fundamentally,” “strictly,” “mandates,” “safety-critical,” “calibrated,” “validated,” and “100%” unless justified.
- Do not claim any sender controller is universally wrong. Scope conclusions to tested configurations.
- Do not recommend changing future standards based on this evidence.
- Name synthetic service times, payloads, mobility, propagation, single-worker processing, assumed-valid signatures, absent shared fusion queue, finite scenarios, and replication limits in the limitations section.
- Keep conclusions proportional to tested outcomes and state what experiment would change the conclusion.

### Exit gate

The manuscript can be read without opening the submission package to discover contradictory interpretations or hidden assumptions.

## Phase 7 — Rebuild submission materials

### Canonical source and exports

- Select one manuscript source as canonical. Generate DOCX, PDF, and LaTeX from it or document necessary format-specific transformations.
- Recreate figures and tables from audited analysis outputs.
- Confirm equations render, citations resolve, tables fit, captions match included images, and page elements fit the chosen format.
- Render DOCX/PDF pages and visually inspect every page, including tables, references, equations, and figure placement. Fix layout defects and repeat inspection.
- Check LaTeX compilation in a clean environment if included.

### Package contents

- Rewrite the package README to inventory actual files, build steps, versions, and limitations.
- Remove the response-to-reviewers document unless authentic reviewer comments and decision letter are supplied. If retained, quote comments accurately and link each response to a verifiable manuscript change.
- Keep a journal-neutral cover-letter draft until journal selection. Address one journal only and use the actual submission date.
- Verify highlights against journal limits only after journal selection.
- Verify author details, affiliations, contribution roles, funding, competing interests, ethics statements, corresponding-author designation, and code/data availability with authors.
- Do not publish personal contact information beyond what authors authorize.
- Rebuild the ZIP from the final package directory and inspect its contents and checksums.

### Exit gate

All exported files represent the same approved manuscript version, and the ZIP has no stale, contradictory, or unsupported material.

## Phase 8 — Independent release review

Have a reviewer who did not perform the analysis select every abstract result and table value; trace each to raw records; independently recalculate at least one result per experiment family; verify denominator, seeds, uncertainty, and policy label; inspect definitions and terminal-state audit; compare manuscript, DOCX, PDF, LaTeX, README, letter, and ZIP; and confirm limitations are not contradicted by promotional language.

### Final release checklist

- [ ] No unresolved numeric discrepancies.
- [ ] Every claim has a source, calculation, denominator, and disposition.
- [ ] Every result family and replication count is named accurately.
- [ ] No unsupported theorem, causal statement, novelty claim, hardware calibration, safety claim, or standards recommendation remains.
- [ ] Methods and model limitations are visible in the paper.
- [ ] References and standards versions are verified.
- [ ] Author statements have been confirmed by authors.
- [ ] DOCX/PDF pages have been rendered and visually checked.
- [ ] LaTeX compiles if included.
- [ ] ZIP contents and checksums match the final directory.
- [ ] README and evidence status distinguish code verification from scientific validity and submission readiness.
- [ ] All authors have reviewed the final manuscript and approved submission.

## Expected final artifacts

- One explicitly named canonical manuscript source.
- evidence/rework_inventory.md, evidence/run_catalog.csv, evidence/claim_evidence.csv, evidence/results_reconciliation.md.
- model/outcome_contract.md and updated model parameter/provenance files.
- Audited tables, figures, raw-to-summary analysis code, and provenance sidecars.
- Final, visually checked DOCX and PDF; LaTeX only if required.
- Corrected package README, verified author statements, journal-specific cover letter only after journal selection, regenerated ZIP, and final release audit.

## Completion standard

The rework is complete only when the manuscript and all submission artifacts are internally consistent, quantitative claims reproduce from preserved data, definitions match code, limitations are explicit, exports pass visual/technical inspection, and all authors approve the final version. A passing test suite alone does not establish scientific validity or submission readiness.
