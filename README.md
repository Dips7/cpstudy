# Reviewer Replication Package: V2V Cooperative Perception Simulation

This repository contains the complete reproducible simulation artifacts, canonical manuscript, publication figures, and dynamic audit verification suite for the research paper:

> **"Receiver Feedback and Timely Source-Update Availability in a Cooperative-Perception Simulation"**  
> **Authors:** Dipesh Gurung¹ (M.Sc.), Binod Bhattarai²* (Ph.D. Scholar), Prof. Dr. R. N. Thakur¹  
> ¹ *Research Department & Intel AI Unnati Lab, Lord Buddha Education Foundation (LBEF College), Kathmandu, Nepal*  
> ² *Department of Computer Science and Engineering, School of Sciences, Noida International University (NIU), Greater Noida, India*  
> \* *Corresponding author: Binod Bhattarai (`binoth25@gmail.com`)*  
> **Target Journal:** Elsevier *Vehicular Communications* (Original Research Article)

---

## 1. Quick Start: 1-Command Independent Verification

To independently recompute all offered-load metrics from raw packet reception traces, replay sample opportunity lifecycle streams, assert per-run rate consistency across all 80 paired runs, and dynamically verify all manuscript figures and tables:

```sh
python3 scripts/verify_rework_results.py
```

### What this verifier checks:
1. **Dynamic Manuscript Linkage:** Directly parses numbers from the canonical manuscript (`manuscript/manuscript.md`) across 8 locations (Abstract, Section 5.1, Section 5.6, and Tables 2–6).
2. **Raw Trace Recomputation:** Reads packet receptions (`network-events.csv.gz`) across 144 receiver observations to recompute Table 2 offered load at displayed decimal precision.
3. **Conservation & Replay:** Replays underlying opportunity streams (`network-opportunities.csv.gz` and `events.jsonl.gz`) to audit demand-to-terminal state conservation.
4. **Statistical Aggregation:** Recomputes paired differences, 95% Student-$t$ intervals, Cohen's $d_z$, and Wilcoxon signed-rank tests across 20 matched seeds.

---

## 2. Generating Publication Figures and Building Submission Deliverables

### A. Generate Publication Figures
To regenerate the publication figures from verified data outputs:

```sh
python3 scripts/generate_manuscript_figures.py
```
- **Figure 1 (`figures/fig1_pipeline_timing.png`):** Architectural flow diagram of sender pipeline, 802.11p broadcast channel, receiver verification queue, and deadline timing budget.
- **Figure 2 (`figures/fig2_offered_load.png`):** Receiver offered load distribution across synthetic verification service budgets from a single common baseline.
- **Figure 3 (`figures/fig3_paired_comparison.png`):** Twenty-seed paired policy evaluation means and paired difference contrasts with 95% confidence intervals.

### B. Build Submission Deliverables
To synchronize canonical Markdown, build Word (`MANUSCRIPT.docx`), LaTeX (`MANUSCRIPT.tex`), PDF (`MANUSCRIPT.pdf`), update `submission_package.zip`, and recompute SHA-256 checksums:

```sh
python3 scripts/build_submission_exports.py
```

---

## 3. Repository Structure

```text
├── manuscript/
│   └── manuscript.md              # Canonical research manuscript in Elsevier format
├── submission_package/            # Formatted submission deliverables for journal review
│   ├── MANUSCRIPT.docx            # Word export with preserved table layout
│   ├── MANUSCRIPT.tex             # Standalone LaTeX export
│   ├── MANUSCRIPT.pdf             # Formatted PDF with embedded figures
│   ├── MANUSCRIPT.md              # Synchronized Markdown manuscript
│   ├── HIGHLIGHTS.md              # Standalone highlights (4 bullets, <= 85 chars each)
│   ├── COVER_LETTER.md            # Formal submission cover letter
│   ├── REFERENCES.bib             # BibTeX reference library
│   └── figures/                   # High-resolution figures embedded in submission
├── figures/                       # High-resolution 300-DPI publication figures
├── scripts/
│   ├── verify_rework_results.py   # Complete dynamic verification and recomputation suite
│   ├── generate_manuscript_figures.py # Audited figure generation script
│   └── build_submission_exports.py    # Submission package builder and export pipeline
├── results/
│   ├── processed/rework/          # Recomputed evaluation and paired comparison datasets
│   └── raw/                       # Raw ns-3 network event and opportunity traces
├── configs/                       # Simulation parameters and evaluation manifests
├── model/                         # Closed-loop contract, specification, and parameters
└── evidence/                      # Status tracking, citation audits, and SHA-256 manifests
```

---

## 4. Acknowledgements & Computational Resources

Computational infrastructure, research facilities, and lab resources for this simulation study were supported by the **Department of Research** and the **Intel AI Unnati Lab** at **Lord Buddha Education Foundation (LBEF College)**, Kathmandu, Nepal, and the School of Sciences at **Noida International University (NIU)**.
