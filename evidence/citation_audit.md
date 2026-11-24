# Phase 5 Citation Audit

Date: 2026-11-23

## Scope and method

This is a bounded citation and metadata audit of the manuscript's numbered references (1–14), the BibTeX file, and the literature matrix. It is not a systematic literature review: no protocol for database coverage, screening, duplicate handling, or eligibility was specified. Claims below are therefore limited to inspected papers, publisher metadata, author manuscripts, and standards records.

## Numbered citation mapping and disposition

The numbers in the audit table below map the legacy manuscript reference numbering to the current eleven-reference bibliography, which is strictly numbered in first-use order in `manuscript/manuscript.md`:

| Legacy No. | Reference | Audit result and manuscript action | Current Number & Status |
|---:|---|---|---|
| 1 | Muhammad et al. (2019), security overhead in broadcast V2V | Metadata consistent. Full text inspected. Supports an analytical queueing/security-overhead precedent. It does not support the manuscript's specific 1–5 ms or 6–10 ms hardware verification-time estimates; remove those estimates or supply independent hardware benchmarks. | Retained as [5] (first cited Section 1 line 17) |
| 2 | Thandavarayan et al. (2020), congestion control | DOI and title consistent; corrected pages to 197665–197683. Full author manuscript inspected. It studies cooperative-perception performance and congestion control. Avoid describing it as the dynamic CPM-generation paper; that is legacy reference 13. Any claim that verification is ignored or zero-cost must be checked against its full model before retention. | Retained as [1] (first cited Section 1 line 17) |
| 3 | ETSI TS 103 324 V2.1.1 (2023) | Version/title metadata consistent. Cite for the relevant Collective Perception Service specification only; do not imply that the simulation implements the standard's full generation behavior unless separately demonstrated. | Retained as [3] (first cited Section 1 line 17; standards context) |
| 4 | SAE J3186 (2023) | Edition/title/DOI retained as supplied. Used only for background propositions within the standard's cooperative-perception-system scope. | Retained in BibTeX; excluded from concise draft |
| 5 | Wang et al. (2023), asynchronous collaborative-perception AoI scheduling | Material metadata error corrected. The supplied VTC DOI resolved to an unrelated VTC article. Correct record is WiOpt 2023, pp. 1–8, DOI 10.23919/WiOpt58741.2023.10349877; the arXiv full text and MOSC program were inspected. Its abstract/system model support describing region-level age-constrained scheduling. Remove broad negative claims (e.g. specific omitted contention or verification costs) unless each is verified from the complete paper. | Retained as [6] (first cited Section 1 line 17) |
| 6 | ETSI TS 102 687 V1.2.1 (2018) | Version and title are correct. It is an ITS access-layer DCC specification for ITS operating in the 5 GHz range. The manuscript's implementation should be called a project DCC mapping, not ETSI conformance. | Retained as [4] (first cited Section 1 line 17; standards context) |
| 7 | SAE J2945/1 (2016) | Historical edition record retained. Do not call it the current edition or generalize its scope to all North American congestion control. Reassess whether it is needed after narrowing the standards discussion. | Retained in BibTeX; excluded from concise draft |
| 8 | IEEE Std 1609.2-2016 | Historical edition record retained. Identify the edition explicitly; do not state that it is the current standard. It does not specify measured signature-verification time. | Retained in BibTeX; excluded from concise draft |
| 9 | ETSI TS 103 097 V1.4.1 (2020) | Historical security-format edition metadata retained. Cite only for certificate/header format requirements; it does not establish a specific cryptographic algorithm's runtime. | Retained in BibTeX; excluded from concise draft |
| 10 | Chen et al., Age of Computing | Published version corrected from an arXiv-only 2024 record to IEEE Transactions on Mobile Computing 24(11), 11987–12000 (2025), DOI 10.1109/TMC.2025.3582741. Full author manuscript inspected. It supports distinguishing computation-freshness metrics and deadline models; it is not a vehicle-broadcast or certificate-verification study. | Retained as [7] (first cited Section 1 line 17) |
| 11 | Krishnan & Weimerskirch (2011), Verify-on-Demand | Bibliographic record retained. The manuscript's detailed kinematic-filter description and proposed implementation were not verified here. Phase 4 already records VoD as unimplemented; remove prescriptions and list only as one possible untested direction if accurately described. | Retained in BibTeX; excluded from concise draft |
| 12 | Feiri et al. (2012), certificate omission | Bibliographic record retained. The detailed statement that it omits full certificate chains specifically under high CBR and uses fixed generation frequency needs full-text proposition checking before reuse. | Retained in BibTeX; excluded from concise draft |
| 13 | Thandavarayan et al. (2020), CPM generation | Material metadata error corrected: title is “Generation of Cooperative Perception Messages for Connected and Automated Vehicles,” IEEE Transactions on Vehicular Technology 69(12), 16336–16341, DOI 10.1109/TVT.2020.3036165. Full author manuscript inspected. Cite for dynamic message-generation rules and content organization, not for the separate congestion-control evaluation. | Retained as [2] (first cited Section 1 line 17) |
| 14 | Yates & Kaul (2019), Age of Information | Metadata consistent. General background source for AoI terminology; it does not validate the manuscript's operational timely-opportunity metric or its implementation. | Retained in BibTeX; excluded from concise draft |
| — | Tian, Shi, & Chen (2026), Sense2Com | *Physical Communication* 78, 103214, DOI 10.1016/j.phycom.2026.103214. Publisher record, abstract, problem formulation, and coordination model inspected. Authors corrected to Jin Tian, Yan Shi, and Shanzhi Chen. Formulates multi-agent reinforcement learning for joint sensing target selection, V2V communication, and computation offloading. Contrast softened to its stated focus on transmission scheduling and offloading coordination rather than receiver-side signature-verification queue dynamics. | Added as [8] (first cited Section 1 line 17) |
| — | Henderson et al. (2008), ns-3 simulator | *ACM SIGCOMM 2008 Demonstration*, p. 527, DOI 10.1145/1402958.1403014. Verified from conference PDF. Cited for discrete-event simulator architecture. | Added as [9] (first cited Section 3.1 line 52) |
| — | ns-3 project (2025), ns-3.46.1 release & ns-3.46 model library | Official 2025 release download: `https://www2.nsnam.org/releases/ns-3-46/download/`; versioned ns-3.46 model documentation: `https://www.nsnam.org/docs/release/3.46/models/html/wifi-user.html`. Cited for 802.11p AdhocWifiMac and log-distance propagation model behavior. | Added as [10] (first cited Section 3.1 line 52) |
| — | Kleinrock (1975), Queueing Systems Vol. 1 | Classical queueing textbook (John Wiley & Sons, ISBN 0-471-49110-1). Cited in Section 3.2 for the Pollaczek–Khinchine $M/G/1$ mean waiting-time equation and its core theoretical assumptions. | Added as [11] (first cited Section 3.2 line 64) |

