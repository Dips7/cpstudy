# Simulation Model Specification

Version 0.2 — Phase 4 model-assumption audit, 2026-11-23.

This document describes the implemented experiment model in `simulator/cp-closed-loop.cc`, `cpstudy/closed_loop.py`, `cpstudy/receiver.py`, and the configurations under `configs/` and `scripts/`. It is a discrete-event simulation specification. It is not a vehicle-system specification, hardware benchmark, CPM implementation, or safety model.

## Demand, movement, and eligibility

Each source receives exogenous periodic acquisition opportunities at 10 Hz, with a seeded phase. Opportunity generation is independent of policy and transmission admission. A selected opportunity schedules a data broadcast after the configured fixed inference and signing delays. Suppressed opportunities remain in the demand denominator. The main studies use 100 ms deadlines and evaluate eligible source-receiver pairs using geometry at acquisition time; they do not model object detections or perception quality.

The intersection and highway scenarios use controlled, synthetic constant-velocity trajectories. Vehicles are placed on perpendicular two-way road flows for the intersection or six straight lanes for the highway. The configured speed is 10 m/s (36 km/h) in both scenarios. Nodes recycle at the simulation boundary. There is no car following, traffic-light behavior, SUMO trace, measured trajectory, or calibrated traffic density. Eligibility uses a 150 m pairwise range and scenario evaluation regions; eligibility geometry and actual radio delivery are distinct.

## Radio model

The closed-loop studies use ns-3.46.1, `WIFI_STANDARD_80211p`, `AdhocWifiMac`, UDP broadcast, a constant-rate 6 Mbps OFDM mode with 10 MHz bandwidth, 23 dBm transmit power, constant-speed propagation delay, and log-distance propagation loss with exponent 2.5 and reference loss 47.86 dB. These settings are simulator inputs. The experiment does not include building blockage, shadowing, a calibrated NLOS model, measured channel traces, a facilities-layer ITS-G5 stack, or an ASN.1 CPM encoder. Do not describe the radio result as standards conformance or field validation. The source does not set a project-specific receive-sensitivity threshold; any such value must be taken from the exact ns-3 build/default and not asserted from the manuscript.

Each data packet includes a 1100-byte experiment payload plus 100 bytes of modeled security overhead. Feedback uses a 96-byte experiment payload plus the same overhead. The data airtime approximation in the DCC mapping adds 64 bytes of protocol overhead and assumes the configured 802.11p 6 Mbps / 10 MHz frame format. These are simulator byte counts, not encoded CPM sizes or measured signed-message sizes. The controller's local busy value is the union of observed TX, RX, and CCA-busy PHY intervals over its configured control window, including the node's own transmissions; it is an experiment occupancy measure and is not claimed to be a standardized CBR measurement.

## Sender workload and controllers

The common opportunity rate is 10 Hz, with sender rates bounded between 1 and 10 Hz. Fixed emits at its configured fixed rate. Radio and queue-aware policies adapt a rate target at 100 ms control intervals. The admission timer advances by the reciprocal of the current target rate and is not rescheduled when the target changes; emission is therefore quantized to opportunity ticks and can show timing jitter and delayed response. Rate-control outcomes apply to these implemented policies and settings only.

The `radio` policy is the project's channel-busy-ratio AIMD controller. `joint` combines the same radio signal with authenticated neighbor backlog reports; `calibrated` changes the backlog aggregation and thresholds. For feedback-enabled policies, feedback is broadcast every 200 ms, signed with the configured delay, processed by the same receiver verification queue, and treated as truthful after verification. Missing or stale reports can trigger conservative behavior in `joint`; this is an explicit policy rule, not evidence that a real vehicle would observe the same neighbor set.

The `dcc` policy implements a research single-service mapping built from the bounded adaptive core associated with ETSI TS 102 687 and an airtime-to-interval rule. It omits a full ITS-G5 facilities stack, multiple traffic classes, and the complete resource allocation/conformance framework. Call it the project's DCC mapping or DCC-inspired comparator, not a standards-conformant ETSI implementation. It is not included in the 20-seed paired comparison.

