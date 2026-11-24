# Reviewer Replication Package: V2V Cooperative Perception Simulation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24498751.svg)](https://doi.org/10.5281/zenodo.24498751)

This repository contains the complete reproducible simulation artifacts, ns-3 scenarios, trace datasets, publication figures, and dynamic audit verification suite for the research paper:

> **"Receiver Feedback and Timely Source-Update Availability in a Cooperative-Perception Simulation"**  
> **Authors:** Dipesh Gurung¹ (M.Sc.), Binod Bhattarai²* (Ph.D. Scholar), Prof. Dr. R. N. Thakur¹  
> ¹ *Lord Buddha Education Foundation (LBEF College), Kathmandu, Nepal*  
> ² *Department of Computer Science and Engineering, School of Sciences, Noida International University (NIU), Greater Noida, India*  
> \* *Corresponding author: Binod Bhattarai (`binoth25@gmail.com`)*  
> **Target Journal:** Elsevier *Vehicular Communications* (Original Research Article)  
> **Permanent Archive:** [DOI: 10.5281/zenodo.24498751](https://doi.org/10.5281/zenodo.24498751)

---

## 1. Quick Start: 1-Command Independent Verification

To independently recompute all offered-load metrics from raw packet reception traces, replay sample opportunity lifecycle streams, assert per-run rate consistency across all 80 paired runs, and verify all numerical claims and tables:

```sh
python3 scripts/verify_rework_results.py
```

### What this verifier checks:
1. **Raw Trace Recomputation:** Reads packet receptions (`network-events.csv.gz`) across 144 receiver observations to recompute Table 2 offered load at displayed decimal precision.
2. **Conservation & Replay:** Replays underlying opportunity streams (`network-opportunities.csv.gz` and `events.jsonl.gz`) to audit demand-to-terminal state conservation.
3. **Statistical Aggregation:** Recomputes paired differences, 95% Student-$t$ intervals, Cohen's $d_z$, and Wilcoxon signed-rank tests across 20 matched seeds.
4. **Benchmark Verification:** Confirms all 8 published evidence locations (Abstract, Section 5.1, Section 5.6, and Tables 2–6) match simulation traces at exact decimal precision.

---

## 2. Generating Publication Figures

To regenerate the publication figures from verified data outputs:

```sh
python3 scripts/generate_manuscript_figures.py
```
- **Figure 1 (`figures/fig1_pipeline_timing.png`):** Architectural flow diagram of sender pipeline, 802.11p broadcast channel, receiver verification queue, and deadline timing budget.
- **Figure 2 (`figures/fig2_offered_load.png`):** Receiver offered load distribution across synthetic verification service budgets from a single common baseline.
- **Figure 3 (`figures/fig3_paired_comparison.png`):** Twenty-seed paired policy evaluation means and paired difference contrasts with 95% confidence intervals.

---

## 3. Repository Structure

```text
├── figures/                       # High-resolution 300-DPI publication figures
├── scripts/
│   ├── verify_rework_results.py   # Complete dynamic verification and recomputation suite
│   ├── generate_manuscript_figures.py # Audited figure generation script
│   └── run_20seeds_paired.py      # Paired simulation execution driver
├── simulator/                     # C++ ns-3 closed-loop simulation models
│   ├── cp-closed-loop.cc
│   └── cp-radio-pilot.cc
├── results/
│   ├── processed/rework/          # Recomputed evaluation and paired comparison datasets
│   └── raw/                       # Raw ns-3 network event and opportunity traces
├── configs/                       # Simulation parameters and evaluation manifests
├── model/                         # Closed-loop contract, specification, and parameters
└── evidence/                      # Status tracking, citation audits, and verification manifests
```

---

## 4. Acknowledgements & Computational Resources

Computational infrastructure, simulation workstations, and research resources for this investigation were provided by the **Intel AI Unnati Lab** at **Lord Buddha Education Foundation (LBEF College)**, Kathmandu, Nepal, and the School of Sciences at **Noida International University (NIU)**.

