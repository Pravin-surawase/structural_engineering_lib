# Research Plan — Structural Design Automation Market & Pain Points

**Purpose:** Understand the real-world context, engineer pain points, existing solutions, and practical applications before creating blog content.

**Directive:** "Writing without actual knowledge of current situation and practical world and application, problem solving, will be a mistake." — User requirement

**Timeline:** Pre-blog research phase (before Jan 2025 publications)

---

## Research Objectives

### Primary Questions

1. **Engineer Pain Points:**
   - What are the biggest frustrations with current structural design workflows?
   - Where do engineers spend the most time in the design process?
   - What automation attempts have failed and why?
   - What keeps engineers stuck in Excel despite better tools existing?

2. **Existing Products:**
   - What structural design automation tools exist today?
   - What do they do well? What do they lack?
   - How do they integrate with Excel vs force platform migration?
   - What are their pricing models and adoption rates?

3. **Real-World Examples:**
   - Who has successfully automated structural design workflows?
   - What approaches worked? What failed?
   - Case studies of Excel-based automation in structural engineering
   - Examples of engineers building custom tools/macros

4. **Academic Research:**
   - Papers on structural design automation
   - Research on Excel-based engineering tools
   - Studies on engineer workflow and productivity
   - Sensitivity analysis applications in practice

5. **Current Solutions:**
   - How are engineers solving automation problems today?
   - What workarounds exist?
   - Community-built tools and open-source projects
   - VBA/Python integration approaches

---

## Research Methodology

### Phase 1: Engineer Communities & Forums (Week 1)

**Sources:**
- **Eng-Tips Forums** — Structural engineering discussion
- **Reddit:** r/StructuralEngineering, r/civilengineering
- **LinkedIn Groups:** Structural Engineering, Civil Engineering Software
- **Stack Exchange:** Engineering Stack Exchange
- **Discord/Slack:** Engineering communities

**Search Keywords:**
- "structural design automation"
- "Excel VBA structural engineering"
- "ETABS automation"
- "beam design spreadsheet"
- "structural engineering productivity"
- "repetitive design tasks"

**What to Extract:**
- Common complaints and pain points
- Questions asked repeatedly
- Tools mentioned (positively/negatively)
- Workarounds engineers share
- Unmet needs expressed

**Documentation:** `findings/01-engineer-pain-points.md`

---

### Phase 2: Product Analysis (Week 1-2)

**Products to Research:**

**Commercial Software:**
1. **STAAD.Pro** — Structural analysis and design
2. **ETABS** — Building analysis (CSI)
3. **RAM Structural System** — Bentley
4. **Tekla Structures** — Detailing and BIM
5. **RISA-3D** — 3D structural analysis
6. **SkyCiv** — Cloud-based structural software

**Excel Add-ins/Tools:**
1. **Tedds** — Structural calculations
2. **Excel-based design spreadsheets** (common practice)
3. **Custom VBA tools** (community-built)

**Python/Open-Source:**
1. **PyNite** — Finite element analysis
2. **StructPy** — Structural analysis
3. **Concrete design libraries** (if any)

**Analysis Framework:**
For each product, document:
- **What it does:** Core features
- **Integration:** Excel-native vs standalone
- **Automation:** Can workflows be automated?
- **Strengths:** What it does well
- **Weaknesses:** What's missing or frustrating
- **Pricing:** Cost barrier
- **Adoption:** Who uses it and why
- **Smart features:** Optimization, sensitivity, guidance?

**Documentation:** `findings/02-product-analysis.md`

---

### Phase 3: Academic Literature Review (Week 2)

**Databases:**
- **Google Scholar** — Primary source
- **ResearchGate** — Paper access
- **arXiv.org** — Preprints
- **ASCE Library** — Civil engineering journals
- **ScienceDirect** — Elsevier journals

**Search Queries:**
1. "structural design automation"
2. "Excel-based engineering tools"
3. "sensitivity analysis reinforced concrete"
4. "beam design optimization"
5. "constructability assessment automation"
6. "deterministic methods structural engineering"
7. "engineering workflow productivity"
8. "VBA automation civil engineering"

**Target Papers:**
- Recent (2020-2025) for current state
- Foundational (pre-2020) for established methods
- Case studies of automation implementation
- Surveys of engineer tool usage

