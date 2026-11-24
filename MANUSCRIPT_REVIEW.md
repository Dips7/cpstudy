# Full Manuscript and Folder Review

**Manuscript:** “Clear Airwaves, Clogged Computers: The Dual Bottleneck of Radio Contention and Receiver Verification in Cooperative Vehicle Perception”  
**Review date:** 23 November 2026  
**Scope:** Project folder, source manuscript, submission package, experiment outputs, code/model specifications, evidence logs, figures, and references.

## Editorial assessment

**Recommendation: major revision; do not submit the current package.**

The folder contains substantial useful research infrastructure: a reproducible ns-3 experiment harness, configuration and provenance artifacts, raw and processed outputs, tests, and a manuscript that acknowledges synthetic inputs and several limits. The strongest defensible contribution is a controlled comparative characterization of a particular receiver-feedback controller under a synthetic mobility/radio/verification model. The current manuscript overstates what this implementation establishes, mixes result sets, and presents several claims as measured or proven when the underlying artifacts do not support them.

The local cpstudy README and evidence/contribution_statement.md are more cautious than the submission materials. They identify synthetic service/payload inputs, no validated fusion or safety outcome, no certificate stack, and a journal-neutral study. The manuscript and cover letter should be brought back into alignment with those evidence boundaries.

## Major findings

### 1. Result sets and policy labels are mixed

The headline manuscript combines at least three distinct experiment sets:

- The 180-run factorial campaign has 3 replications per condition and evaluates fixed, radio, receiver, joint, and dcc in two scenarios at 12/24/48 sources and 1/3 ms verification. It has no calibrated policy.
- The major-revision stress sweep has 3 seeds and includes the uncalibrated joint and calibrated policies.
- The paired 20-seed study includes only fixed, radio, joint, and calibrated, at 48 sources/3 ms/intersection.

The paper’s headline 94.75%, 81.98%, 55.91%, and 15.84% values are from the 20-seed result, whereas other tables use 3- or 5-seed runs. That can be legitimate if every result is clearly sourced and the methods explain why separate campaigns were run, but the current text calls these a single replication campaign and does not give a coherent study hierarchy. Tie every claim/table to run IDs and configuration hashes and state its experiment set.

### 2. The receiver utilization table conflicts with saved evidence

The manuscript’s Table 2 reports at 3 ms: mean arrival rate 237.0 packets/s, mean utilization 0.71, median 0.81, maximum 1.13, and 1.3 of 48 receivers over saturation. The persisted results/raw/major_revision/utilization_audit.json reports at 3 ms: mean 222.04 packets/s, mean utilization 0.666, median 0.655, maximum 0.964, and zero nodes over 1.0. It separately reports 237.02 packets/s and mean utilization 0.237 at 1 ms. Thus the paper appears to have mixed aggregation/seed summaries across rows. Recompute Table 2 from its raw audit input, specify node/seed aggregation, and regenerate the table and claims.

### 3. Claims exceed the executable model or evidence

- The manuscript and cover letter call verification “calibrated ECDSA,” cite automotive HSM costs, and describe signatures as mandated. The model contract says all signatures are assumed valid and verification is represented only as configurable processing delay. model/parameters.csv labels service values synthetic and says provenance is needed. Rephrase as a synthetic signature-verification service budget unless a scoped benchmark is supplied.
- The manuscript uses safety-critical language and makes recommendations for standards and ECU firmware. No perception accuracy, validated operational deadline, physical safety endpoint, HSM workload, or real vehicles are evaluated. Frame conclusions as simulation findings.
- The cover letter and rebuttal claim dead-packet head-of-line blocking wastes 100% of processor cycles authenticating expired frames. No evidence artifact measures the share of worker cycles spent on expired packets. The calculation 32 × 6 ms = 192 ms assumes a full queue and does not prove all cycles are wasted across a run. Instrument this mechanism or present it only as a conditional illustration.
- The manuscript claims a 66.7% TOSR theorem from 166.7 frames/s divided by 25 senders. This assumes equal reception by 25 receivers, one useful update per demand, no loss, and a relation between aggregate service capacity and per-source opportunity credit. These assumptions do not follow from the model’s geometry-based receiver sets. Replace it with a conditional bound and explicit assumptions, or remove it.
- Proposition 1 assumes the success metric credits only the message generated for the same opportunity, but the TOSR definition allows a newer message to satisfy an earlier opportunity. The proof uses a half-open deadline interval while the success inequality permits equality at the deadline. Align definition, boundary, proof, and actual implementation in cpstudy/metrics.py.
- The abstract says 93.4% of cuts are caused by “isolated” neighbor bursts and that 86.2% of safety updates are suppressed. The attribution output establishes 93.38% backlog-only triggers, not that they were isolated; the JSON does not establish 86.2% suppression. Supply the matching trace calculation and denominator or narrow the wording.

### 4. Literature and novelty framing are not supportable yet