## In-text claim checks requiring Phase 6 edits

- Introduction's safety-critical framing, collision consequences, and field-of-view generalizations are broader than this synthetic study and need citation-specific support or removal.
- The ECDSA verification-time ranges attributed to references 1 and 8 are unsupported by those sources as currently cited; remove unless benchmark data with device, implementation, and measurement method are added.
- Table 1 contains several categorical negative claims about prior methods (no verification, no contention, no feedback, closed access, and specific model simplifications). Retain only entries verified from the complete cited source; otherwise replace the table with a small, neutral comparison of documented model focus and access reviewed.
- The current Table 1 description of reference 2 as “Dynamic CPM generation & DCC” conflates two distinct papers. Separate reference 2 (congestion-control evaluation) from reference 13 (message generation).
- The manuscript's phrase “historically ... almost exclusively” and statements that prior work does not combine queues or feedback imply a broad search. Remove or explicitly limit them to the inspected studies; this audit is not systematic.
- References 11 and 12 should not be used to prescribe Verify-on-Demand or certificate omission. Those mechanisms were not implemented or evaluated in this study.
- The conclusion's standard-revision mandate and safety claims are outside the evidence base and are already marked for removal in the causal-claim and limitations registers.

## Standards and current-edition notes

The references intentionally preserve historical editions used by the source manuscript. ETSI TS 102 687 V1.2.1 is scoped to ITS in the 5 GHz range. IEEE 1609.2-2016, SAE J2945/1 (2016), and ETSI TS 103 097 V1.4.1 should be named as specific historical editions rather than presented as current. The simulated DCC policy is not a complete standards implementation.

## Emerging or deferred candidates

- Tian, Shi, and Chen, “Sense2Com” (Physical Communication 78, 2026, article 103214, DOI 10.1016/j.phycom.2026.103214): publisher record, abstract, problem formulation, and coordination model inspected. Authors are Jin Tian, Yan Shi, and Shanzhi Chen. Promoted to cited related work [8] as an adjacent 2026 study on multi-agent reinforcement learning for joint sensing, communication, and computation offloading. It is boundedly contrasted in Section 2 and Table 1 by describing its stated focus on transmission scheduling and offloading coordination rather than receiver-side cryptographic signature-verification queue dynamics.
- Miyata et al., “Load-Aware Agent Selection via Delay Prediction in V2X Cooperative Perception”: the author page identifies a GLOBECOM 2026 work to appear and supplies an abstract. No verified proceedings publication or DOI is yet available. Explicitly deferred pending publication of proceedings.
- “A Dynamic Priority-Based Batch Verification Scheme for V2X Communication in Vehicular Networks” (DPBV, IEEE IV 2025, DOI 10.1109/IV64158.2025.11097768): IEEE abstract record checked; full text was not accessible for complete algorithmic auditing. Explicitly deferred pending full-text retrieval.

## Metadata and reproducibility notes

Corrected bibliographic records are in `references/references.bib`; the matching printed reference list is in `manuscript/manuscript.md`. The literature matrix records access depth and remaining review work per item. `references/search_log.csv` records targeted, ad hoc metadata checks and does not represent a comprehensive discovery/search protocol.
