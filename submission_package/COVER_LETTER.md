# Cover Letter

To:  
Editor-in-Chief  
*Vehicular Communications*  
Elsevier

Date: November 24, 2026

**Subject: Submission of Original Research Article: "Receiver Feedback and Timely Source-Update Availability in a Cooperative-Perception Simulation"**

Dear Editor-in-Chief,

We are pleased to submit our original research manuscript titled **"Receiver Feedback and Timely Source-Update Availability in a Cooperative-Perception Simulation"** for consideration for publication as a regular research article in *Vehicular Communications*.

### Context and Summary of Findings
Cooperative perception relies on broadcast V2V communication to exchange status and sensor updates among nearby vehicles. Prior research has separately examined access-layer congestion control (e.g., Thandavarayan et al., 2020) and security-related broadcast delays (e.g., Muhammad et al., 2019). This study evaluates how sender transmission control policies affect timely authenticated source-update availability in a simulation combining ns-3.46.1 802.11p broadcast contention with a deterministic synthetic receiver verification queue:

1. **Receiver Offered Load:** In an arrival analysis applying configured service durations to a single common baseline of simulation-derived packet-reception observations under fixed 10 Hz transmission (144 receiver observations across 3 seeds), calculated mean receiver offered load rises from 0.190 at 1 ms to 0.571 at 3 ms and 1.143 at 6 ms synthetic service budgets. The study explicitly distinguishes offered load ($\rho = \lambda \tau$) from measured CPU execution or physical worker saturation.
2. **Paired Policy Comparison:** In an exploratory 20-seed paired comparison at 48 sources, intersection geometry, and 3 ms service, mean same-opportunity timely success was 94.75% for fixed 10 Hz transmission, 81.98% for the project radio-only controller, 55.91% for calibrated feedback, and 15.84% for uncalibrated joint feedback. Calibrated feedback exceeded uncalibrated feedback by 40.07 percentage points (paired 95% t interval half-width 4.18 points; Cohen's $d_z = 4.49$), while remaining below fixed and radio-only control.
3. **Trigger Classification:** In the saved controller decision record, 93.38% (1,242 of 1,330) of recorded rate decreases for the uncalibrated joint policy were labeled as `backlog_only`.

### Simulation Scope and Boundaries
The simulation models verification using synthetic service durations, assumes valid signatures, and does not execute cryptographic algorithms, benchmark hardware, or evaluate object-level tracking, driving decisions, or safety outcomes. Findings characterize the specified simulation model and configurations.

### Author Declarations
- **Originality:** The authors confirm that this manuscript represents an original contribution that has not been published previously and is not currently under formal consideration for publication elsewhere.
- **Author Approval & CRediT:** All listed authors have contributed significantly to the work, reviewed and approved the final manuscript, confirmed their respective CRediT roles, and agreed with its submission to *Vehicular Communications*.
- **Competing Interests:** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
- **Acknowledgements:** Computational infrastructure, research facilities, and lab resources were supported by the Department of Research and the Intel AI Unnati Lab at Lord Buddha Education Foundation (LBEF College), Kathmandu, Nepal, and the School of Sciences at Noida International University.
- **Funding:** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.
- **Data & Replication Code Availability:** Simulation configuration files, processed evaluation datasets, figures, and reproducible verification scripts are publicly archived at GitHub: https://github.com/Dips7/cpstudy.

Sincerely,

**Binod Bhattarai** (Corresponding Author)  
Ph.D. Scholar, Department of Computer Science and Engineering, School of Sciences  
Noida International University (NIU), Greater Noida, Uttar Pradesh 203201, India  
Email: `binoth25@gmail.com` | ORCID: 0009-0006-6691-5264

*On behalf of:*  
- **Dipesh Gurung**, Research Associate, Lord Buddha Education Foundation (LBEF College), Kathmandu, Nepal (`dipesh.gurung@lbef.edu.np`)  
- **Prof. Dr. R. N. Thakur**, Dean of Academics, Lord Buddha Education Foundation (LBEF College), Kathmandu, Nepal (`rn.thakur@lbef.edu.np`)
