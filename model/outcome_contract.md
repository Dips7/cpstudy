# Outcome and Event Contract

## Status

This contract describes the current intended scoring behavior and the inspected code paths. An independent raw-run replay covered 370 saved run directories: 360 passed conservation and summary comparisons; ten major-revision runs have incomplete preserved traces and cannot be validated. See evidence/outcome_audit_summary.md and evidence/outcome_audit.json.

## Entities and units of analysis

### Source-update opportunity

An opportunity is one exogenous source acquisition at time t for source s. It has a sequence identifier, acquisition timestamp, deadline, and a receiver set fixed by the scenario eligibility rule at acquisition. Opportunities whose deadline is later than the observation stop are excluded from evaluated demand.

### Opportunity-receiver demand pair

The unit for the primary opportunity outcome is one evaluated opportunity and one receiver in its exogenous eligible receiver set. The denominator is the total number of such pairs, including pairs whose source opportunity was suppressed. Suppressed demand cannot disappear from the denominator.

### Generated message-receiver pair

When a source opportunity is emitted, each eligible receiver defines an expected generated message-receiver pair. Ineligible traffic may still consume radio or receiver resources but is outside this pair set. A generated eligible pair must reach exactly one terminal state, including explicit unfinished/censored states at the observation boundary.

These populations are distinct. A demand pair for a suppressed opportunity has no generated message pair. Conversely, non-eligible messages and feedback may generate work and terminal events in the simulation but do not enter the evaluated demand denominator.

## Lifecycle and timestamps

Times are represented as integer nanoseconds in simulation event records.

1. **Acquisition:** sensor/source-update opportunity time, t_acq. This is the age and deadline origin.
2. **Emission decision:** the source policy either admits the opportunity for message generation or suppresses it. Suppression is a demand outcome, not a generated message terminal state.
3. **Generation/signing availability:** the model applies configured inference and signing delays before the update is available to transmit. These are fixed/synthetic delays in the current model.
4. **Transmit start and completion:** the radio simulator records transmission events. The contract must distinguish the simulator’s event timestamp from actual PHY airtime completion where the trace provides separate fields.
5. **Reception:** a receiving node gets a data frame. Broadcast delivery and receiver eligibility are separate: all traffic can affect radio/processor resources, while only evaluation-eligible pairs enter the opportunity score.
6. **Queue admission:** the update either starts verification immediately, enters the bounded waiting queue, or terminates as queue_overflow if no waiting slot is available.
7. **Verification start/end:** one modeled FCFS worker processes the update for the configured service time. Signature validity is assumed; no cryptographic primitive or certificate path is executed.
8. **Verification expiry:** if verification ends after the source opportunity deadline, the terminal reason is verification_expired. Equality at the deadline is permitted by the receiver implementation.
9. **Fusion availability:** after successful verification, a fixed fusion availability delay is applied. It is not a shared fusion-worker queue.
10. **Fusion expiry/readiness:** if fusion availability is later than the deadline, the terminal reason is fusion_expired. Otherwise the pair reaches fusion_ready and then terminal reason success. Equality at the deadline is permitted.
11. **Observation boundary:** any generated pair without a prior terminal event is assigned a boundary reason. In the closed-loop replay, a deadline beyond stop is right_censored; a received pair with an already-observed deadline is processing_unfinished; an opportunity with no emitted message is sender_unfinished; otherwise a sent message not received by the eligible receiver is radio_not_received.

Raw event logs should preserve event time, trace order, source, receiver, sequence/message identity, acquisition time, event type, and terminal reason. Do not infer missing lifecycle stages from a summary percentage.

## Deadline boundary

The current receiver code expires only when current time is strictly greater than the deadline. The opportunity freshness implementation uses bisect_right, which includes readiness timestamps equal to the deadline. Therefore the operational success rule is:

**fusion_ready_time <= opportunity_deadline**

The deadline interval is closed at its upper endpoint for scoring. Manuscript prose, equations, tests, and plots must use this rule consistently.

## Two separate opportunity metrics

The code exposes two related but non-identical outcomes. The existing campaign aggregation and paired-study runner use same-opportunity timely success. They must not be conflated under one unexplained label.

### A. Same-opportunity timely success

