# Blog Outlines — Evidence-Based Updates

**Update Date:** 2025-12-31
**Status:** ✅ ALL THREE OUTLINES CORRECTED
**Evidence Basis:** [00-research-summary-FINAL.md](findings/00-research-summary-FINAL.md)

---

## Summary of Changes

All three blog post outlines have been updated to reflect corrected, evidence-based research with proper sourcing and scope limitations.

### Key Corrections Applied

1. **"100% accuracy" → "100% match (sample-only)"**
   - Properly scoped validation claims to 3-4 golden vectors
   - Added explicit "sample-only validation" notes

2. **"10-20 iterations per beam" → REMOVED**
   - No source for specific iteration counts
   - Replaced with "Engineers commonly use trial-and-error workflows"

3. **"ML requires thousands of samples" → Evidence-based**
   - Now cites Vabalas et al. (2019) PLOS One on overfitting
   - Softened "thousands" to "large datasets" with academic citation

4. **"Majority of engineers" → "Engineers commonly"**
   - Removed unsupported quantifier
   - Changed to descriptive language based on academic papers

5. **Added evidence basis links**
   - All outlines link to 00-research-summary-FINAL.md
   - Status updated to "OUTLINE — EVIDENCE-CORRECTED"

6. **Added sources/references sections**
   - Primary sources (peer-reviewed papers) listed
   - Secondary sources clearly labeled
   - Internal documentation linked

---

## Blog 01: Making Structural Design Intelligent

**File:** [blog-posts/01-smart-library/outline.md](blog-posts/01-smart-library/outline.md)

### Changes Made

**Hook Section (Line 37):**
- **Before:** "achieving 100% accuracy against golden test vectors"
- **After:** "All features achieved 100% match against IS 456 golden test vectors (sample-only validation) and are fully deterministic and traceable"

**Section 1 (Line 59):**
- **Before:** "10-20 iterations per beam (time waste)"
- **After:** "Engineers commonly use trial-and-error workflows, iteratively revising until code-compliant (time waste)"

**Section 2 (Line 97):**
- **Before:** "Small data (10-15 examples, not 10,000)"
- **After:** "Small data (research shows small samples cause overfitting and bias — Vabalas et al. 2019)"

**Section 6 — Results Table (Lines 399-403):**
- **Before:** "Accuracy | 100%"
- **After:** "Match Rate | 100% match (sample-only)"
- **Added:** ⚠️ Sample-only validation note in key findings

**Section 8 — Takeaway 4 (Line 483):**
- **Before:** "3 golden vectors sufficient for validation... Not all problems need 10,000 training samples"
- **After:** "Deterministic Methods Are Data-Efficient... Validated with 3-4 golden vectors (sample-only)... ML with small samples leads to overfitting (Vabalas et al. 2019)"

**Added:**
- Evidence basis link in header
- Sources & References section with primary/secondary sources
- Internal documentation links

---

## Blog 02: Deterministic ML

**File:** [blog-posts/02-deterministic-ml/outline.md](blog-posts/02-deterministic-ml/outline.md)

### Changes Made

**Hook Section (Line 27):**
- **Before:** "Small datasets (10-100 examples, not 10,000)"
- **After:** "Small datasets (research shows ML overfits and produces biased estimates — Vabalas et al. 2019)"

**Section 2 — Decision Matrix (Line 88):**
- **Before:** ">1000 samples" vs "<100 samples"
- **After:** "Large datasets" vs "Small datasets (overfitting risk)"
- **Added:** Note explaining "Large" vs "small" depends on complexity, with Vabalas et al. citation

**Section 2 — Engineering Characteristics Table (Lines 100-109):**
- **Before:** "10-15 verified examples" vs "10,000+ training samples" | "100% accuracy required"
- **After:** "Small (3-4 IS 456 golden vectors for validation)" vs "Large (thousands+ samples)" | "Deterministic verification against worked examples"

**Added:**
- Evidence basis link in header
- Sources & References section with primary sources (Vabalas, Figueroa, Panko)
- Note distinguishing our approach from ML use cases

---

## Blog 03: Sensitivity Analysis

**File:** [blog-posts/03-sensitivity-analysis/outline.md](blog-posts/03-sensitivity-analysis/outline.md)

### Changes Made

**Header:**
- Added "OUTLINE — EVIDENCE-CORRECTED" status
- Added evidence basis link to 00-research-summary-FINAL.md

**Added:**
- Sources & References section with:
  - Primary sources: Kytinou et al. (2021), Lagrangian studies, PCE studies
  - Secondary sources: Poh & Chen (1998)
  - Standards: IS 456:2000, SP:16
  - Internal documentation links

**Note:** Blog 03 is the most technically focused and had fewer overclaims to correct. Main update was adding proper academic sourcing for sensitivity analysis methods.

