# Cooperative Perception Manuscript Rebuild Plan

Implementation plan completed 16 October 2026. Research execution has not started.

## Direction and intended outcome

Rebuild the paper as a reproducible analytical and simulation study of timely cooperative perception. The proposed focus is how radio congestion, receiver processing, and signature verification jointly limit the number and frequency of usable perception updates. Develop and evaluate a lightweight policy that adjusts transmission rate and payload selection under explicit latency and freshness constraints.

Working title: **Deadline Aware Cooperative Perception under Communication and Verification Constraints**.

This is a proposed research direction, not an established novelty claim. A structured literature comparison must establish whether the proposed model or policy adds a defensible contribution. No performance improvement, deployment guarantee, or safety benefit will be claimed in advance.

The first deliverable is this plan. Implementation, new experiments, and manuscript rewriting follow after review of the research direction. Preserve all existing files unchanged.

## Research questions

1. When does receiver verification or fusion processing become the limiting resource even though aggregate radio load appears feasible?
2. How accurately can a tractable model predict useful-update delivery and deadline failures as density, payload size, emission rate, and processing capacity change?
3. Can a joint radio and processing aware policy improve timely useful updates relative to fixed-rate and radio-only policies under the same workload and resources?
4. How sensitive are these conclusions to bursty arrivals, correlated losses, clock offsets, and uncertain service times?

Primary outcome: the proportion of required receiver updates delivered, verified, and made available to fusion within a declared deadline. Count lost and expired updates as failures. Define the receiver set and denominator before experiments; report distance and scenario strata so poor reception is not hidden by aggregation.

Supporting outcomes: latency distributions conditional on successful delivery, deadline miss probability, receiver verification backlog, channel occupancy or busy ratio where supported, throughput, information age at fusion, and fairness between senders. Timeliness is a communications outcome; it does not independently establish perception accuracy or vehicle safety.

## Scope

Use one intersection scenario as the main study and a highway scenario as an external scenario check. Begin with object-level messages and one radio implementation. An IEEE 802.11p reference profile is a candidate for the first implementation because contention is central to the research question; its simulator support and reproducibility must be checked before selection. Do not describe that legacy reference profile as a recommendation for current spectrum deployment.

Treat CPM as a facilities-layer message and service, distinct from the access technology. Verify selected generation rules and encoding against a pinned ETSI version. If only approximate sizes or simplified generation rules are implemented, describe them as CPM-inspired traffic rather than standards-compliant CPM.

Keep compressed feature payloads as a secondary workload sensitivity unless a real encoder and fusion pipeline can be reproduced. Payload size alone cannot establish equivalent information value or perception quality. Do not claim that an object-versus-feature comparison is fair without a defensible quality control.

NR-V2X is an extension after the core study works, not a dependency for the first result. Exclude AI model training, raw sensor streaming, MEC migration, 6G forecasts, and a three-stack deployment survey from the core contribution. An edge path may be a later extension only if its alternative processing stages and additional network hops are explicitly represented.

## Phase 1 Establish the contribution

Create a verified bibliography and a literature matrix organized by modeled stages, queueing assumptions, traffic generation, security costs, freshness constraints, policy controls, validation method, and released code. Search recent primary publications through the research freeze date and follow citations in both directions. Record search terms, databases, dates, and inclusion decisions.

Inspect complete papers before attributing limitations. At minimum, examine age-constrained collaborative-perception scheduling, computation-freshness models, and joint sensing/communication/computation policies. The existence of these lines of work rules out novelty claims based merely on adding AoI or combining communication and computation.

Candidate contribution: a calibrated receiver-capacity model and an implementable policy that accounts for radio and verification bottlenecks together. Compare this specifically against the closest existing methods. If the contribution is already covered, revise the question before coding; possibilities include a careful replication and extension or a narrower empirical characterization, rather than an unsupported priority claim.