**What to Extract:**
- Problem statements (what researchers identify as pain points)
- Proposed solutions (what's been tried)
- Validation methods (how success is measured)
- Gaps identified (what's still unsolved)
- Citations for our own work

**Documentation:** `findings/03-academic-literature.md`

---

### Phase 4: Real-World Case Studies (Week 2-3)

**Search for:**
1. **Engineering firm automation stories**
   - Blog posts by structural engineers
   - LinkedIn articles on workflow improvements
   - Case studies from consulting firms

2. **Excel automation examples**
   - VBA projects on GitHub
   - Spreadsheet templates shared publicly
   - Macro libraries for structural engineering

3. **Success stories**
   - "How we automated our beam design workflow"
   - "Reducing design time by X%"
   - "Custom tools that saved our firm"

4. **Failure stories**
   - "Why our automation project failed"
   - "Abandoned software implementations"
   - "Lessons learned from tool migration"

**Sources:**
- Medium, Dev.to (engineering blogs)
- LinkedIn articles
- Company websites (case studies)
- YouTube (tutorial videos, demos)
- GitHub (open-source projects)

**Documentation:** `findings/04-case-studies.md`

---

### Phase 5: Current Problem-Solving Approaches (Week 3)

**Investigation Areas:**

1. **Repetitive Design Workflows:**
   - How do engineers handle 100s of similar beams?
   - Copy-paste patterns in Excel
   - Template reuse
   - Manual iteration processes

2. **Integration Challenges:**
   - ETABS → Excel → Design → CAD workflows
   - Data transfer pain points
   - Version control issues
   - Collaboration bottlenecks

3. **Validation & Checking:**
   - How are designs verified?
   - Manual calculation checks
   - Peer review processes
   - Code compliance documentation

4. **Knowledge Transfer:**
   - How do junior engineers learn?
   - Senior engineer time spent mentoring
   - Documentation gaps
   - Tribal knowledge problems

**Methods:**
- Forum discussions analysis
- LinkedIn polls (if needed)
- YouTube comments on tutorial videos
- GitHub issues on structural engineering projects

**Documentation:** `findings/05-problem-solving-approaches.md`

---

### Phase 6: Market Gaps & Opportunities (Week 3)

**Synthesis Phase:**

Combine findings from Phases 1-5 to identify:

1. **Unmet Needs:**
   - What do engineers want that doesn't exist?
   - Features present in research but not in products
   - Common complaints not addressed by current tools

2. **Excel-Specific Gaps:**
   - Why isn't intelligence available in Excel?
   - What prevents smart features in VBA?
   - Technical barriers vs. business model barriers

3. **Automation Bottlenecks:**
   - What stops engineers from automating?
   - Technical skills gap
   - Time investment required
   - Reliability concerns

4. **Our Unique Position:**
   - What can we offer that others don't?
   - Deterministic intelligence in Excel
   - Open-source vs. commercial advantage
   - Research-driven credibility

**Documentation:** `findings/06-market-gaps.md`

---

## Research Execution Plan

### Week 1: Foundation

**Days 1-2:**
- ✅ Create research plan (this document)
- 🔲 Set up findings folder structure
- 🔲 Engineer forums search (Eng-Tips, Reddit)
- 🔲 Document initial pain points

**Days 3-5:**
- 🔲 Product research (commercial software)
- 🔲 Product research (Excel add-ins)
- 🔲 Product research (open-source)
- 🔲 Create product comparison matrix

**Days 6-7:**
- 🔲 Academic literature search (Google Scholar)
- 🔲 Download and catalog relevant papers
- 🔲 Begin literature summary

### Week 2: Deep Dive

**Days 8-10:**
- 🔲 Continue academic literature review
- 🔲 Extract key findings from papers
- 🔲 Identify citation-worthy sources

**Days 11-14:**
- 🔲 Real-world case studies search
- 🔲 GitHub/YouTube exploration
- 🔲 LinkedIn articles analysis
- 🔲 Document examples and patterns

### Week 3: Synthesis

**Days 15-17:**
- 🔲 Current problem-solving approaches analysis
- 🔲 Integration workflow pain points
- 🔲 Validation process documentation

**Days 18-21:**
- 🔲 Synthesize all findings
- 🔲 Identify market gaps
- 🔲 Map our solution to real needs
- 🔲 Create research summary document

---

## Documentation Structure

### findings/ Directory

```
findings/
├── 01-engineer-pain-points.md          # Forum/community analysis
├── 02-product-analysis.md              # Commercial & open-source tools
├── 03-academic-literature.md           # Papers and research
├── 04-case-studies.md                  # Real-world examples
├── 05-problem-solving-approaches.md    # Current workflows
├── 06-market-gaps.md                   # Synthesis and opportunities
└── 00-research-summary.md              # Executive summary
```

### Document Format (Template)

Each findings document will follow this structure:

```markdown
# [Topic]

**Research Date:** [Date range]
**Sources:** [List of sources]
**Key Findings:** [3-5 bullet summary]

---

## Detailed Findings

### Finding 1: [Title]
**Source:** [URL/Citation]
**Evidence:** [Quote or data]
**Implication:** [What this means for our work]

### Finding 2: [Title]
...

---

## Patterns & Themes

[Cross-cutting observations]

---

## Gaps Identified

[What's missing or unsolved]

---

## Relevance to Our Work

[How this informs our blog content and product direction]
```

---

## Success Criteria

**Research phase is complete when:**

1. ✅ Documented 20+ engineer pain points from real sources
2. ✅ Analyzed 10+ competing products with strengths/weaknesses
3. ✅ Reviewed 15+ academic papers on relevant topics
4. ✅ Found 5+ real-world case studies (success or failure)
5. ✅ Identified 5+ clear market gaps we can address
6. ✅ Created synthesis document connecting findings to our solution

**Quality Checks:**

- [ ] All claims backed by sources (URLs, citations)
- [ ] Quotes and data extracted verbatim (no assumptions)
- [ ] Patterns identified across multiple sources
- [ ] Our solution mapped to real, documented needs
- [ ] Blog content can reference specific findings

---

## Post-Research: Blog Content Update

**After research complete:**

1. **Revise blog outlines** based on findings
   - Update pain points with real examples
   - Reference competing products accurately
   - Cite academic research where relevant
   - Use case study data to support claims

2. **Create evidence-based narratives**
   - "Engineers on Eng-Tips consistently complain about X"
   - "A 2023 study found that Y% of time is spent on Z"
   - "Product A solves for deflection but lacks sensitivity"

3. **Add credibility markers**
   - Citations in footnotes
   - Links to sources
   - Data tables from research
   - Screenshots from products

4. **Ensure practical relevance**
   - Speak to documented pain points
   - Offer solutions to real problems
   - Compare against known alternatives
   - Provide actionable insights

---

## Resources & Tools

**Web Research:**
- Google Scholar (academic papers)
- Google Search (forums, blogs, products)
- LinkedIn search (articles, posts)
- Reddit search (community discussions)
- YouTube search (tutorials, demos)

**Documentation:**
- Markdown files in findings/
- Source URLs tracked
- Screenshots where helpful
- Data tables for comparisons

**Analysis:**
- Thematic coding of pain points
- Product feature matrix
- Citation database
- Gap analysis framework

---

## Risk Mitigation

**Risk:** Research takes too long, delays blog publication

**Mitigation:**
- Time-boxed phases (3 weeks max)
- Parallel research tracks
- Prioritize high-impact sources
- Create summary as we go (not at end)

**Risk:** Findings contradict our approach

**Mitigation:**
- Embrace transparency (acknowledge limitations)
- Pivot blog angle if needed
- Focus on specific use cases where we excel
- Learn from what doesn't work

**Risk:** Limited public information available

**Mitigation:**
- Use academic proxies (papers on similar topics)
- Infer from related domains (Excel automation broadly)
- Focus on what we CAN document
- Note knowledge gaps explicitly

---

## Next Steps

1. **Immediate (Today):**
   - Create findings/ directory
   - Begin engineer forum research
   - Document first 10 pain points

2. **This Week:**
   - Complete Phase 1 (engineer communities)
   - Complete Phase 2 (product analysis)
   - Start Phase 3 (academic literature)

3. **Week 2-3:**
   - Complete academic review
   - Find case studies
   - Synthesize findings
   - Create research summary

4. **Post-Research:**
   - Update blog outlines with evidence
   - Write drafts grounded in research
   - Publish with confidence

---

**Last updated:** 2025-12-31
**Status:** ACTIVE — Research in progress
**Owner:** Pravin + Claude Code (research execution)