**Additional correction (2025-12-31):**
- Blog 03 hook also contained an unsupported "10-20 iterations" phrasing; now replaced with "iteratively revising until code-compliant".

---

## Evidence Levels Applied

### 🟢 PRIMARY Sources Used in Outlines
- **Vabalas et al. (2019)** — ML overfitting with small samples (*PLOS One*)
- **Panko (2008)** — Spreadsheet error rates (*JOEU*)
- **Poh & Chen (1998)** — BDAS productivity validation (*CME*)
- **Kytinou et al. (2021)** — Sensitivity analysis for RC beams (*Applied Sciences*)
- **Our testing** — 100% match on 3-4 golden vectors (sample-only)

### 🟡 SECONDARY Sources Used
- **Chang et al. (2020)** — Trial-and-error workflows (*ICML Proceedings*)
- **EuSpRIG** — Research synthesis (aggregator)
- **Nature (2025)** — DRL for beam optimization (contrast example)

### 🟠 ANECDOTAL (Removed or Clearly Labeled)
- Removed: "10-20 iterations per beam" (no source)
- Removed: "Majority of engineers" (no usage statistics)
- Softened: Specific sample size thresholds (">1000" vs "<100")

---

## Blog-Ready Claims — Final Versions

### For Blog 01 (Smart Library)

**Validation:**
> "Our sensitivity analysis, predictive validation, and constructability features achieved 100% match against 3-4 golden vectors from IS 456 worked examples (sample-only validation). All outputs are deterministic and traceable to code clauses."

**ML vs. Classical:**
> "Research shows that machine learning with small sample sizes produces overfitting and biased performance estimates (Vabalas et al. 2019 PLOS One). Deterministic methods based on physical equations require zero training data."

### For Blog 02 (Deterministic ML)

**Sample Size:**
> "Academic research shows that insufficient sample sizes lead to ML overfitting and biased performance estimates. For code-compliant design with verified test cases, deterministic methods based on physical equations (IS 456) require zero training data."

**Comparison Table:**
> "Our use case: Small data (3-4 IS 456 golden vectors for validation), must cite code clauses, deterministic verification required. Typical ML use case: Large datasets (thousands+ samples), probabilistic predictions, statistical accuracy metrics."

### For Blog 03 (Sensitivity Analysis)

**Academic Foundation:**
> "Sensitivity analysis for reinforced concrete beams is well-established in peer-reviewed literature using variance-based methods (Sobol indices), cost optimization (Lagrangian multipliers), and perturbation analysis (Kytinou et al. 2021 Applied Sciences)."

---

## Quality Checklist — All Blogs

### ✅ Completed

- [x] All "100% accuracy" scoped to "100% match (sample-only)"
- [x] Removed unverified iteration counts ("10-20 iterations")
- [x] Removed unsupported quantifiers ("Majority of engineers")
- [x] Softened ML sample requirements with academic citations
- [x] Added evidence basis links in headers
- [x] Added sources/references sections to all three outlines
- [x] Clearly distinguished primary vs. secondary sources
- [x] Linked internal documentation

### Ready for Full Draft Writing

All three blog outlines now have:
1. ✅ Evidence-based claims with proper sources
2. ✅ Scope limitations clearly stated
3. ✅ Primary research cited for key claims
4. ✅ Secondary sources labeled appropriately
5. ✅ No overclaims on validation or usage statistics
6. ✅ Sources/references sections ready for expansion

---

## Next Steps for Blog Writing

**When writing full drafts:**

1. **Expand sources sections** — Add full citations in APA format
2. **Add inline citations** — Link to sources in blog text, not just at end
3. **Use exact quotes** — Where appropriate, quote primary sources directly
4. **Add evidence tags internally** — For fact-checking (don't show in published blog)
5. **Include disclaimers** — "Sample-only validation" where needed
6. **Link to horror stories** — EuSpRIG documented cases (secondary source)

**Writing order recommendation:**
1. Blog 02 first (most controversial, HackerNews-ready)
2. Blog 01 second (broader appeal, Dev.to + Medium)
3. Blog 03 third (technical deep-dive, Medium longform)

---

## Files Updated

1. ✅ [blog-posts/01-smart-library/outline.md](blog-posts/01-smart-library/outline.md)
2. ✅ [blog-posts/02-deterministic-ml/outline.md](blog-posts/02-deterministic-ml/outline.md)
3. ✅ [blog-posts/03-sensitivity-analysis/outline.md](blog-posts/03-sensitivity-analysis/outline.md)

---

**Last Updated:** 2025-12-31
**Status:** ✅ ALL OUTLINES EVIDENCE-CORRECTED — READY FOR FULL DRAFT WRITING