Outputs: references.bib, literature_matrix.csv, claim_evidence.csv, and a one-page contribution statement. Gate: identify the closest prior methods, the exact difference, and the experiment that can test its value.

## Phase 2 Specify the model

Define the timing origin at sensor acquisition, availability after inference, message generation, transmission, receipt, verification, and fusion completion. Distinguish processing duration, waiting time, transmission scheduling delay, timestamp error, and information age. State which stages overlap and which share a processor.

Build the simplest model that supports the questions. Start with an independently checkable stationary queueing approximation for screening; explicitly state its arrival and service assumptions. Extend with empirical service distributions and a discrete-event model when burstiness or shared resources invalidate the approximation. Do not sum stage percentiles or assume independence without justification.

For a homogeneous broadcast workload, express offered payload load in consistent units as B = 8 N f S bits/s. Add actual headers, signatures, fragmentation, and repeat transmissions separately. Broadcast transmission load is not multiplied by the number of receivers, but each receiver has its own arrival, loss, and verification workload. Treat offered load as a necessary resource check, not a delivery guarantee.

Define verification utilization from the actual incoming workload and mean service demand, with processor sharing or multiple workers represented explicitly. Distinguish stability conditions from deadline reliability. Define freshness from acquisition timestamps to the newest valid information available to fusion, with clock error evaluated separately.

Outputs: model specification, notation and units table, assumptions register, parameter provenance, and analytical derivations. Gate: unit consistency, low-load limits, overload behavior, zero-loss behavior, and single-sender cases agree with independently calculated checks.

## Phase 3 Implement the reproducible core

Create a separate research directory with model/, simulator/, policies/, configs/, tests/, results/raw/, results/processed/, figures/, manuscript/, and references/. Keep generated results separate from source code. Record dependency versions, simulator commits, hardware, configuration hashes, seeds, and run identifiers.

Implement message generation, per-receiver processing queues, expiry and replacement semantics, fusion availability, and stage timestamps. Use a minimal discrete-event harness to check the analytical approximation, followed by a network simulator for contention and packet reception. Agreement with a harness sharing the same assumptions is internal verification, not independent physical validation.

Pilot the selected radio simulator on a small scenario before building the full experiment framework. For any NR-V2X extension, use the dedicated 5G-LENA V2X branch and its documented ns-3 pairing; do not assume the latest mainline NR module contains compatible sidelink support.

Use measured or traceable published service-time inputs. A local cryptographic microbenchmark measures only the declared implementation and hardware; it is not equivalent to a complete vehicular credential stack. Separate modeled signature processing, certificate handling, and certificate-cache behavior where supported. Do not manufacture a measured dataset from assumed ranges.

Gate: one command recreates a pilot result, stage timestamps reconcile, loss and expiry accounting is complete, and the receiver model responds correctly to controlled overload.

## Phase 4 Develop the policy and baselines

Start with a deterministic policy using locally observable congestion, verification backlog or processing feedback, and update age. Specify how receiver feedback is obtained, its airtime, delay, loss, and privacy implications. A policy using perfect global state must be labeled an oracle, not a deployable baseline.

Candidate controls are bounded emission-rate adaptation, relevance-based object selection, and dropping superseded updates before expensive processing where validity and security semantics allow. Keep selected standards requirements explicit; document any departures. Do not introduce a learned policy unless evidence shows a concrete need.

Compare against fixed-rate transmission, radio-only adaptation, receiver-only adaptation, and the closest reproducible published method identified in Phase 1. Include a properly labeled offline or ideal-information bound only if its assumptions and computation are defensible. Give all deployable methods the same observations, budgets, and tuning opportunities.

Gate: the policy specification is complete, controller costs are included, and baseline tuning uses scenarios separate from final evaluation.

## Phase 5 Evaluate and challenge the claims

