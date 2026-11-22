# 🏛️ System Architecture & Algorithmic Design

## 1. Pipeline Overview
The Automated Resume Screening Tool executes a decoupled, multi-stage retrieval and ranking pipeline:

```
[Raw Files: PDF/DOCX/TXT] ──> [Text Extraction] ──> [Regex Normalization]
                                                          │
          ┌───────────────────────────────────────────────┴───────────────────────────────┐
          ▼                                                                               ▼
[Taxonomy & Alias Mapper]                                                      [TF-IDF N-gram Matrix]
[RapidFuzz Fuzzy Matcher]                                                      [Cosine Similarity]
[Experience & Education Regex]                                                            │
          │                                                                               │
          └───────────────────────────────────────┬───────────────────────────────────────┘
                                                  ▼
                                      [Hybrid ATS Scoring Formula]
                                                  ▼
                                      [Decision Threshold Engine]
                                                  ▼
                               [Outputs: CSV, Brief, UI, REST Endpoints]
```

## 2. Hybrid Scoring Mathematics
Unlike raw keyword ATS tools that are easily tricked by keyword stuffing, this engine calculates an explainable composite score:

$$\text{Composite Score} = w_{\text{sim}} \cdot S_{\text{norm}} + w_{\text{skills}} \cdot C_{\text{must}} + w_{\text{exp}} \cdot E_{\text{ratio}} - P_{\text{gaps}}$$

Where:
- $w_{\text{sim}} = 0.35$: Weight for semantic TF-IDF cosine similarity.
- $S_{\text{norm}} = \min\left(1.0, \frac{\text{Cosine Similarity}}{0.35}\right)$: Normalized semantic document alignment.
- $w_{\text{skills}} = 0.50$: Weight for core must-have technical skill coverage.
- $C_{\text{must}} = \frac{\text{Must-Have Hits}}{\max(1, \text{Total Must-Have})}$: Direct coverage fraction of required skills.
- $w_{\text{exp}} = 0.15$: Experience tenure factor.
- $E_{\text{ratio}} = \min\left(1.0, \frac{\text{Candidate Exp Years}}{\text{Required Exp Years}}\right)$.
- $P_{\text{gaps}} = \min(0.12, 0.02 \times \text{Missing Gaps})$: Bounded deduction for missing mandatory criteria.

## 3. Threshold Gates
- **Shortlisted:** $\text{Score} \ge 0.65$ and missing must-haves $\le 3$.
- **Under Review:** $0.38 \le \text{Score} < 0.65$.
- **Rejected:** $\text{Score} < 0.38$.
