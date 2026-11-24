# Submission Package (Elsevier *Vehicular Communications*)

This submission package contains the complete manuscript, figures, bibliography, research highlights, and cover letter prepared for submission review to Elsevier's **Vehicular Communications** as an Original Research Article.

## Contents

| File / Folder | Description |
|---|---|
| `MANUSCRIPT.md` | Canonical Markdown manuscript formatted for *Vehicular Communications* with decimal section numbering, draft author declarations, and embedded figure callouts. Synchronized from `../manuscript/manuscript.md`. |
| `MANUSCRIPT.docx` | Publication-ready Word export generated directly via Pandoc with preserved table row formatting and embedded figures. |
| `MANUSCRIPT.pdf` | Formatted PDF rendered with embedded assets via Pandoc HTML5 and headless Google Chrome. |
| `MANUSCRIPT.tex` | Standalone LaTeX export generated via Pandoc with single-backslash math formatting and relative figure paths. |
| `HIGHLIGHTS.md` | Standalone Research Highlights compliant with Elsevier guidelines (4 bounded bullet points, each \(\le 85\) characters). |
| `COVER_LETTER.md` | Internal review draft cover letter addressed to the Editor-in-Chief of *Vehicular Communications* (marked pending author review and sign-off). |
| `REFERENCES.bib` | Clean BibTeX bibliography source strictly aligned with the manuscript references. |
| `figures/` | High-resolution publication figures strictly limited to the three figures referenced in the manuscript (`fig1_pipeline_timing.png`, `fig2_offered_load.png`, `fig3_paired_comparison.png`). |
| `README.md` | This package inventory, build documentation, and submission readiness status. |

## Publication Figures

1. **Figure 1 (`figures/fig1_pipeline_timing.png`):** Simulated cooperative-perception pipeline architecture, opportunity admission/suppression, and verification timing model.
2. **Figure 2 (`figures/fig2_offered_load.png`):** Receiver offered load distribution calculated across synthetic verification service budgets from a single common fixed 10 Hz arrival baseline (144 receiver observations across 3 seeds).
3. **Figure 3 (`figures/fig3_paired_comparison.png`):** Twenty-seed paired policy evaluation (48 sources, intersection scenario, 3 ms service) showing policy means and paired differences with 95% Student-t confidence intervals.

## Build and Export Verification

From the project root (`cpstudy/`), execute:

```sh
python3 scripts/build_submission_exports.py
```

The build script copies the canonical `manuscript/manuscript.md`, mirrors only referenced figures to `submission_package/figures/` and `references/references.bib`, uses Pandoc and headless Chrome to generate standalone exports, archives `submission_package.zip`, and updates the SHA-256 manifest.

To verify all recomputed results and dynamic linkage against the canonical manuscript:

```sh
python3 scripts/verify_rework_results.py
```

## Submission Readiness Status (Review Draft)

- **Internal Review Draft:** This package is maintained as a review draft. The cover letter explicitly notes that formal submission is pending unanimous author review and written sign-off.
- **Author Declarations & Data Availability:** CRediT authorship contributions, conflict-of-interest disclosures, funding statements, and data-availability arrangements are clearly marked as internal draft placeholders pending direct confirmation and release authorization from the co-authors.
- **Audit Verification:** All abstract numbers, narrative metrics, and Tables 2–6 are verified via `scripts/verify_rework_results.py` directly against raw packet traces and per-run summaries.
- **Phase 8 Release Gate:** In accordance with project protocol, release approval remains provisional pending independent external review, local TeX engine compilation, and formal co-author sign-off.
