# Phase 8 Provisional Internal Technical Audit (Self-Audit)

**Audit Date:** 2026-11-23  
**Auditor Classification:** Worker Self-Audit (**Independent outside review remains PENDING**)  
**Status:** PROVISIONAL TECHNICAL CHECK (Phase 8 release sign-off remains OPEN pending independent external review and formal all-author approval)  
**Script Artifact:** `scripts/verify_rework_results.py`

---

## 1. Audit Methodology & Dynamic Manuscript Linkage

To eliminate any risk of verification drift, `scripts/verify_rework_results.py` contains **zero hardcoded reference values**. Instead, it dynamically parses reference metrics from **eight specific manuscript locations** in `manuscript/manuscript.md` at runtime and tests that calculations match the manuscript at its exact displayed decimal precision:

1. **Abstract:** Parses policy means (Fixed 94.75%, Radio 81.98%, Joint 15.84%, Calibrated 55.91%), paired contrasts (+40.07 pp, CI 4.18 pp, $d_z = 4.49$; 38.83 pp below Fixed, 26.07 pp below Radio), and offered load (0.571 at 3 ms, 1.143 at 6 ms).
2. **Table 2:** Parses receiver arrival rates, offered load distribution, and receivers > 1.0 across 5 service budgets.
3. **Table 3:** Parses trace-audited stress sweep outcomes, sample sizes, and confidence intervals.
4. **Table 4:** Parses threshold ablation condition outcomes, sample sizes, and confidence intervals.
5. **Table 5:** Parses 20-seed paired comparison policy means, sample sizes, and confidence intervals.
6. **Table 6:** Parses 20-seed paired difference contrasts, confidence intervals, and Cohen's $d_z$.
7. **Section 5.1 Narrative:** Parses the 48-source 3 ms factorial cell means and confidence intervals for all 5 policies.
8. **Section 5.6 Narrative:** Parses trigger attribution decrease totals, backlog-only counts, and percentage.

*Scope Note on Dynamic Coverage:* The parser specifically tests these eight primary reporting locations. Secondary or repeated narrative mentions of these numbers elsewhere in the text (such as in the Introduction, Discussion, or Conclusion) are not individually parsed by the script.

### Displayed-Precision Assertions:
Every check formats the calculated float to the exact number of decimal places displayed in the manuscript (e.g. 2 decimal places for percentages, 3 for offered load) and asserts string equality (`assert_displayed_precision`).

### Execution Tiers:
- **Tier A (Source Trace Recomputation):**
  - **Receiver Offered Load (Table 2 & Abstract):** Iterates over every packet reception (`kind == '0'`, `event_type == 'reception'`) in $[1.0\text{ s}, 5.0\text{ s})$ across all 48 receivers and 3 seeds in raw ns-3 network event streams (`network-events.csv.gz`). Recomputes $\lambda_r$ and offered load $\rho_r$ across 144 receiver observations, asserting agreement with Table 2 and the Abstract at displayed precision.
  - **Terminal Lifecycle Replay:** Replays opportunity demand partitions and terminal states directly from underlying `network-opportunities.csv.gz` and `events.jsonl.gz` for sampled runs (`fixed_s1`, `radio_s1`, `joint_s1`, `calibrated_s1`), verifying exact conservation.
- **Tier B (Per-Run Summary Consistency & Statistical Aggregation):**
  - **Per-Run Consistency Assertion:** Across all 80 paired run records, asserts that derived rate (`succ / denom`) strictly equals the stored `opportunity_success_rate` to within $10^{-9}$.
  - **Statistical Contrasts & Uncertainty:** Recomputes means, Student-$t$ 95% confidence intervals, and effect sizes across 20 matched seeds (Tables 5 & 6), 35 ablation runs (Table 4), 65 trace-audited stress runs (Table 3), and factorial cells (Section 5.1).

---

## 2. Reproducible Script Execution & Output

### Execution Command:
```sh
python3 scripts/verify_rework_results.py
```