references/literature_matrix.csv marks recent close studies as preview/abstract-only and lists missing full-paper review. evidence/contribution_statement.md says broad novelty is not established and recommends treating the controller as a diagnostic policy. The manuscript’s “systematic literature comparison,” categorical claims about prior work, “fully public” reproducibility language, and cover letter’s “high-impact” framing do not match that status. Remove “systematic” unless a reproducible search protocol exists; qualify entries where full texts were not inspected; avoid claims about prior work without reviewing the full text.

### 5. Package and export defects need a clean rebuild

- submission_package/README.md calls this a “Round 2 Major Revision,” claims a response to 12 reviewer comments, and says the manuscript is ready for multiple journal formats. The folder contains no reviewer decision letter or actual reviewer reports. Do not represent the rebuttal as authentic unless those source comments exist and match.
- The cover letter is addressed simultaneously to IEEE T-ITS and IEEE TVT and dated 17 October 2026, while the package is not journal-specific. Prepare a journal-neutral draft and a single-journal letter only after journal selection and author approval.
- MANUSCRIPT.pdf, .docx, .tex, and .md are separate artifacts. Rebuild all exports from one canonical source after scientific corrections; render and inspect final pages, tables, equations, references, and figure captions.
- The manuscript’s reference list needs citation, DOI, standard-version, and claim-level auditing against REFERENCES.bib.
- Regenerate submission_package.zip only after the package contents and claims are corrected.

### 6. Methods and statistical reporting need tightening

- configs/evaluation.yaml supports only 1 and 3 ms verification, while the stress sweep covers 1, 3, 6, 7.5, and 10 ms. Explain the distinct designs and identify exploratory outputs.
- The factorial campaign uses 3 replications per condition. Show per-seed outcomes or uncertainty intervals and limit generality claims. The 20-seed experiment is one scenario, density, and service budget; it does not validate the broad stress-sweep conclusions.
- Paired tests compare fixed, radio, joint, and calibrated only; ETSI DCC is absent. Do not imply DCC is part of the 20-seed tests.
- The ns-3 model is controlled synthetic mobility with log-distance propagation and no buildings/NLOS or SUMO calibration. State this prominently and avoid “realistic” or safety claims.
- The model uses synthetic payloads, fixed inference/signing/fusion delays, one verification worker, assumed-valid signatures, and no shared fusion queue. Present these as assumptions and add sensitivity analysis before claiming applicability.
- The project README is stale and contradictory: its opening says research is in progress/no rewritten manuscript, while later sections say the campaign and paper are complete. Update it to distinguish implementation checks from scientific validity and submission readiness.

## Strengths worth preserving

- The study asks a useful, testable question about whether delayed receiver feedback can harm timely update availability.
- Exogenous demand accounting and the common-demand audit are stronger than evaluating success only among emitted packets.
- Evidence includes source/build provenance, regression notes, queue audits, and a clean-environment test log reporting 18 tests passed.
- The closed-loop contract candidly documents synthetic mobility, no fusion worker, assumed-valid signatures, stale feedback behavior, and limits of the ETSI DCC comparison.
- The negative result that queue-aware feedback can perform worse than fixed transmission is useful when scoped to the tested model.

## Revision plan

1. Freeze one canonical set of outputs and create a claim-to-artifact table mapping each numerical statement to a run manifest, raw file, analysis script, and denominator.
2. Recompute and reconcile Tables 2–6 from raw outputs. Resolve 3/5/20-seed differences, label exploratory and confirmatory analyses, and report uncertainty consistently.
3. Audit definitions in metrics.py against manuscript TOSR/proposition and terminal outcomes; repair the proof or remove it.
4. Remove or downgrade claims unsupported by measurement: calibrated ECDSA, “100% wasted” CPU, 66.7% theorem, isolated-trigger mechanism, safety/standards prescriptions, and broad novelty/systematic-review claims.
5. Strengthen parameter provenance and sensitivity analysis for verification, payload, feedback, radio propagation, receiver queue capacity, and deadline.
6. Rewrite abstract, contributions, discussion, limitations, and conclusion to describe an exploratory simulation study and its actual validity domain.
7. Have all authors verify names, affiliations, contributions, funding, competing interests, corresponding author, and publication status. Keep personal contact details out of public artifacts unless authors authorize them.
8. Rebuild DOCX/PDF/LaTeX and figures from the corrected source, perform visual QA, validate references, regenerate the ZIP, and write a package README that describes actual contents without claiming an unsupported review round.

## Checks performed

- Inspected folder README, rebuild plan, evidence/status notes, contribution statement, claim-evidence CSV, model contracts, parameters, configs, processed results, raw utilization/stress/ablation/paired outputs, scripts, test logs, figure inventory, references matrix, and submission materials.
- Confirmed manuscript/manuscript.md and submission_package/MANUSCRIPT.md have identical character counts and diff output.
- Confirmed the saved test log reports 18 tests passing and closed-loop evidence reports 10 audited runs passing.
- Compared headline claims against paired_summary.json, stress sweep output, and utilization audit. These are folder-level review checks, not a fresh rerun of experiments or independent verification of external references.

## Overall readiness

The research code and artifacts are promising but not independently validated as a deployment model. The current manuscript is not scientifically or editorially submission-ready. Resolve numeric contradictions and scope claims first; then rebuild the submission exports and journal-specific materials.
