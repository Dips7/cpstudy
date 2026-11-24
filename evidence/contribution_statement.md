# Contribution Statement: Bounded Simulation Characterization

## Current defensible contribution

This project provides a controlled simulation comparison of source-update availability under common exogenous demand, with modeled radio access and a finite receiver verification queue. It characterizes fixed transmission, the project's radio-only rate adaptation, receiver-load feedback, and a project DCC single-service mapping in synthetic scenarios. A separate paired experiment compares fixed, radio, uncalibrated joint, and calibrated-feedback policies at one intersection operating point. Historical major-revision runs lack embedded full configuration and simulator-binary hashes, so reproducibility lineage is incomplete for that family.

The empirical contribution is conditional on the simulator, mobility, propagation, traffic, timing, queue, and policy assumptions documented in the model contracts and run catalog. The controller is a diagnostic policy in this study, not a claimed novel algorithm. Negative or mixed policy results remain valid outcomes.

## Research question

Under common exogenous source-update demand in the implemented simulated system, how does adding delayed receiver-load feedback change timely authenticated source-update availability relative to fixed transmission and radio-only rate control?

## Prior-art boundary

Existing literature already studies vehicular security queues, radio congestion control, and communication/computation freshness. Combining radio and receiver processing constraints is not by itself a novelty claim. Several close recent works in the current literature matrix have only preview or abstract-level inspection. Their methods and limitations remain unknown where full text was not inspected.

The manuscript may describe the specific implementation and evidence gap addressed by this comparative simulation, but it must not claim broad priority, superiority to unreproduced methods, or that prior work omits a feature unless full-text evidence supports that statement. Do not call the literature process systematic unless the search and screening protocol is documented.

## Evidence and validity boundaries

- Verification is represented as a configured service-time budget. The model assumes signatures are valid and does not implement ECDSA, certificate validation, VPKI processing, or an automotive hardware security module.
- Payload and inference, signing, and fusion delays are synthetic or fixed model inputs unless separate measured provenance is provided.
- Mobility and propagation are controlled simulation assumptions, not validated traffic/channel traces.
- The study measures source-update timeliness/freshness, not object-level perception accuracy, driving decisions, collision avoidance, or vehicle safety.
- The factorial, stress, ablation, and paired studies are separate experiment families. Existing analyses are exploratory unless dated records establish that hypotheses and analyses were fixed before outcome inspection.
- Results from one operating point do not establish behavior across the full parameter space.

## Manuscript claim boundary

Describe findings as results within the tested simulation conditions. Do not claim a novel controller, calibrated hardware performance, safety benefit, deployment efficacy, CPM conformance, a general capacity theorem, or a standards-revision mandate based on the current evidence. All numerical claims must map to the canonical evidence/claim_evidence.csv with their run family, source, denominator, and audit disposition.

## Status

The research scope, Phase 2 outcome audit, Phase 3 numerical reconciliation, Phase 4 model-assumption audit, and Phase 5 bounded citation audit are recorded in their evidence artifacts. A journal-neutral canonical manuscript draft now exists at `manuscript/manuscript.md`; figure/format QA, package rebuild, author-statement confirmation, and independent release review remain. This statement does not certify scientific validity or submission readiness.