### Complete Command Output (Exit Code 0):
```text
REWORK NUMERICAL RECOMPUTATION & MANUSCRIPT DYNAMIC LINKAGE AUDIT
Parsing canonical manuscript text from: manuscript/manuscript.md
Successfully parsed Abstract, Section 5.1, Section 5.6, and Tables 2-6 directly from manuscript.md

======================================================================
1. DIRECT RECOMPUTATION OF OFFERED LOAD FROM RAW RECEPTION TRACES
======================================================================
Sample count: 144 receiver-seed observations (48 receivers x 3 seeds)
Service  1.0ms: arrival=190.422 (ms: 190.422), mean_rho=0.190 (ms: 0.190), median_rho=0.218 (ms: 0.218), max_rho=0.304 (ms: 0.304), >1.0= 0.00 (ms: 0.00)
Service  3.0ms: arrival=190.422 (ms: 190.422), mean_rho=0.571 (ms: 0.571), median_rho=0.654 (ms: 0.654), max_rho=0.911 (ms: 0.911), >1.0= 0.00 (ms: 0.00)
Service  6.0ms: arrival=190.422 (ms: 190.422), mean_rho=1.143 (ms: 1.143), median_rho=1.309 (ms: 1.309), max_rho=1.823 (ms: 1.823), >1.0=29.67 (ms: 29.67)
Service  7.5ms: arrival=190.422 (ms: 190.422), mean_rho=1.428 (ms: 1.428), median_rho=1.636 (ms: 1.636), max_rho=2.278 (ms: 2.278), >1.0=32.67 (ms: 32.67)
Service 10.0ms: arrival=190.422 (ms: 190.422), mean_rho=1.904 (ms: 1.904), median_rho=2.181 (ms: 2.181), max_rho=3.038 (ms: 3.038), >1.0=38.00 (ms: 38.00)
PASS: All Table 2 and Abstract offered-load metrics match manuscript at displayed precision.

======================================================================
2. SAMPLE RUN-LEVEL AUDIT FROM UNDERLYING OPPORTUNITY & EVENT TRACES
======================================================================
Sample run fixed_s1       : evaluated_demand=21322, terminal_success=20332, rate=95.36% (exact match to summary.json)
Sample run radio_s1       : evaluated_demand=21322, terminal_success=15767, rate=73.95% (exact match to summary.json)
Sample run joint_s1       : evaluated_demand=21322, terminal_success=2118, rate=9.93% (exact match to summary.json)
Sample run calibrated_s1  : evaluated_demand=21322, terminal_success=11082, rate=51.97% (exact match to summary.json)
PASS: Underlying opportunity & event traces verified for sample runs; exact conservation confirmed.

======================================================================
3. STATISTICAL AGGREGATION ACROSS 20-SEED PAIRED COMPARISON
======================================================================
Per-run rate consistency asserted across all 80 paired summary.json records (derived == stored rate to 1e-9).
Policy fixed     : n=20, mean=94.75% (ms Table 5: 94.75%), CI95 half-width=0.98pp (ms Table 5: 0.98pp)
Policy radio     : n=20, mean=81.98% (ms Table 5: 81.98%), CI95 half-width=3.95pp (ms Table 5: 3.95pp)
Policy joint     : n=20, mean=15.84% (ms Table 5: 15.84%), CI95 half-width=6.54pp (ms Table 5: 6.54pp)
Policy calibrated: n=20, mean=55.91% (ms Table 5: 55.91%), CI95 half-width=4.37pp (ms Table 5: 4.37pp)

--- Paired Contrasts (Table 6 & Abstract) ---
Contrast Calibrated - joint  : mean=+40.07pp (ms Table 6: +40.07pp), CI95=4.18pp (ms Table 6: 4.18pp), dz=+4.49 (ms Table 6: 4.49)
Contrast Calibrated - fixed  : mean=-38.83pp (ms Table 6: −38.83pp), CI95=4.49pp (ms Table 6: 4.49pp), dz=-4.05 (ms Table 6: −4.05)
Contrast Calibrated - radio  : mean=-26.07pp (ms Table 6: −26.07pp), CI95=2.74pp (ms Table 6: 2.74pp), dz=-4.45 (ms Table 6: −4.45)
PASS: All Table 5, Table 6, and Abstract paired metrics match manuscript at displayed precision.

======================================================================
4. TRACE-AUDITED STRESS SWEEP (Table 3)
======================================================================
Stress v=3.0ms, pol=calibrated: n=2, mean=53.04% (ms Table 3: 53.04%), CI95=13.49pp
Stress v=3.0ms, pol=joint     : n=3, mean=11.42% (ms Table 3: 11.42%), CI95= 6.05pp
Stress v=3.0ms, pol=radio     : n=3, mean=77.32% (ms Table 3: 77.32%), CI95=13.28pp
Stress v=3.0ms, pol=dcc       : n=3, mean=43.80% (ms Table 3: 43.80%), CI95= 4.93pp
Stress v=6.0ms, pol=calibrated: n=1, mean= 3.54% (ms Table 3: 3.54%), CI95=Not estimable
Stress v=6.0ms, pol=joint     : n=2, mean= 2.74% (ms Table 3: 2.74%), CI95=13.60pp
Stress v=6.0ms, pol=dcc       : n=3, mean=43.26% (ms Table 3: 43.26%), CI95= 4.53pp
PASS: All Table 3 trace-audited stress metrics match manuscript at displayed precision.

======================================================================
5. THRESHOLD ABLATION (Table 4)
======================================================================
Ablation Fixed 10 Hz         : n=5, mean=94.06% (ms Table 4: 94.06%), CI95=2.83pp (ms Table 4: 2.83pp)
Ablation Radio-only          : n=5, mean=81.49% (ms Table 4: 81.49%), CI95=9.88pp (ms Table 4: 9.88pp)
Ablation Uncalibrated joint  : n=5, mean=13.01% (ms Table 4: 13.01%), CI95=3.73pp (ms Table 4: 3.73pp)
Ablation Queue threshold 4   : n=5, mean=21.37% (ms Table 4: 21.37%), CI95=9.33pp (ms Table 4: 9.33pp)
Ablation Queue threshold 8   : n=5, mean=47.42% (ms Table 4: 47.42%), CI95=12.78pp (ms Table 4: 12.78pp)
Ablation Queue threshold 16  : n=5, mean=55.31% (ms Table 4: 55.31%), CI95=3.80pp (ms Table 4: 3.80pp)
Ablation Queue threshold 24  : n=5, mean=54.29% (ms Table 4: 54.29%), CI95=4.62pp (ms Table 4: 4.62pp)
PASS: All Table 4 ablation metrics match manuscript at displayed precision.

======================================================================
6. FACTORIAL CELL (Section 5.1) & ATTRIBUTION (Section 5.6)
======================================================================
Factorial 48src 3ms fixed     : n=3, mean=95.28% (ms Section 5.1: 95.28%), CI95=1.79pp (ms Section 5.1: 1.79pp)
Factorial 48src 3ms radio     : n=3, mean=86.03% (ms Section 5.1: 86.03%), CI95=20.65pp (ms Section 5.1: 20.65pp)
Factorial 48src 3ms joint     : n=3, mean=13.30% (ms Section 5.1: 13.30%), CI95=1.71pp (ms Section 5.1: 1.71pp)
Factorial 48src 3ms receiver  : n=3, mean=13.30% (ms Section 5.1: 13.30%), CI95=1.71pp (ms Section 5.1: 1.71pp)
Factorial 48src 3ms dcc       : n=3, mean=45.86% (ms Section 5.1: 45.86%), CI95=0.24pp (ms Section 5.1: 0.24pp)

Trigger attribution (Joint decreases): total=1330 (ms Section 5.6: 1330), backlog_only=1242 (ms Section 5.6: 1242), pct=93.38% (ms Section 5.6: 93.38%)
PASS: Factorial cell and trigger attribution match manuscript narrative at displayed precision.

======================================================================
ALL NUMERIC CHECKS & MANUSCRIPT DYNAMIC ASSERTIONS PASSED AT DISPLAYED PRECISION.
======================================================================
```

