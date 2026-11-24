# Closed loop simulation contract

The ns3-closed-loop backend implements the radio and receiver processor in the same ns-3 event clock. Feedback broadcasts compete with data frames and enter the same finite FCFS verification queue. A node can use a report only after its verification completes. Reports are aged from their sender acquisition timestamp and older out-of-order reports cannot replace newer state. All signatures are assumed valid; cryptography is represented by processing cost, not an implementation of a vehicular credential stack.

The locally observable neighbor set is all sources of recently authenticated received feedback. Controllers do not query simulation geometry or remote queue state. Missing fresh feedback invokes the declared conservative rate reduction; this can harm isolated nodes and is an evaluated policy limitation. Feedback snapshots are truthful in this experiment; authentication does not establish truthfulness against a malicious sender.

Data verification cost is paid for received traffic even if the source/receiver pair is outside the evaluation region. External acquisition opportunities use fixed per-source phases and do not depend on policy, admission, reception or processor state. An eligible source/receiver pair must be within range_m at acquisition. In the intersection case both must also lie within the central square extending 150 m from the crossing; highway eligibility uses pairwise distance. Noneligible traffic continues to occupy the radio and processor.

Synthetic mobility consists of constant-speed flows on two perpendicular two-way roads, or a six-lane straight highway with opposing directions. Nodes recycle at the simulation boundary. Recycling is outside both analysis regions: the central 300 m square at the intersection and the central 600 m highway segment. Ground-truth eligibility geometry is computed directly from initial trajectory and time; it is not affected by floating-point accumulation from radio-triggered mobility queries. Radio propagation continues to use ns-3 mobility models. This is controlled mobility, not SUMO-calibrated traffic or a validated road-safety model. The initial propagation model is log-distance, with no building blockage. Occlusion/NLOS studies remain pending.

End-to-end time begins at acquisition, followed by fixed inference/signing delays, actual MAC/radio delivery, a single verification worker with bounded waiting capacity, and a fixed parallel fusion-availability delay. There is no modeled shared fusion GPU. Pre-verification payload metadata does not change authenticated state or trigger content-aware replacement.

The basic fixed/radio/receiver/joint policies use average-rate admission targets quantized to the sensing grid. Their target timer advances by 1/current_rate when an opportunity is admitted; existing timer deadlines are not rescheduled on controller updates. This gives quantization jitter and a delayed reaction that must be reported. The reference DCC policy uses a strict minimum-gap gate and may emit below its nominal rate because of the same sensing grid.

Channel occupation is the union of observed TX, RX and CCA-busy PHY intervals over a local window, including the ongoing state. It includes own transmissions. It is an experiment occupancy metric; no standard CBR-conformance claim is made. The raw controls table preserves every observation and decision for independent replay.

## Project DCC-mapping comparator

The `dcc` policy implements a research adaptation of the bounded core associated with ETSI TS 102 687 V1.2.1 clause 5.4, with globally aligned 200 ms updates using two 100 ms local observations. The single-service rate mapping follows the airtime-to-interval form used by Thandavarayan et al. (2020), equation (4), and is capped at the configured application maximum. Its initial duty allocation is 0.005, a declared experiment setting.

Its packet airtime formula uses the declared 802.11p 6 Mbps/10 MHz non-QoS frame format. No CAM traffic class or full facilities-layer resource allocator is implemented. The gate is not rescheduled on duty updates using the optional annex B timing rule. This is a project DCC mapping in a controlled single-service setting, not a complete reproduction of the 2020 experimental study, a complete ITS-G5 resource allocator, or an ETSI implementation certification.

Primary source: https://www.etsi.org/deliver/etsi_ts/102600_102699/102687/01.02.01_60/ts_102687v010201p.pdf

## Audit contract

Raw event, opportunity, control and DCC tables share a monotonically increasing trace ordinal. The independent Python audit reconstructs feedback visibility, checks every controller rate, and reproduces DCC core updates. Normalized data traces retain only evaluation-eligible pairs; raw traces retain all received traffic and feedback so the cost is not hidden. Every generated eligible pair must have a terminal state or an explicit observation-boundary censoring record. Misses with fully observed deadlines are not censored.