Use a coarse pilot grid, then concentrate independent runs near saturation boundaries. Candidate exploratory ranges are 5–100 contributing vehicles, 1–10 Hz generation, object counts that produce traceable encoded sizes, and multiple receiver processing budgets. These are provisional stress ranges, not claims about realistic operating conditions; finalize them from standards and scenario evidence.

Evaluate low, moderate, and high load; steady and event-driven traffic; LOS and obstructed reception; heterogeneous senders; background traffic; and changing density. Separate numbers of transmitting agents from total road users. Derive failures from the radio model in the main network study; synthetic loss models belong in explicitly labeled robustness experiments.

Use independent seeds and report the number of runs and effective sample sizes. Begin with at least 20 pilot runs per selected condition to estimate variance, then determine final replication counts from confidence-interval precision and compute budget. Use run-level or appropriately clustered uncertainty estimates rather than treating correlated packets as independent samples. Preserve failed runs and explain exclusions.

Use held-out loads, densities, or traces to evaluate model prediction. Report prediction error by operating regime, including near saturation. Predeclare provisional engineering targets such as less than 10% relative error for mean delay away from saturation and at most 0.05 absolute error in deadline-failure probability; finalize targets before held-out evaluation and report failures against them. Accuracy targets are evaluation criteria, not promised outcomes.

Run ablations removing verification awareness, age awareness, and traffic burstiness one at a time. Compare fixed and variable service times. Evaluate robustness to stale processing feedback and controller oscillation. Report negative results and the conditions where the policy loses.

Gate: independent checks support every numerical claim, held-out evaluation is complete, and improvements are reported with absolute differences, relative differences where meaningful, uncertainty, and resource costs.

## Phase 6 Rewrite from evidence

Write methods and results first, followed by discussion and limitations, then introduction, abstract, and title. Use this outline:

1. Introduction with one operational problem, specific research questions, and supported contributions.
2. Related work and explicit differentiation from the closest methods.
3. System model, message semantics, assumptions, and parameter provenance.
4. Analytical model with stability and deadline definitions.
5. Proposed policy, pseudocode, observations, and complexity.
6. Experimental methodology, calibration, baselines, and statistical analysis.
7. Results covering model error, bottlenecks, policy comparisons, and ablations.
8. Discussion covering applicability, failure regimes, and limitations.
9. Conclusion limited to demonstrated findings.

Plan figures for the actual pipeline, receiver queues, prediction error, timeliness versus density, the radio/processing bottleneck boundary, policy comparisons, and ablations. Produce every result figure from preserved data. Draw conceptual figures separately and label them clearly. Maintain a claim-to-result mapping.

Reuse only verified background references and necessary definitions from V3. Rebuild equations, numerical tables, figures, contribution statements, and conclusions. Remove duplicated architecture surveys and unsupported AI, standards-compliance, accuracy, or safety claims. Add journal-required author, funding, data/code availability, and disclosure statements based on facts supplied by the authors.

Gate: each reported result traces to a configuration and raw output; all citations resolve; no illustrative scenario is presented as a measurement; all pages and figures receive visual review.

## Phase 7 Select the journal and package the submission

Select the journal after the evidence establishes the contribution. Wireless Networks is a candidate for a model and protocol-performance study; Sensors is a candidate if sensing freshness and fusion relevance are central. Reconsider Vehicular Communications if the final results support a substantial V2X-specific advance. Verify current scope, indexing requirements, fees, and author instructions before formatting or submission.

Prepare a clean manuscript, supplement, reproducibility README, verified bibliography, and journal-specific cover letter. Remove all old journal branding. Author approval, declarations, and permission to submit remain author decisions. No submission is included in this plan.

## Delivery order and effort

| Milestone | Main output | Planning estimate |
|---|---|---|
| M1 | Novelty comparison and frozen research question | 3–5 working days |
| M2 | Model specification and simulator pilot | 4–7 working days |
| M3 | Core implementation and baseline policies | 5–10 working days |
| M4 | Calibration, independent evaluation, and ablations | 7–12 working days |
| M5 | Complete rewrite and reproducibility audit | 5–8 working days |