---

## 3. TeX, Figures & Packaging Status (Elsevier *Vehicular Communications*)

- **Elsevier Package Alignment:** Manuscript formatted strictly as per *Vehicular Communications* Guide for Authors (structured author block with affiliations $a, b$, 4 bounded highlights $\le 85$ chars, 206-word abstract, decimal section numbering, CRediT statement, and competing interest declarations).
- **Publication Figures & Provenance:** 3 high-resolution publication figures generated dynamically from audited trace data and embedded into manuscript:
  - `figures/fig1_pipeline_timing.png` (Section 3.1: architecture and timing model).
  - `figures/fig2_offered_load.png` (Section 5.2: receiver offered load distribution dynamically loaded from `utilization_recomputed.json`; text, caption, and title explicitly clarify this is an analytical calculation applying service durations to a single common baseline of simulation-derived packet-reception observations across 144 receiver observations, not separate runs).
  - `figures/fig3_paired_comparison.png` (Section 5.5: 20-seed paired comparison policy means and contrast intervals dynamically loaded from `paired_policy_recomputed.csv` and `paired_contrasts_recomputed.csv`; contrast annotations positioned inward to eliminate clipping within $[-58, 58]$ range; caption updated to describe confidence intervals).
- **PDF Generation:** `submission_package/MANUSCRIPT.pdf` rendered directly via Pandoc HTML5 embedded assets and headless Google Chrome.
- **LaTeX Status:** Standalone LaTeX export `submission_package/MANUSCRIPT.tex` generated cleanly with single-backslash math and embedded figure references. Local TeX compilation remains **PENDING / UNCOMPILED** due to the absence of a local TeX engine (`pdflatex`, `xelatex`, `typst`).
- **Clean Export Package:** `submission_package.zip` and `submission_package/figures/` updated to include strictly the 3 figures referenced in the manuscript, removing older unreferenced figures. SHA-256 manifest verified.
- **Author Declarations & Cover Letter Status:** Cover letter revised to an internal review draft removing overclaims (realistic timeliness, queue stability transitions, causal throttling, and "less understood") in favor of specific literature context (Thandavarayan 2020, Muhammad 2019). Submission and declarations (originality, CRediT, competing interests, funding, data availability) remain marked as draft placeholders pending explicit author verification and unanimous written approval. Public GitHub repository claims replaced with an authorized request mechanism.

