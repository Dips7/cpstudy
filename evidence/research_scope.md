# Research Scope and Claim Boundaries

**Status:** Phase 1 draft frozen for the current rework; study analyses are classified as exploratory because no dated preregistration or other evidence of a pre-analysis hypothesis/analysis freeze is present in the folder.

## Study purpose

This project is a comparative simulation characterization of sender policies under a controlled common source-update demand. It studies how radio access and a modeled receiver verification queue affect whether source updates become authenticated and fusion-ready before a fixed deadline, and how delayed receiver-load feedback changes that outcome in the implemented scenarios.

The work does not evaluate object detection, perception accuracy, driving decisions, collision avoidance, safety, vehicle deployment, cryptographic correctness, certificate validation, or measured automotive hardware.

## Primary research question

Under common exogenous source-update demand in the implemented simulated system, how does adding delayed receiver-load feedback change timely authenticated source-update availability relative to fixed transmission and radio-only rate control?

## Supporting research questions

### RQ1 — Load and bottleneck characterization

Across the implemented source counts, synthetic mobility scenarios, and verification service-time settings, how do radio delivery, receiver queue outcomes, and timely source-update availability vary?

**Evidence family:** 180-run factorial campaign for 1 ms and 3 ms verification across two synthetic scenarios and three source counts; separate 3-seed stress sweep for 1, 3, 6, 7.5, and 10 ms at 48 sources. These are separate experiments. The factorial campaign alone does not locate a transition above 3 ms.

### RQ2 — Feedback behavior and trigger attribution

In the tested feedback policies, how often are rate reductions associated with backlog-only, channel-only, or combined trigger conditions, and how do outcome measures vary with controller threshold settings?

**Evidence family:** trigger-attribution outputs and the separate threshold ablation. The saved attribution categories support “backlog-only trigger” counts; they do not by themselves establish that a queue event was isolated, anomalous, or the causal mechanism for a failure.

### RQ3 — Paired comparison at one operating point

At 48 sources, intersection scenario, and 3 ms verification service time, how do fixed, radio, uncalibrated joint, and calibrated-feedback policies compare under the recorded paired-seed design?

**Evidence family:** 20-seed paired study. This comparison includes four policies, not ETSI DCC. The calibration and test analysis are treated as exploratory pending evidence that hypotheses, parameter selection, and statistical procedures were frozen before outcome inspection. Results from this operating point do not establish performance over the broader factorial or stress-sweep domain.

## Primary outcome contract

The manuscript currently calls its primary measure **Timely Opportunity Success Rate (TOSR)**, but the code exposes two different quantities. For consistency with the existing paired-study runner and factorial aggregation, the primary outcome for this rework is provisionally **same-opportunity timely success rate** (opportunity_success_rate). It is a source-update availability measure, not object-level perception success and not a safety metric. The term TOSR should be removed until the authors approve one unambiguous definition.

For an evaluated opportunity o and eligible receiver r:

- The opportunity is a source acquisition time and its fixed deadline, with an exogenous receiver set determined by the scenario’s eligibility geometry.
- For the primary same-opportunity measure, an opportunity-receiver pair succeeds only when the message generated for that opportunity-receiver pair has terminal reason success.
- Separately, the implementation’s deadline freshness measure can credit a later update to an earlier opportunity when acquisition time is at least as recent as the opportunity and fusion readiness is no later than its deadline. A single update may satisfy multiple earlier freshness queries.
- The denominator is the count of evaluated opportunity-receiver pairs. Opportunities excluded because their deadline extends beyond the observation window are not in the denominator.
- The code includes readiness exactly at the deadline, because it uses a right-inclusive search through event times at or before the deadline. The manuscript must use this boundary consistently.
- Suppressed demand remains in the denominator. Radio loss, queue overflow, expiry, and unfinished processing do not count as successes.

The exact-deadline and later-update rules have been checked in cpstudy/metrics.py; Phase 2 traced the receiver and closed-loop terminal paths and replayed 370 saved runs. 360 passed conservation and summary reconciliation. Ten major-revision runs contain incomplete raw traces and cannot support terminal-level claims. Do not retain Proposition 1: the secondary freshness metric allows one later update to satisfy multiple earlier opportunities, while the primary same-opportunity measure uses a different credit rule.

## Experiment status and inference

All existing simulation campaigns are classified as **exploratory** for manuscript inference. The 20-seed paired experiment has more replication at one operating point but is not confirmatory solely by virtue of its seed count. Promote it to confirmatory only if dated records demonstrate that the hypothesis, primary outcome, policy contrasts, exclusion rules, stopping rule, and statistical analysis were fixed before those outcomes were inspected.

The 3-seed factorial and stress results support descriptive comparisons within their tested configurations. They are not broad population estimates. The 5-seed ablation is threshold exploration and must not be used as independent confirmation of a threshold chosen using those same results.

## Terms and claim boundaries

Permitted descriptions, subject to final evidence audit:

- “synthetic simulation,” “controlled scenario,” “modeled verification service time”;
- “timely authenticated source-update availability” or “opportunity freshness”;
- “backlog-only trigger” when reporting the saved trigger category;
- “paired comparison at the tested operating point.”

Do not claim from the current artifacts:

- a novel controller or broad priority over prior work;
- calibrated ECDSA/HSM timing, correct signature validation, VPKI performance, or complete security overhead;
- CPM standards conformance or measured perception payload equivalence;
- validated vehicle mobility, channel propagation, real-world generalization, deployment efficacy, or safety benefit;
- that a sender policy is universally harmful or beneficial;
- a general 66.7% TOSR theorem or empirically measured 100% processor-cycle waste;
- that every backlog-only trigger was an isolated outlier or caused the observed outcome.

## Model boundary to state in the paper

The current study uses controlled synthetic mobility, a configured IEEE 802.11p PHY/MAC and simplified propagation, synthetic payload and processing inputs, one modeled FCFS verification worker with finite waiting capacity, assumed-valid signatures, fixed inference/signing/fusion availability delays, and no shared fusion/GPU worker. It does not model object-level accuracy or physical road safety. Any untested sensitivity dimension must be named rather than implied to be validated.

## Phase 1 exit gate

- The primary question, three supporting questions, outcome, denominator, deadline rule, and campaign mapping are stated above.
- The analyses are conservatively classified as exploratory until pre-analysis timing evidence is found.
- Broad novelty, safety, hardware calibration, and standards-revision claims are excluded.
- Phase 2 remains required to verify the provisional outcome contract against all execution paths before manuscript use.