Allow roughly five to nine working weeks for the core study, subject to simulator compatibility, workload evidence, and computing access. These are planning estimates, not delivery commitments. A second radio stack or real perception-quality evaluation expands the scope and needs a separate estimate.

The next concrete step is M1: establish the nearest prior work and produce the contribution statement before implementing the proposed policy. If the novelty comparison fails, update this plan rather than proceeding with the same claims.

## Implementation contracts

### Workload and outcome definitions

Freeze an exogenous opportunity trace before policy comparison. Each opportunity contains a source, acquisition time, intended receiver set, required object set, deadline, and scenario stratum. Receiver eligibility is determined by ground-truth geometry and a fixed relevance rule at acquisition, never by whether a packet arrived. Fix an analysis region and exclude opportunities without the full observation window before the simulation ends. Report the excluded count.

Use two complementary outcomes. Message timeliness measures transport and processing for messages actually generated. Opportunity coverage measures whether eligible receivers obtained sufficiently fresh, authenticated required information before the external deadline. A policy that suppresses a transmission or removes required objects must not improve the primary outcome merely by removing difficult messages from the denominator. Report full required-object coverage and object-level coverage separately. If matching persistent object identities is unavailable, restrict the claim to source-update freshness and state that limitation.

For receiver r and source s, information age at time t is t minus the acquisition time of the newest successfully verified and fusion-ready update. Out-of-order arrivals never move this timestamp backwards. Specify an initialization state and report age-outage duration before the first valid update rather than silently deleting it. Separate simulation truth from receiver clock observations.

Use deadlines of 50, 100, and 200 ms as provisional sensitivity settings, with 100 ms as the pilot setting. These are experiment design choices, not certified maneuver requirements. Define opportunity success at acquisition time plus deadline, and continuously sampled freshness coverage over the evaluation window. Keep end-to-end latency distinct from the inter-generation interval.

### Component interfaces

| Component | Inputs | Outputs and obligations |
|---|---|---|
| Opportunity generator | Scenario, geometry, source activity, seed | Immutable acquisition and receiver-eligibility trace shared by policies |
| Message builder | Available observations, selected objects, encoding profile | Payload bytes, included object IDs, acquisition timestamps, signature and header lengths |
| Policy | Local observations, delayed authenticated feedback, available observations | Rate, object-selection decision, and feedback transmission decision |
| Radio adapter | Packet size, send time, sender, receiver geometry | Actual receive events, channel observations, packet loss reasons where observable |
| Receiver processor | Arrivals, service profile, worker count, queue capacity | Verification, expiry, fusion availability, and rejection events |
| Analytical predictor | Frozen configuration and calibrated parameters | Predicted mean delay, stability domain, and supported deadline estimates with assumptions |
| Evaluator | Opportunity trace, event log, configuration | Coverage, latency, age, fairness, uncertainty, and accounting report |

Use integer simulation timestamps in nanoseconds and explicit byte counts internally. Convert units only at configuration parsing and presentation boundaries. The mathematical notation may use seconds and bits/s if conversions are documented.

The common event log must contain run_id, config_hash, seed, scenario_id, policy_id, source_id, receiver_id, opportunity_id, message_id, object_ids, acquisition_ns, event_ns, event_type, payload_bytes, wire_bytes, queue_depth, and reason. Mark non-applicable fields as null rather than zero. Define event types for acquisition, generation, enqueue, transmission, reception, verification start/end, fusion readiness, expiry, rejection, and feedback. Keep simulator-specific diagnostic fields in separate tables.

Receiver queues are finite in the executable study. Start with one non-preemptive verification worker and FCFS discipline. Recheck expiry before verification and before fusion. Bound queue capacity, record overflow, and retain all drop reasons. A receiver may reject an arrival using local arrival age or resource limits before verification, but must not trust unsigned identity, timestamps, or object content to replace authenticated state. Any pre-verification replacement optimization requires explicit trust assumptions and a threat analysis; otherwise disable it.

