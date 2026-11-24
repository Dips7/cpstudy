# Author Details & Institutional Affiliations

Standard reproducible author records and templates for research manuscripts, journal submission portals, and documentation generation.

---

## 1. Author Directory

### Dipesh Gurung
* **Full Name:** Dipesh Gurung
* **Academic Degrees:** M.Sc.
* **Role / Position:** Research Associate
* **Department:** Research Department
* **Institution:** Lord Buddha Education Foundation (LBEF College)
* **Postal Address:** Opposite to Maitidevi Temple, Kathmandu 44600, Nepal
* **Primary Email:** `dipesh.gurung@lbef.edu.np`
* **Personal Email:** `dips.grg7@gmail.com`
* **ORCID:** [0009-0009-0335-2267](https://orcid.org/0009-0009-0335-2267)
* **GitHub Profile:** [https://github.com/Dips7](https://github.com/Dips7)
* **CRediT Roles:** Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing – original draft, Visualization, Project administration.

### Binod Bhattarai (Corresponding Author)
* **Full Name:** Binod Bhattarai
* **Role / Position:** Ph.D. Scholar
* **Department:** Department of Computer Science and Engineering, School of Sciences
* **Institution:** Noida International University (NIU)
* **Location:** Greater Noida, Uttar Pradesh 203201, India
* **Email:** `binoth25@gmail.com`
* **ORCID:** [0009-0006-6691-5264](https://orcid.org/0009-0006-6691-5264)
* **CRediT Roles:** Conceptualization, Investigation, Validation, Writing – review & editing, Supervision.

### Prof. Dr. R.N. Thakur
* **Full Name:** Prof. Dr. R.N. Thakur (also cited as Dr. R N Thakur)
* **Role / Position:** Dean, Academics
* **Department:** Academics
* **Institution:** Lord Buddha Education Foundation (LBEF College)
* **Location:** Kathmandu 44600, Nepal
* **Email:** `rn.thakur@lbef.edu.np`
* **ORCID:** [0000-0003-3911-4358](https://orcid.org/0000-0003-3911-4358)
* **CRediT Roles:** Conceptualization, Supervision, Methodology, Resources, Writing – review & editing.

---

## 2. Manuscript Snippets

### A. LaTeX (`authblk` Package)
```latex
\usepackage{authblk}

\author[1]{Dipesh Gurung\thanks{ORCID: \url{https://orcid.org/0009-0009-0335-2267}}}
\author[2,*]{Binod Bhattarai\thanks{Corresponding Author: \texttt{binoth25@gmail.com}; ORCID: \url{https://orcid.org/0009-0006-6691-5264}}}
\author[1]{Prof. Dr. R.N. Thakur\thanks{ORCID: \url{https://orcid.org/0000-0003-3911-4358}}}

\affil[1]{Research Department, Lord Buddha Education Foundation (LBEF College), Kathmandu 44600, Nepal}
\affil[2]{Department of Computer Science and Engineering, School of Sciences, Noida International University, Greater Noida, Uttar Pradesh 203201, India}
```

### B. Typst
```typst
#set document(
  title: "Manuscript Title",
  author: ("Dipesh Gurung", "Binod Bhattarai", "Prof. Dr. R.N. Thakur"),
)

#align(center)[
  #text(17pt, weight: "bold")[Manuscript Title] \ \
  #text(12pt)[
    *Dipesh Gurung*#super[1], *Binod Bhattarai*#super[2,\*], *Prof. Dr. R.N. Thakur*#super[1]
  ] \ \
  #text(10pt)[
    #super[1] Research Department, Lord Buddha Education Foundation (LBEF College), Kathmandu 44600, Nepal \
    #super[2] Department of Computer Science and Engineering, School of Sciences, Noida International University, Greater Noida 203201, India \
    \* Corresponding author: binoth25\@gmail.com
  ]
]
```

### C. Plain Text / Word Title Page Block
```text
Dipesh Gurung 1, Binod Bhattarai 2,*, Prof. Dr. R.N. Thakur 1

1 Research Department, Lord Buddha Education Foundation (LBEF College), Kathmandu 44600, Nepal
2 Department of Computer Science and Engineering, School of Sciences, Noida International University, Greater Noida, Uttar Pradesh 203201, India

* Corresponding Author:
Full Name: Binod Bhattarai
Position: Ph.D. Scholar
Department: Department of Computer Science and Engineering, School of Sciences
Institution: Noida International University (NIU)
Location: Greater Noida, Uttar Pradesh 203201, India
Email: binoth25@gmail.com
ORCID: 0009-0006-6691-5264
```

### D. CRediT Author Statement
```text
CRediT Author Statement:
Dipesh Gurung: Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing – original draft, Visualization, Project administration.
Binod Bhattarai: Conceptualization, Investigation, Validation, Writing – review & editing, Supervision.
Prof. Dr. R.N. Thakur: Conceptualization, Supervision, Methodology, Resources, Writing – review & editing.
```

---

## 3. Programmatic Access in Python

You can load these details directly into any build script:

```python
import json
from pathlib import Path

METADATA_FILE = Path(__file__).resolve().parent / "author_metadata.json"

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    author_data = json.load(f)

for author in author_data["authors"]:
    print(f"{author['name']} - {author['position']}, {author['full_affiliation']}")
```