## Receiver service and queue

Each receiver has one non-preemptive FCFS verification worker and a waiting capacity of 32 messages; the active message is additional, so the maximum modeled system population is 33. The verification service duration is a configured deterministic delay in the main experiments (`service_cv = 0`), not measured CPU time. Signatures are assumed valid. The model includes no signature failures, certificate parsing, chain validation, revocation checks, key lookup, HSM/ECU scheduling, processor contention between cores, or measured cryptographic implementation.

Every received data message is admitted to the worker/queue or dropped on queue overflow. The implementation does not prune an already-expired message before verification. Once verification completes, it compares simulated completion time to the message deadline; an expired message terminates as `verification_expired`. Otherwise it incurs a fixed fusion-availability delay without a shared fusion worker, then succeeds or terminates as `fusion_expired`. This behavior is a software-model rule, not a claim about standard automotive firmware. Queue depth and simulated service time do not measure physical processor occupancy or CPU cycles.

## Queueing calculations and limits

For a receiver, offered load is estimated as `rho = lambda * E[V]`, where arrivals are counted from receiver events in the declared time window and `E[V]` is the configured mean service duration. This is a queueing load estimate; it is not measured worker busy fraction. The Phase 3 recomputation uses data receptions during `[1 s, 5 s)` for the fixed-policy stress traces, divided by the 4 s active interval, and includes all 48 receiver identities for each of three seeds. Fixed-policy reception traces across verification budgets were identical where available. Two 3 ms traces were unavailable or truncated; in those cases the matching 1 ms fixed-policy baseline trace was reused and that provenance is disclosed in `evidence/results_reconciliation.md`.

The M/G/1 expression `Wq = lambda E[V^2] / (2(1-rho))` requires Poisson arrivals, iid service independent of arrivals, FCFS, and an infinite queue with `rho < 1`. The experiment traffic is periodic and bursty, the queue is finite, and service is deterministic in the main runs. Use the expression only as a conditional analytical reference, not as a validated prediction for these traces. Finite queues may bound stored work by dropping arrivals; that does not establish deadline reliability.

An arithmetic service-capacity illustration may be stated conditionally: if one receiver has exactly `n_s` equally active senders, every emitted message is received without loss, each requires deterministic service `tau`, and service allocation is equal, keeping offered load strictly below one requires each sender rate `f < 1/(n_s * tau)`. With 24 other senders and `tau = 6 ms`, that condition is `f < 6.94 Hz`; relative to 10 Hz demand, the corresponding emission fraction is below 69.4%. This is not a TOSR theorem or a predicted success rate. It assumes a fixed complete neighborhood, equal rates, no radio loss, no feedback/background load, and one-to-one same-opportunity credit. It must not be generalized to the dynamic simulations.

## Outcomes and audit boundaries

The primary `opportunity_success_rate` scores the exact generated update for its demand-receiver pair, with suppressed demand retained in the opportunity denominator. `opportunity_freshness_rate` separately allows an authenticated newer observation to cover an earlier opportunity if the freshness and deadline conditions hold. These metrics have different credit rules. A deadline is inclusive (`ready_time <= deadline`). See `outcome_contract.md` for terminal states, censoring, and the raw-run audit.

The audit validates event accounting and saved summary consistency for 360 of 370 discovered runs. Ten stress runs have incomplete traces; they are excluded from trace-supported aggregates and cannot resolve mechanism claims. Audit success does not validate radio realism, workload representativeness, signature security, hardware performance, or safety benefit.

## Scope boundary

Results describe these synthetic policies, periodic demand, controlled geometries, radio settings, deterministic service delays, finite queue, and selected seeds. They do not establish a deployable controller, calibrated ECDSA/HSM timings, real-world cooperative perception efficacy, vehicle safety impact, CPM conformance, standards revision needs, or general optimality of any sender/receiver architecture. The tested result is an application-level timing outcome in a bounded simulation model.