### Analytical starting point

For a stationary single-worker verification queue with Poisson arrivals and independent service times, use the M/G/1 mean waiting expression Wq = lambda E[V²] / (2(1-rho)), where rho = lambda E[V] < 1. This is a declared approximation for a specific stage, not a general result for periodic CPM traffic or a finite drop queue. Show where observed traffic violates these assumptions. Do not extrapolate the expression into rho >= 1, and do not infer a deadline distribution from the mean alone.

Obtain deadline estimates from an explicitly specified distributional model or event simulation, separating approximation from simulation output. Keep the finite-buffer executable model and infinite-buffer analytical approximation distinguishable. Estimate calibration parameters from training scenarios only. Report evaluation error without refitting on the held-out results.

### Initial controller specification

Implement a transparent bounded controller before considering optimization. Pilot control intervals are 100 ms, bounded rates are 1–10 Hz, multiplicative reduction is 0.8, and additive recovery is 0.5 Hz per interval. These are tunable research settings. Select congestion and backlog thresholds on training scenarios, record the search budget, and freeze them before evaluation. Require two consecutive low-load observations before increasing rate to reduce oscillation. Log every control decision and its inputs.

The joint controller reduces emission rate when either channel occupancy or reported receiver backlog exceeds its threshold. Recover only when both are below their low thresholds. Derive the receiver summary from a fixed eligible-neighbor rule, include feedback age, and define conservative behavior when feedback is missing or stale. Pilot staleness is three control intervals. Evaluate malicious feedback only if a supported security model is added; authentication alone does not establish truthful queue reports.

Initially hold payload selection fixed to isolate rate-control effects. Add relevance-based selection as a separate controlled extension, with identical priority rules available to comparable baselines. Evaluate reduced coverage of omitted objects. Feedback must use the modeled radio and verification resources. The radio-only baseline may ignore receiver feedback; provide an additional matched-overhead comparison to distinguish the value of information from its communication cost. Baselines with published semantics retain their original requirements and disclose any adaptation.

## Experiment allocation and execution

Use an intentionally bounded experiment budget rather than the full Cartesian product of all variables.

| Campaign | Proposed design | Purpose and split |
|---|---|---|
| Smoke | 2 and 10 sources, one seed, two rates, fixed processing | Debug accounting; no publication claims |
| Queue calibration | Controlled arrivals and 3 processing budgets | Estimate service behavior and compare analytical limits |
| Policy tuning | 10, 30, and 60 sources; 3 and 7 Hz; separate seeds | Freeze thresholds and service parameters |
| Main comparison | 10, 30, 60, and 100 sources; 2, 5, and 10 Hz; 3 processing budgets; 4 internal policies | 144 configurations before replications; intersection scenario |
| Published comparator | Compatible subset of main comparison | Add the closest method once reproduced; explicitly report excluded cases |
| Generalization | Highway scenario and intermediate unseen source counts such as 20, 45, and 80 | Evaluate without retuning |
| Robustness and ablations | Selected low-load, boundary, and overloaded configurations | Burstiness, feedback delay, service variability, clock offset, and object selection |

The internal policies are fixed-rate, radio-only, receiver-only, and joint control. Offered source sensing opportunities remain common while each policy may change its actual emission rate. Treat the table's rate axis as the fixed-rate baseline or maximum permitted emission setting, as declared in each configuration; do not change its interpretation between plots. For bounded controllers, set the minimum no higher than this maximum.

For a fair model-prediction experiment, include fixed-rate workloads independently of policy comparisons. Choose held-out densities and seeds before calibration. Test periodic and bursty arrivals separately. Add lower-density scenarios if a 10-source condition is already overloaded or lacks a clean low-load reference.