---

## 4. Limitations Register Alignment (L01–L20)

All 20 limitations in `evidence/limitations_register.md` are accounted for in the manuscript:
- 16 consolidated items in Section 7 & Table 7 (L01–L13, L16, L17, L20).
- 4 items in dedicated sections: L14 (Section 5.6 descriptive trigger attribution), L15 (Section 4 cross-sectional averaging), L18 (Section 6 conditional arithmetic / Theorem 2 removed), L19 (Section 6 & 7 processor-cycle waste removed).

---

## 5. Citation & Reference Audit Reconciliation

Following targeted reference auditing and first-use order reconciliation, the cited bibliography in `manuscript/manuscript.md` and `references/references.bib` comprises eleven references strictly numbered in first-appearance order (1–11):
1. **Strict First-Use Appearance Order:**
   - [1] Thandavarayan et al. (2020) (congestion control evaluation) & [2] Thandavarayan et al. (2020) (message generation) introduced in Section 1 (line 17).
   - [3] ETSI TS 103 324 V2.1.1 (2023) & [4] ETSI TS 102 687 V1.2.1 (2018) introduced in Section 1 (line 17) as standards context.
   - [5] Muhammad et al. (2019) (security broadcast delay baseline) introduced in Section 1 (line 17).
   - [6] Wang et al. (2023) (AoI status updates) & [7] Chen et al. (2025) (Age of Computing) introduced in Section 1 (line 17).
   - [8] Tian, Shi, & Chen (2026) (*Sense2Com*) introduced in Section 1 (line 17). Authors corrected to Jin Tian, Yan Shi, and Shanzhi Chen. Contrast softened to describe its stated focus on transmission scheduling and computation offloading via MARL rather than asserting what it omits.
   - [9] Henderson et al. (2008) (*ACM SIGCOMM 2008 Demonstration*, p. 527) introduced in Section 3.1 for the ns-3 simulator architecture.
   - [10] ns-3 project (2025) (*ns-3.46.1 Release Information and ns-3.46 Model Library Documentation*) introduced in Section 3.1 for 802.11p `AdhocWifiMac` and log-distance propagation model behavior.
   - [11] Kleinrock (1975) (*Queueing Systems, Volume I: Theory*) introduced in Section 3.2 for the $M/G/1$ Pollaczek–Khinchine waiting-time equation and theoretical assumptions.
2. **Access-Depth & Matrix Alignment:** Sense2Com access-depth verified across `manuscript/manuscript.md`, `references/literature_matrix.csv`, and `evidence/citation_audit.md` as publisher record, abstract, problem formulation, and coordination model inspected.
3. **Deferred Candidates:** DPBV (IEEE IV 2025) and Miyata et al. (GLOBECOM 2026, to appear) explicitly deferred pending full-text retrieval and published proceedings, respectively.
4. **Standards & Boundaries:** ETSI specifications retained as standards context; bounded, non-systematic review phrasing maintained.

---

## 6. Release Gate Status: PROVISIONAL AUDIT (RELEASE PENDING)

| Phase 8 Item | Status | Action Required |
|---|:---:|---|
| Direct trace recomputations & dynamic assertions | **VERIFIED** | Runnable script `scripts/verify_rework_results.py` passes with exit code 0. |
| Independent outside review | **PENDING** | Must be conducted by an outside reviewer who did not perform the analysis. |
| LaTeX compilation | **PENDING** | Awaiting environment with a TeX compiler. |
| Author statements & declarations | **PENDING** | Co-authors must confirm CRediT, funding, ethics, and competing interests. |
| Final all-author submission approval | **PENDING** | Formal review and unanimous sign-off required by all co-authors. |

**Conclusion:** The internal technical verification passes cleanly with dynamic manuscript linkage across the Abstract, narrative claims, and Tables 2–6, enforcing displayed-precision comparisons and per-run rate consistency. The project is frozen as a **canonical review draft**. Full Phase 8 sign-off and release approval remain provisional pending independent outside review, TeX compilation, and all-author formal approval.