The summary field opportunity_success_rate counts terminal reason success for the message generated for that exact opportunity-receiver pair and divides by evaluated opportunity-receiver pairs. A suppressed opportunity contributes no success and remains in the denominator. This is the field used by the paired-study runner and the campaign aggregation path. This measure does not credit a later update toward an earlier opportunity.

### B. Newest-update freshness coverage at opportunity deadlines

opportunity_freshness constructs successful update streams by source and receiver. For each evaluated opportunity-receiver pair, it checks whether at least one successfully fusion-ready update from that source/receiver has acquisition time at least as recent as the opportunity and readiness time no later than its deadline. A later update can therefore satisfy an earlier demand. A single successful update can satisfy multiple earlier opportunity queries when the acquisition and deadline conditions hold. This is not a one-to-one message/opportunity matching metric.

Manuscript usage:

- Use “same-opportunity timely success rate” for opportunity_success_rate. This is the provisional primary outcome for the rework because it is the field used by both the paired runner and factorial aggregation.
- Use “deadline freshness coverage” for opportunity_freshness_rate.
- Reserve “TOSR” for one of these only after the authors choose a formal definition and all reported analyses are regenerated using that exact field.
- Remove the current Proposition 1: its one-message/one-opportunity conclusion does not follow from the freshness-coverage implementation.

## Terminal-state conservation

For each evaluated opportunity-receiver demand pair:

- If its opportunity was not generated, classify it as suppressed.
- If generated, classify it by exactly one terminal reason for the corresponding message-receiver pair.

The scored partition must satisfy:

evaluated_demand_pairs = suppressed_demand_pairs + generated_evaluated_pairs

generated_evaluated_pairs = sum of terminal counts over generated evaluated pairs

evaluated_demand_pairs = suppressed_demand_pairs + success + radio_not_received + queue_overflow + verification_expired + fusion_expired + sender_unfinished + processing_unfinished + right_censored + any explicitly documented terminal class.

The global terminal log may also contain non-eligible traffic and feedback. Its total must not be compared directly to the evaluated opportunity denominator. Audits must filter by source opportunity, receiver eligibility, and data/feedback kind before checking this partition.

## Required audit behavior

scripts/audit_outcomes.py accepts one run directory and reads its preserved compressed opportunity and event records without modifying them. It must:

- verify unique opportunity identity and receiver-set membership;
- derive expected generated eligible message-receiver pairs from opportunity records;
- require exactly one terminal event for each such pair and reject duplicate/unexpected terminals;
- count suppression separately from generated-pair terminal reasons;
- report demand, generated, suppressed, and terminal totals and rates;
- compare recomputed counts with summary.json when available, identifying metrics that use different credit rules;
- write a machine-readable JSON report to an explicit output path, never overwrite raw inputs.

An aggregate campaign audit can be added only after the single-run audit is independently reviewed.

## Verified implementation details and open questions

- metrics.py uses bisect_right and therefore includes readiness exactly at deadline.
- metrics.py allows one update to cover multiple older freshness queries; this behavior is already partly covered by test_newer_observation_can_cover_suppressed_demand.
- engine.py summary same-opportunity success is based on the terminal for the opportunity’s own message identifier, while its opportunity_freshness_rate is calculated by opportunity_freshness.
- receiver.py records terminal success only after fusion readiness and permits equality at deadline.
- closed_loop.py reconstructs eligible pair terminal states from network opportunities/events and assigns boundary states at simulation stop.
- The independent audit script reads normalized events.jsonl.gz because ClosedLoop synthesizes terminal states for missed receptions; the lower-level network-events.csv.gz does not contain those synthesized terminal states.
- Across the 360 complete factorial, paired, and major-revision traces, the audit confirmed exactly one terminal per generated eligible message-receiver pair and matched summary counts, including suppression. Ten incomplete stress traces remain preserve-only and cannot support terminal-level claims.
- Three major-revision opportunity CSVs are truncated; one major-revision normalized event file is incomplete. The corresponding summaries cannot be independently reconciled from surviving traces. These historical files must remain unchanged and those run results must be excluded from claims requiring a complete terminal audit unless complete provenance-matched copies are located.
- The raw pair denominator and excluded-opportunity rule must be checked for every campaign before manuscript tables are regenerated.