Pilot run length is 120 simulated seconds with a 20-second warm-up. Confirm adequacy using longer runs and time-series diagnostics; overloaded or transient regimes must be reported as transient rather than assumed stationary. Preserve acquisition opportunities only when their deadlines can be observed. Pair comparable policies using the same exogenous traffic and mobility traces, while keeping radio, processing, and policy random streams separate to prevent policy decisions from shifting unrelated random draws.

At 20 replications, the main internal comparison comprises 2,880 runs. Measure wall-clock runtime and output size on smoke and pilot runs before approving that allocation internally. Estimate core-hours as runs multiplied by observed seconds per run divided by 3,600; estimate storage from measured bytes per run. If compute is insufficient, reduce redundant grid points before reducing uncertainty reporting, preserve boundary and held-out cases, and document the revised design before final evaluation. Do not infer compute cost from simulated duration.

Use 95% run-level confidence intervals and paired differences where the trace design supports pairing. Set an initial precision target of a two-percentage-point half-width for the primary coverage rate in selected main conditions. Check the replication budget in batches using pilot variance; freeze final replication counts before final analysis rather than stopping when an improvement becomes significant. For heavy-tailed outcomes, report quantiles and run-level variability. Uncertainty intervals for rare failures require sufficient observations and a stated method; zero observed failures does not establish zero risk.

## Task backlog and evidence of completion

| ID | Task | Depends on | Required evidence |
|---|---|---|---|
| T01 | Preserve originals and inventory reusable material | None | Inventory with file hashes and reuse/discard decisions |
| T02 | Verify literature and bibliography | T01 | Complete source records and literature matrix with locators supporting comparisons |
| T03 | Freeze contribution and evaluation questions | T02 | Contribution statement, nearest-method comparison, and claim-to-experiment mapping |
| T04 | Freeze metrics and system contracts | T03 | Opportunity denominator, timing diagram, queue semantics, parameter provenance |
| T05 | Pilot radio simulator and lock dependencies | T04 | Build/run instructions, pinned revisions, pilot logs and measured runtime |
| T06 | Implement analytic and event models | T04 | Derivations, low-load calculations, overload checks and executable comparisons |
| T07 | Integrate radio and receiver event flow | T05, T06 | Packet-to-opportunity traceability and complete terminal accounting |
| T08 | Implement internal baseline policies | T07 | Deterministic fixtures and logged decisions matching each specification |
| T09 | Reproduce published comparator | T02, T07 | Original configuration comparison or explicit reproduction limitations |
| T10 | Implement joint controller | T08 | Observability audit, feedback overhead, expiry and staleness behavior |
| T11 | Calibrate and freeze experiment manifest | T09, T10 | Train/evaluation split, frozen tuning record, resource estimate and manifest |
| T12 | Execute evaluation and ablations | T11 | Raw runs, failure ledger, uncertainty analysis and held-out error report |
| T13 | Rewrite manuscript and regenerate figures | T12 | Results traced to raw runs, supported contributions and checked references |
| T14 | Audit artifacts and prepare journal package | T13 | Reproduction log, visual review, author-declaration checklist and journal requirements |

T09 may proceed alongside model development once the source study is available. Do not claim comparison with an unreproduced method: document the limitation, include a fair implementable alternative, and adjust the paper's comparative claims. A failure to reproduce the nearest method is a research limitation, not evidence that it performs poorly.

Planned command contract for the future repository:

```text
python -m cpstudy validate-config configs/pilot.yaml
python -m cpstudy run --config configs/pilot.yaml --seed 1
python -m cpstudy audit --manifest results/pilot/manifest.json
python -m cpstudy campaign --manifest configs/evaluation.yaml
python -m cpstudy analyze --manifest configs/evaluation.yaml
python -m cpstudy figures --manifest configs/evaluation.yaml
python -m pytest tests
```

These commands are implementation specifications; they do not exist or run yet. Each command must return a nonzero status on invalid inputs or failed integrity checks. Analysis and figure generation must read preserved outputs and must not silently rerun or modify experiments. A smoke reproduction must work in a fresh documented environment; full reproduction must declare its runtime and storage needs.

Meaningful verification cases include exact single-message timing; byte/bit conversion; one broadcast with multiple independent receiver queues; loss and expiry conservation; duplicate and out-of-order updates; known queueing limits; policy bounds; feedback loss and staleness; no optimistic age update from an unverified packet; and the suppression-denominator case. For each generated message-receiver pair, audit one terminal state or an explicitly right-censored state at the observation boundary. For opportunities, separately account for suppression, missing required content, loss, processing expiry, and success. Preserve multiple contributing diagnostic causes if needed while using one declared precedence for mutually exclusive aggregate failure counts.

## Risks and decision rules

| Risk | Trigger | Planned response |
|---|---|---|
| Novelty already covered | Closest work includes the same model and policy | Change the contribution before experiments; document a replication/extension if defensible |
| Simulator incompatibility | Pinned build or radio smoke case cannot be reproduced | Diagnose the documented stack, then select a supported radio implementation and revise the scope explicitly |
| No credible service-time evidence | Only untraceable latency ranges are available | Run transparent sensitivity studies, seek a scoped benchmark, and limit deployment claims |
| Controller improves delivery but harms coverage | Suppressed updates disappear or object coverage declines | Use the exogenous denominator, show both outcomes, and revise the controller if warranted |
| Model fails near saturation | Error exceeds frozen criteria | Publish the validity boundary and investigate finite buffers, burstiness, or service correlation |
| No policy advantage | Paired comparisons show no material gain | Report the null result and assess whether bottleneck characterization supports a standalone contribution |
| Excessive compute cost | Measured budget exceeds available resources | Reduce redundant conditions before final runs and preserve reproducible held-out checks |
| Missing institutional requirements | Indexing, fees, or author declarations are unknown | Continue journal-neutral research; resolve these facts before final formatting or submission |

## Planning completion and execution status

This plan is complete when it defines the research direction, contribution-validation gate, scope, metrics, component contracts, data provenance, implementation tasks and dependencies, experiment allocation, statistical analysis, reproducibility interface, manuscript structure, risks, and submission boundary. Those planning requirements are specified above.

Research completion is a separate state. T01–T14, the candidate novelty claim, toolchain compatibility, calibration, experiments, manuscript rewrite, and submission package remain to be executed and verified. Listing an acceptance criterion here does not mean that criterion has passed. Journal selection and author declarations remain open facts; they do not prevent completion of this journal-neutral implementation plan.

## Sources checked for planning

- [ETSI TS 103 324 V2.1.1](https://www.etsi.org/deliver/etsi_ts/103300_103399/103324/02.01.01_60/ts_103324v020101p.pdf): published CPS and CPM specification to inspect and pin for the implementation.
- [ETSI CPM ASN.1 repository](https://forge.etsi.org/rep/ITS/asn1/cpm_ts103324): source for encoding definitions; select a compatible revision.
- [Age of Information Guaranteed Scheduling for Asynchronous Status Updates in Collaborative Perception](https://arxiv.org/abs/2310.04813): existing age-constrained CP scheduling; full-paper review required in M1.
- [Age of Computing](https://arxiv.org/abs/2403.05007): existing communication/computation freshness modeling; full-paper review required in M1.
- [Sense2Com](https://www.sciencedirect.com/science/article/pii/S1874490726002235): recent joint sensing, communication, and computation work; full-paper review required in M1.
- [5G-LENA software guidance](https://5g-lena.cttc.es/download/) and [extension compatibility documentation](https://cttc-lena.gitlab.io/nr/manual/extensions.html): dedicated NR-V2X branch and dependency constraints.

These sources establish planning constraints and candidate related work. They do not constitute a completed systematic review or establish the novelty of the proposed study.
