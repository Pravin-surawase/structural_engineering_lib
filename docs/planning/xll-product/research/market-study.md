---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: intermediate
tags: [excel-dna, xll, planning, research]
---

# ETABS market and competitor study
> Software for our engineering work, and evidence for a possible commercial product
> India-focused RC building workflows • Global competitors • 3 September 2026

## 1. What the research changes

**Status: external research paused at the user's request on 3 September 2026.** The evidence below remains the dated research archive. The companion document, StructAutomate: product blueprint and parked research, extracts proposed requirements, preserves the original P0/P1 boundaries and records 23 remaining items with reopening conditions. No new external research was conducted for that synthesis.

**Similar products already exist, and some are considerably more developed in individual parts of the proposed workflow.** The market includes Excel toolboxes, concrete design and detailing packages, model optimizers, connected calculation platforms, AI assistants, and complete alternatives to ETABS. There is no evidence from this research that one universally best product covers every requirement we have discussed.

For our own work, buying or combining existing tools deserves serious evaluation before building a large system. For a business, the useful question is narrower: which recurring task can we perform more reliably, with less total engineering effort, for a clearly identified customer?

The proposed StructAutomate workflow is: **read ETABS → check/design → compare alternatives → approve changes → update a model copy → rerun analysis → verify and report**. The supplied implementation brief specifies an **x64 Excel-DNA XLL written in C#, hosted in desktop Excel with a native Ribbon**. Its first milestone is only the Excel shell. This study compares the intended later engineering workflow separately from that first milestone; it does not assume that every first-milestone restriction applies permanently.

### Correction after closer investigation

**The earlier conversational claim that CivilAI was closest overall was too strong and is withdrawn.** Its advertised scope overlaps our ambition, but the public evidence establishes a bespoke service offering, not a comparable packaged application. The comparison must separate the Excel experience, the Indian RC engineering engine and the automated model-revision sequence.

| Comparator | Closest substantiated overlap | Essential unresolved difference |
| --- | --- | --- |
| StructPro | Excel commands for CSI model edits, result extraction, repeated calculations and reports demonstrated in tutorials | Current installer link is broken; licence scope conflicts; exact XLL implementation, Indian RC validation and complete approved revision/reanalysis loop unestablished |
| ETABS SideKick | Excel retrieval, load-input workbooks and geometry creation shown in a historical demonstration; live India offer | Current ETABS/Office support and delivered package unverified; complete Indian RC design/revision workflow unestablished |
| RCDC | Documented Indian RC design, reinforcement, detailing and revision capabilities | Separate design application; exact current ETABS write-back and automatic reanalysis sequence unestablished |
| ConGro | Chat-driven ETABS work plus a separately initiated optimizer; beta artifact available | Founder separates agent from optimizer; Indian RC validation and our Excel approval workflow unestablished |
| ACE OCP | Historically documented material-cost search using candidate models, repeated analysis/design and comparison reports | Current ETABS support, permanent price and client-project licence terms unresolved; complete Indian RC/Excel workflow unestablished |
| ETABS MATE | Documented reinforcement detailing, selected checks, drawings and schedules | Indian-code coverage, preserved edits on reimport, upstream changes and client-project licence rights unresolved |
| CivilAI | Advertised custom office workflow around ETABS, Excel and Indian codes | No public packaged product, executable demonstration or reference calculation found in the audited site |

These are **comparisons of documented fit, not scores from software testing**. The evidence supporting each row is developed in sections 4–6. No single reviewed product has yet been shown to deliver our complete intended workflow.

Three findings matter most:

- **The incumbent is a strong competitor.** ETABS already provides design, member selection/optimization facilities, editable tables and reporting. Its API allows external programs to create or modify models, run analysis and retrieve results. Existing licenses plus internal spreadsheets/scripts are a credible substitute. [ETABS features](https://www.csiamerica.com/products/etabs/features), [CSI Developer](https://www.csiamerica.com/developer).
- **Direct automation competitors are real.** StructPro and SideKick sell Excel-led productivity; ConGro advertises a repeated ETABS resizing/reanalysis workflow; CivilAI advertises custom Indian-office automation. Their evidence and maturity differ substantially. See the product records below.
- **The commercial opening is unproven.** A traceable Indian RC revision workflow is worth investigating, but documentation gaps in competitors do not establish an empty market, dissatisfied customers, or willingness to pay.

This is a desk-research study using official product pages, manuals, release notes, pricing pages, original research and public repositories. Three research agents helped investigate CivilAI, ConGro, RCDC, StructPro, ACE OCP, ETABS SideKick and ETABS MATE in bounded research lanes. The lead researcher reconciled decisive sources, inspected original RCDC reference packages, and examined StructPro's live site, complete tutorial transcripts and selected video frames. ACE OCP evidence includes historical manuals/research, a complete presentation transcript, a sponsored review and live shop selections. SideKick evidence includes sampled official tutorial frames, an independently checked India order display and related engineering-tool documentation. ETABS MATE evidence includes current manuals, selected page images, historical schedules, licence terms and bounded adoption research. We did not install software, purchase licenses, contact vendors or interview customers. “Documented” means a source supports the claim, not that we independently verified the software's engineering accuracy. Other products remain screened comparators, not equally detailed audits.

## 2. Understand the market before comparing products

Think of a design office as a workshop. ETABS is a major machine; Excel holds worksheets and instructions; specialist design software is another machine; an add-in moves information and operates controls. Improving the conveyor between machines is useful, but it does not automatically improve every machine or certify the finished work.

| Market category | What the customer buys | Relevant examples |
| --- | --- | --- |
| Existing analysis/design environment | Core modelling, analysis, member design and reports | ETABS, SAFE and CSI's own integrations |
| Excel productivity toolbox | Fewer repetitive selections, data transfers and model edits | StructPro, ETABS SideKick |
| Concrete design/detailing | Reinforcement choices, member checks, drawings and quantities | RCDC, S-CONCRETE, VIS, ETABS MATE, PROKON |
| Optimizer or AI controller | Candidate changes and, in some cases, repeated analysis | ACE OCP, ConGro AI; newer offerings on the watchlist |
| Calculation/workflow platform | Reusable office calculations and connected reports | CalcTree; custom services such as CivilAI |
| Complete alternative suite | A different integrated modelling-to-deliverables workflow | Tekla Structural Designer, ProtaStructure, CYPECAD |
| Development foundation | Building blocks for an internal or commercial tool | Excel-DNA, PyXLL, xlwings, BHoM, public ETABS repositories |

**Six capabilities must be kept separate.** Import reads information. Write-back changes the upstream model. Reanalysis computes new structural response after changes. Member design selects or checks a section/reinforcement arrangement. Optimization searches alternatives against an objective and constraints. Detailing produces construction-oriented reinforcement information. A product can do one very well without doing the others.

For example, reducing a column size in a spreadsheet is a proposed change. Exporting that size to ETABS applies it. Running ETABS again produces new forces and displacements. Rechecking the revised building establishes whether the proposal remains acceptable. A report based only on the earlier forces cannot demonstrate the whole revised workflow. CYPE's own documentation explicitly distinguishes reinforcement redesign using previous forces from full reanalysis after stiffness-changing edits. [CYPECAD analysis options](https://info.cype.com/en/product/cypecad-options-in-the-analyse-menu-on-the-beam-input-tab/).

## 3. The baseline we would compete against

### ETABS, SAFE and CSiXCAD

ETABS already supports substantial analysis/design automation. Its help describes auto-select sections and period-target optimization, with iteration between analysis and design. These facilities should be benchmarked before claiming a new optimizer. They do not establish that native ETABS solves every whole-building RC cost-minimization problem. [Set Time Period Targets](https://docs.csiamerica.com/help-files/etabs/Menus/Design/Set_Time_Period_Targets.htm).

CSI's July 2026 release record lists ETABS 23.3.0/23.3.1 and SQLite table export. The history also documents the IS 13920:2016 update to IS 456:2000 concrete frame design. Thus, neither Indian-code checking nor structured extraction alone is a defensible new-product claim. [ETABS enhancements](https://www.csiamerica.com/products/etabs/enhancements).

CSiXCAD generates structural drawings in supported CAD hosts and incorporates changes imported from ETABS/SAP2000/SAFE while retaining drawing edits. This competes for drawing-production work. Its documented direction is analysis-model changes flowing into CAD; it is not evidence of an ETABS optimization loop. [CSiXCAD](https://www.csiamerica.com/products/csixcad).

**Buying implication:** first identify the missing task in the existing CSI workflow. An additional product should save enough total effort to justify another license, integration and review process.

## 4. Excel, integration and workflow competitors

### StructPro — closest Excel control-panel comparator

**StructPro close study: its demonstrated Excel/model workflow overlaps our plan substantially, but its current purchase readiness is uncertain.** This strengthens its position as an interface and command-workflow comparator. It does not establish a complete Indian RC revision product. The homepage advertises over 100 commands for CSI programs and AutoCAD. [StructPro homepage](https://www.structprollc.com/p/homepage.html).

The official catalogue contains fourteen lessons. Across this and the previous pass, we read complete auto-generated transcripts for installation, CSI interaction, CalcPro, property, database, beam and column commands, and sampled selected frames. We did not watch every lesson frame by frame or execute the software. Tutorial narration can establish the demonstrated sequence, but cannot prove the current build behaves identically. [Official tutorial catalogue](https://www.structprollc.com/p/tutorial.html).

#### How the Excel connection works

The CSI interaction lesson uses predefined header identifiers to map model data into worksheet columns. An engineer selects ETABS objects, retrieves their names and fetches corresponding properties. This resembles an address book: the object name identifies the item, and the column identifier identifies the information requested. It is a commanded retrieval, not evidence of continuous background synchronization. [CSI interaction, 4:00–6:18](https://www.youtube.com/watch?v=FSn0H2H2wNM).

The property lesson demonstrates **actual model writes**. The user retrieves section properties, changes spreadsheet values, selects the matching section type and applies Set Section Property; the narrator then checks the changed property in ETABS. It also creates a new section from an Excel row. The spring example is specifically limited to point springs. Wrong section-type selection is a meaningful operating dependency. [Property commands, 2:32–6:28 and 6:35–9:26](https://www.youtube.com/watch?v=17Bw_jLEZMU).

Two different edits must be understood. Changing a section definition alters the dimensions/material information belonging to that named section. Assigning a section tells a particular member which existing section to use. These are separate ETABS operations, and both kinds appear in StructPro's tutorials. [ETABS section definitions](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Properties/Frame_Sections/Frame_Section_Property_Data_Form.htm), [ETABS section assignments](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Section_Property.htm).

The database lesson distinguishes Get Table For View from Get Table For Edit. For editing, it instructs users to unlock the model, refresh the editable table, change Excel values and apply Edit Current Table. It also binds result retrieval to a chosen load case/combination and selected object group. Consequently, a table's purpose and selection context matter as much as the displayed numbers. [Database commands, 3:20–6:55 and 8:04–9:48](https://www.youtube.com/watch?v=KtytM6zq5u0).

#### What the beam and column tools actually return

The beam lesson demonstrates assigning existing sections, collecting forces for selected combinations, optional individual force sheets and deflections. Deflection retrieval requires appropriate model meshing and prior analysis; the lesson does not establish every cracked-section or long-term assumption. For reinforcement results, the sequence runs design in ETABS before retrieving design reinforcement/forces. This is evidence of operating and reading ETABS, not a separate StructPro structural-design engine. [Beam commands, 3:41–6:50 and 11:12–17:00](https://www.youtube.com/watch?v=IyW0OLb4okU).

The column lesson adds story/group selection and combined result handling. Joining member names with a plus sign is a results-grouping operation; it is not evidence that physical ETABS objects are merged. Its crucial distinction is **Design versus Checking**: the design example retrieves required reinforcement and reports utilization as zero; checking uses reinforcement already specified and produces a utilization result. Zero in the first context must not be presented as proof that supplied reinforcement passed. This is a result-interpretation issue, not an identified software defect. [Column commands, 8:07–12:39 and 14:13–17:03](https://www.youtube.com/watch?v=FuyPcjOqBDM).

CSI's own help confirms the underlying distinction: reinforcement design calculates required steel area, whereas checking uses the reinforcement specified in the section definition. A future interface should display the calculation mode alongside the value and explain when a quantity is not applicable. [ETABS reinforcement data](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Properties/Frame_Sections/Frame_Section_Property_Reinforcement_Data_Form.htm).

#### CalcPro automates a calculation library

CalcPro maps named input/output cells to table columns. CalcWS runs rows through calculations in the same workbook; CalcWB selects library templates using a Type field and identifies cases separately. It can retain row calculation workbooks, reopen them through OpenCalc, and export selected sheets as individual or combined PDFs. SyncData copies current calculation inputs and outputs back into the chosen table row: it changes stored row data. The lesson instructs users to rerun after template/report setup changes. The demonstration uses a simple mathematical calculation; it does not validate Indian RC formulas, template errors or stale-result detection. [CalcPro, 2:03–7:58 and 8:54–17:36](https://www.youtube.com/watch?v=PZi3IXS8TKU).

A beginner's analogy is an office assistant operating a trusted worksheet repeatedly. The assistant can copy inputs, run calculations and print pages. The engineering quality still depends on the worksheet, its assumptions, the input mapping and review. Automating an existing formula does not independently establish that formula's correctness.

#### Follow one proposed column change through the workflow

The following is our comparison scenario, not a tested StructPro result: an engineer proposes using a different named section for one column. Each stage asks a separate question.

| Stage | Evidence from the reviewed lessons | What still needs demonstration |
| --- | --- | --- |
| Identify and read the column | Object names, properties and selected results retrieved into Excel | Mapping remains correct after renames and model revisions |
| Propose a different section | Spreadsheet values and section assignments can be edited | Alternatives satisfy a defined objective and engineering constraints |
| Apply the change | Explicit property/assignment and editable-table commands demonstrated | Enforced approval, intended model-copy targeting and recoverable partial failure |
| Obtain revised results | Analysis/design is a prerequisite to the illustrated result retrieval | Automatic rerun, completion checking and detection of stale results |
| Check and issue deliverables | ETABS design results and template/PDF workflows demonstrated | Validated Indian checks tied to the exact revised model and calculation versions |

This table separates known commands from missing evidence. It does not assert that unshown capabilities are absent. The reviewed material does not establish a single automated sequence that proposes alternatives, records approval, updates a model copy, reruns analysis and verifies the revised building.

#### Current availability, support and licence cost

The download page labels version 1.0, build 18 April 2025. Its linked MediaFire archive returned a missing-file page during this review on 3 September 2026. **We could not obtain the advertised public installer.** This may be a broken distribution link; it is not proof that the business has stopped operating or that customers lack private downloads. [Download page](https://www.structprollc.com/p/download.html), [vendor-linked archive availability](https://www.mediafire.com/file/22zrv013lwzvne3/StructPro_Built20250418.zip/file).

The installation tutorial describes setup, a library folder and loading an additional Excel add-in. Without an accessible package, neither C# nor an Excel-DNA XLL architecture is established. No binary inspection or execution occurred. [Installation, 2:50–5:27](https://www.youtube.com/watch?v=nk1KnflYVK8).

The support page lists Windows desktop Excel 2013/2016/2019/365, ETABS/SAFE 19–21 and AutoCAD 2010–2023. ETABS 22/23 compatibility remains unconfirmed. It explicitly says Undo is unavailable. Although ordinary installation is described as generally not requiring administrator rights, ETABS registration troubleshooting does use administrator execution. [Support](https://www.structprollc.com/p/support.html).

**There is no verified public numeric price.** The purchase page advertises internet-dependent floating access, concurrent-computer limits, a seven-day trial and subscription renewal for continued use. It does not supply the price, subscription length or included slot count. Its 1.5-hour slot-release delay after an offline exit must not be mistaken for permission to work offline. [Purchase terms](https://www.structprollc.com/p/purchase.html).

The EULA instead describes a subscription per user, assignment to one device and an additional portable copy for the primary user; it also says renewal is not automatic. These descriptions do not establish how a team's shared floating pool is licensed. **The earlier unqualified floating-licence description is therefore corrected:** concurrent operation is advertised, but contractual user/device rights require reconciliation. [EULA](https://www.structprollc.com/p/eula.html).

For a single engineer, total cost needs the subscription quote plus any additional Excel/ETABS entitlements, setup, template preparation and review time. For a team, obtain both the authorized-user count and simultaneous-computer count. Five engineers sharing two concurrent slots cannot be costed as two licences from the present evidence. Existing host licences should count only when an additional fee is actually necessary. A dependable one- or three-year total is currently not calculable.

#### Decision for our own work and possible product

For our own work, StructPro deserves a controlled comparison for repeated Excel/ETABS tasks once a current trial and consistent licence terms are available. A purchase recommendation is premature without those items and confirmation for our exact software versions. No independently attributable adoption or measured savings evidence was established in this bounded research.

For a product, **Excel-to-ETABS editing, batch calculations and PDF generation already have a demonstrated competitor**. Those features alone do not establish a new commercial opening. A testable differentiation hypothesis is a tightly supported Indian RC revision workflow that makes object identity, calculation mode, approval and result freshness explicit. The next proof should be one complete changed-column case, including a failed check and recovery, with total engineer/reviewer time recorded.

### ETABS SideKick — Excel productivity with a verified Indian offer

**SideKick close study: a direct competitor for repeated Excel/ETABS operations, with a clearer public purchase path than StructPro.** The product advertises selection, geometry/force retrieval, load assignment, section/object creation and AutoCAD exchange. These commands overlap our early integration ambitions. They do not establish a complete Indian RC design-and-revision product. [SideKick product record](https://excelcrib.com/downloads/spreadsheets/ETABS-Sidekick.html).

#### What the demonstration actually shows

The official video is dated 6 April 2020 and lasts 10:29. We inspected eight sampled frames: the opening, coordinates around 1:39, AutoCAD text around 3:11, end results around 4:11, a frame-load workbook around 6:17, and geometry creation around 8:23–9:59. The last samples show an initially empty ETABS view followed by a curved triangular frame model. The demonstration uses ETABS 18.1.1 and helper workbooks named Assign Frame Loads.xlsm and Add Frames.xlsm. This supports an Excel-command/template workflow, without establishing the add-in's own format, language or current behavior. We did not watch every frame or obtain a complete transcript. [Official demonstration](https://www.youtube.com/watch?v=u1Q6m0_ndcg).

The practical sequence is understandable without programming: select objects, bring their identifiers or quantities into a worksheet, prepare values in a template, then invoke a command to read or write the model. For our product, the competitive question is how much work remains around those commands: preparing inputs, checking the selected objects, verifying assignments and producing trustworthy revised results.

#### Three concepts that matter more than the number of buttons

**Object identity is like an address.** A column label such as C1 may recur on several storeys. CSI explains that labels can renumber after deletions, while a unique name is unique within its object type and may be changed manually. A dependable worksheet therefore needs the model and object context, not merely a familiar-looking label. A row should be checked against its intended storey/member before a write. This is an evaluation requirement, not evidence of a SideKick selection fault. [CSI labels and unique names](https://docs.csiamerica.com/help-files/etabs/Keyboard_Commands_and_Special_Features/Labels_and_Unique_Names.htm).

**A force needs its context.** CSI's API distinguishes member/analysis-element identity, station, load case or combination, step and local-axis components. The older API documentation establishes these meanings, not compatibility with today's SideKick build. [FrameForce, ETABS2016 API](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm). End results also need careful interpretation: with end offsets, they occur at the inside face of the offset. A table containing only ends does not establish the maximum demand everywhere along a member. [CSI end offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm), [output stations](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Output_Stations.htm).

Consider this invented example at one member station. P is axial force; M2 and M3 are moments about the member's local axes. The figures illustrate data handling, not an engineering check:

| Load combination | P, kN | M2, kNm | M3, kNm |
| --- | --- | --- | --- |
| A | 1,000 | 40 | 60 |
| B | 800 | 70 | 25 |

Selecting the largest value from each column produces 1,000/70/60, which is neither original row. An intentional envelope may be useful for a defined purpose, but it should not be presented as forces that occurred together. Our interface should preserve the originating combination and station. We have not established how every SideKick extraction mode handles this issue.

**Applying an edit is only one stage.** ETABS distinguishes adding distributed loads from replacing loads in a specified pattern; repeating an additive operation can accumulate loads. [CSI distributed-load assignment](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame_Loads/Distributed_Load.htm). Unlocking an analysed model deletes its analysis results. CSI recommends Save As before changes when the original model/results must be retained. [CSI model locking](https://docs.csiamerica.com/help-files/etabs/Menus/Analyze/Lock_Model.htm). The reviewed SideKick material does not establish an enforced approval → model copy → edit → reanalyse → verify sequence, or its recovery behavior after a partial failure.

Native ETABS already offers selection by unique name and configurable table/Excel export. SideKick's potential value is the reduction in steps and worksheet handling around these abilities. Benchmark the same task in both workflows instead of treating extraction itself as new engineering functionality. [CSI selection](https://docs.csiamerica.com/help-files/etabs/Menus/Select/Select/Labels/Frame_Unique_Names_Select.htm), [table workflow](https://docs.csiamerica.com/help-files/etabs/Keyboard_Commands_and_Special_Features/Choose_Tables_form.htm).

#### The engineering tools are separate products

Excelcrib's related products help explain the market, but their functions are not included in SideKick merely because links appear on its page. Dollar amounts below reproduce the displayed symbol; the currency is not explicitly identified on those pages. Required host/design-engine licences are additional.

| Separate product | Documented purpose | Displayed offer or status |
| --- | --- | --- |
| Load Combination Manager | Reads and batch-edits combination definitions; CSV, envelopes and deletion | $49/year; ETABS18–21. [Product](https://www.excelcrib.com/downloads/Plug-ins/ETABS-Combination-Editor.html) |
| Column Design Companion | Maximum axial-force retrieval, grouping and Excel/CAD export; no documented reinforcement-design engine | $95/year; older host requirements. [Product](https://www.excelcrib.com/downloads/Plug-ins/ETABS-CDC.html) |
| ETABS-to-Prokon GenCol | Generates column inputs for a separately installed design program; lists Indian Standard without edition | $95/year; ETABS2016–21 and GenCol3+. [Bridge](https://excelcrib.com/downloads/Plug-ins/ETABS-to-Prokon-GenCol.html) |
| ETABS-to-spColumn | Batch ACI/CSA checks/reports and ETABS section assignment, optionally with reinforcement/modifiers | Explicitly discontinued; historical $199 single-module/$399 combined prices are not current offers. [Product](https://www.excelcrib.com/downloads/Plug-ins/ETABS-to-spColumn-Design.html) |

PROKON's own General Column specification describes checking provided bars or determining bar size, and explicitly lists IS 456:2000. This is evidence for the external engine; it does not validate Excelcrib's Indian-code transfer or establish IS 13920 detailing. [GenCol specification](https://read.prokon.com/view/730985369/), [code list](https://read.prokon.com/view/730985369/3/).

The spColumn v7 manual explains its CTI batch interface and warns that changing an input-file units flag does not convert the numeric data. That gives us a concrete translation test, but does not prove how Excelcrib handles conversion. The vendor-linked sample-report archive returned HTTP 403 and was not inspected. [Original manual, physical pp.84 and 184](https://structurepoint.org/pdfs/manuals/spColumn/spColumn%20manual%20v7.00.pdf). Later, spColumn v10 introduced native EDB/XML load import and batch processing. Some old bridge functionality therefore also faces competition from its host. This does not establish native ETABS write-back. [December 2021 release](https://structurepoint.org/soft/spColumn/release-notes/spColumn-v10.00-and-Newer-Release-Notes/10.00-New-Features/10.00-New-Features.htm?rhtocid=_2).

#### Indian price and what the licence buys

On 3 September 2026, the linked FastSpring page showed one SideKick perpetual licence at **₹17,576 including 18% GST of ₹2,681.08**. The lead checked the visible page and screenshot; an agent independently checked its public response. No customer details or payment were entered. This is an observed offer, not a personalized invoice or completed delivery. [India order display](https://excelcrib.onfastspring.com/ETABS-Sidekick-Perpetual).

The main page advertises $149 but does not itself identify USD. Our earlier unqualified US$149 comparison is therefore replaced with the directly observed Indian offer. [Product price](https://excelcrib.com/downloads/spreadsheets/ETABS-Sidekick.html). For the pre-tax cost table, subtracting displayed GST gives ₹14,894.92. One perpetual purchase remains the same software fee over one or three years under the stated entitlement; ongoing service and host costs remain separate.

The FAQ says licences are nonfloating, with internet needed for activation/deactivation. Purchased quantity controls simultaneous computers; a transferable key is deactivated before moving its slot. Perpetual use has no expiry, with at least three years of upgrades and support. The FAQ's one-year expiry rules apply to its normal licence, not this perpetual offer. Failed-computer recovery, transfer limits, post-three-year service prices and response times remain unspecified. [Licence FAQ](https://excelcrib.com/license-faq.html).

FastSpring's sale terms defer software rights to the vendor licence and do not supply a blanket India money-back trial. We found no SideKick-specific public EULA, refund policy or trial installer. A working order page does not verify delivery, activation or runtime behavior. [FastSpring sale terms, §§1,6–7](https://fastspring.com/legal/terms-sale/).

The latest listed release remains 2.0.0, 17 April 2024: ETABS 18–21, AutoCAD 2018–2024 and VBA Enabler. Office version/bitness and ETABS 22/23 compatibility remain unestablished. The video's helper workbooks and the AutoCAD dependency do not prove an Excel-DNA/C#/XLL architecture. [Published requirements](https://excelcrib.com/downloads/spreadsheets/ETABS-Sidekick.html).

#### Would it pay for itself in our office?

Use time measurements, not the command count. This is an invented costing example: assume engineering time is valued at ₹1,000/hour, setup takes 4 hours, and a repeated task takes 15 minutes manually versus 8 minutes including review with the tool. The net saving is 7 minutes per repetition.

Counting the full displayed tax-inclusive outlay, the initial time-equivalent cost is ₹17,576 ÷ ₹1,000/hour + 4 hours = 21.576 hours. Dividing by 7/60 hours per repetition gives 184.94, so approximately 185 repetitions cover that assumed outlay. This is not measured SideKick ROI. Tax recovery, additional host licences, rework and update disruption are excluded. Existing paid hosts should be counted only if this purchase creates an additional cost.

For our own work, SideKick deserves a comparison for recurring selection, extraction and modelling tasks once our exact Office/ETABS configuration and trial/refund route are clear. No attributable outside customer case or measured time-saving study was found in bounded searches; that does not mean it has no users.

For a possible product, this is a price reference for a focused productivity toolbox, not a price ceiling for a verified RC workflow. Compare the whole job: user preparation, model edits, fresh analysis, checking and issuing results. Our differentiation still needs evidence that customers value and will pay for the additional engineering/revision responsibilities.

### CalcTree — calculation knowledge and connected reporting

CalcTree's June 2026 Connection Nodes announcement describes typed, unit-aware connections among ETABS, Excel and calculations/reports. These desktop connections are enterprise deployments set up with customers. The examples establish results-to-checks/reporting positioning; the complete ETABS model-write command set is not enumerated. [Introducing Connection Nodes](https://www.calctree.com/blog/desktop-connection-nodes-launch).

A separate September 2026 Excel add-in update describes reusable calculations, named formulas and report previews. Named formulas require Excel 365; other described features require Excel 2019+. [What's new in the Excel add-in](https://www.calctree.com/blog/calctree-for-excel).

**Fit:** firms whose calculation library and report consistency are the main problem. **Demo question:** show exactly which ETABS changes are supported, how stale results are detected, and what the enterprise connector costs.

### CivilAI — custom Indian-office automation service

CivilAI's homepage explicitly describes an early custom operation with no off-the-shelf product. An audit of all eleven sitemap pages found no linked installer, manual, release history, sample workbook/model, calculation report or recorded demonstration. This is a bounded public-evidence finding; private customer deliverables may exist. It is sufficient reason to withdraw the earlier “closest overall product” label. [CivilAI](https://civilai.arpitkhandelwal.com/), [audited sitemap](https://civilai.arpitkhandelwal.com/sitemap.xml).

Its detailed ETABS page advertises versions 19–22, file-based EDB/E2K integration, extraction into Excel, revised section assignments returned to the model and revision/approval records. It says ETABS performs analysis. These are proposed service capabilities without an inspectable execution trace; Excel exchange does not establish an Excel-hosted XLL. [ETABS automation](https://civilai.arpitkhandelwal.com/etabs-automation).

The structural-engineering example ends by asking for a rerun, without showing automatic analysis, completion checking or fresh verification. It names IS 456, IS 875, IS 1893, IS 800 and IS 13920, but provides no reviewed edition-by-element validation matrix. Review before client delivery is also different from an enforced approval gate before model modification. [Structural-engineering workflow](https://civilai.arpitkhandelwal.com/ai-for-structural-engineers).

Published build fees are ₹50,000 for one workflow, ₹2 lakh for connected workflows and ₹5 lakh for a custom pipeline, with 30-day, 90-day and six-month support respectively. Lifetime use and no seat fees are advertised, but source/IP ownership, redistribution, post-support maintenance and exact acceptance criteria are not established. All audited Privacy, Terms and Support footer anchors point to page placeholders. **₹5 lakh is not a quotation for building and selling our specified product.** [CivilAI pricing](https://civilai.arpitkhandelwal.com/pricing).

**Fit judgment:** a custom-service enquiry candidate, with delivery evidence still required. Searches did not establish independently attributable customer case studies or measured savings; that does not prove its claims false. A useful next evidence item would be a delivered application and one reproducible model-revision trace.

## 5. Concrete design and detailing competitors

### Bentley RCDC — first priority for Indian RC design/detailing

STAAD Advanced Concrete Design (RCDC) covers member design/redesign, detailing, drawings and quantities. Its scope includes beams, columns, walls and other concrete elements, with module qualifications. [Bentley product datasheet](https://www.bentley.com/wp-content/uploads/PDS-STAAD-Advanced-Concrete-Design-LTR-EN-LR.pdf).

Bentley's overview names IS 456:2000 and IS 13920:2016, plus DXF drawings/BBS and HTML calculation reports. The Indian validation index contains worked examples for ductile columns, joints, boundary-element walls and other checks. This is reviewable engineering evidence, though we have not independently recalculated every example. [RCDC overview](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0115950), [Indian validation index](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0110823).

The June 2026 release records v23.00.09 and fixes involving IS 13920 spacing, grouped-column redesign, merged-beam forces and displayed reinforcement. These are resolved issues and useful lessons for future regression cases, not evidence that every current design is faulty. The history also describes checking existing reinforcement against revised analysis files. [RCDC release history](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0111459).

**ETABS integration requires care.** An older direct-link article describes EDB/MDB extraction, but Bentley's more specific article says EDB import is unavailable for ETABS 17 onward and directs users to ACCDB exports. An ETABS 20 support answer repeats that requirement. A broad “any version” statement is not an explicit current ETABS 23 compatibility matrix. [EDB limitation](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0115155), [ACCDB requirement](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0115862).

The documented ETABS 18 procedure also distinguishes basic-case forces from combination definitions and lists import restrictions. Such interpretation details matter more than the word “integration” on a product page; their application to a current release still needs confirmation. [ETABS import procedure](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0115830).

**Two update commands have different directions.** Update Analysis File can return redesigned beam/column sizes to an analysis file. Update Design checks an existing RCDC design against revised analysis supplied to it. The first capability is supported by a dated Bentley document description; its demonstration ZIP required authentication and was not accessed. Neither description establishes a current ETABS model-copy, automatic reanalysis and final verification sequence. [Update Analysis File, 26 June 2020](https://bentleysystems.service-now.com/community?id=community_document&sys_id=b443446e1b314610dc6db99f034bcbe8), [design-update release history](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0111459).

The 2026 STAAD release identifies RCDC 23.00.09.015 and includes its license with STAAD.Pro Advanced or Structural WorkSuite. Basic STAAD.Pro has restrictions on redesign, Update Design, Update Analysis File and drawing export. A standalone RCDC license is documented, but its current India price was not found. [Current release and entitlement](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0050365), [feature restrictions](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0111695), [license selection](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0111693).

**Fit judgment:** strongest documented Indian RC engineering comparator among the closely reviewed products. It is a separate design application; its Excel export documentation describes opening HTML reports in Excel/Word, not an Excel-hosted calculation runtime. Current package prices are in section 9. [Report export](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0116095).

#### RCDC close study: what an engineer actually does

The closer study strengthens RCDC's position as an incumbent design-and-revision competitor. It also identifies the work left for an engineer between applications. In this workflow, ETABS supplies an analysed building and RCDC develops or checks reinforcement and deliverables. ETABS itself also has design capabilities; this is the selected division of work, not a claim that ETABS only performs analysis.

Consider a hypothetical project where an architect changes a floor layout after the first design. The useful question is not simply whether a column passes. The engineer needs to know which objects changed, whether accepted reinforcement remains adequate, and which drawings must be reissued. The following is an evaluation procedure, not a claim that one command performs every step:

1. Record the source model revision and complete its analysis in ETABS.
2. Export the required model and analysis data, then check that the export is complete and belongs to that revision.
3. Import into RCDC, reconcile member/level identities, set engineering options and review reinforcement and detailing.
4. When loads or geometry change, analyse the revised source model and bring that analysis into the existing RCDC design through Update Design.
5. Review retained and changed reinforcement, investigate mapping differences, and regenerate affected deliverables. If the accepted proposal changes the analysis model again, repeat the analysis and design checks.

The documented RCDC procedures support the downstream import and design-update steps. A complete ETABS-specific copy, approved write-back, automatic analysis and freshness check still needs a current executable demonstration.

#### Import quality is part of the product

Bentley's ETABS import instructions require basic load-case forces as well as combination definitions; RCDC derives the combination forces. A troubleshooting article identifies missing tables covering geometry, connectivity, offsets, restraints, materials and cases. **Product implication:** a successful file-open operation is not enough; an importer should explain which required information is missing. These support articles describe historical workflows, not an ETABS 23 acceptance test. [ETABS data requirements](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0115830), [missing-table troubleshooting](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0115864).

The documented prerequisite is at least 13 beam output stations and three column stations before ETABS analysis. Stations are sample locations along a member. Bentley relates the beam sampling to reinforcement cutoff positions along the span. Reading only a member's end values can therefore lose information needed for detailing. [Station prerequisite](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0116279), [why thirteen beam stations](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0116235).

Wall identity also needs care: Bentley specifies separate pier labels for the arms of combined walls and new labels where an arm becomes a separate wall at higher levels. A shape obvious on screen may still be ambiguous to an importer. Our proposed interface would need to show the mapping rather than assume a matching name proves a matching member. [Wall-label examples](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0115790).

#### Revision handling is already established competitor functionality

The v8.0.1 release note documents retaining adequate column reinforcement when revised analysis is imported. Its wizard asks users to map levels, configure new section sizes and reconcile added load cases/combinations. The original PDF has April 2019 metadata and shows the actual screens. This is more specific evidence than a general promise to handle revisions. [Column Update Design, pp. 4–6](https://bentleysystems.service-now.com/sys_attachment.do?sys_id=20bdb7d197118b540b8af4f3a253af25).

The v11.04 note, with July 2022 metadata, extends the workflow to beams. It describes level mapping, retained grouping where possible, geometry validation for regrouped levels and settings for new widths. Its column/wall change report lists additions/removals, level mapping, location/size changes and reinforcement changes. **Competitive implication:** preservation of accepted work and a change report already exist. Public notes do not fully disclose object-matching tolerances or guarantee rename/split/merge handling in current ETABS workflows. [Beam update, pp. 2–4; column change report, p. 8](https://bentleysystems.service-now.com/sys_attachment.do?sys_id=b0bdb7d197118b540b8af4f3a253af74).

#### What the actual validation packages establish

We inspected two original public Bentley ZIP packages without running their model files. They contain worked calculation documents and separate RCDC outputs, rather than only an index of example names. Both use STAAD inputs and date from 2019–2020; they do not test the current ETABS connection.

The six-page column worksheet, dated August 2020 by PDF metadata, includes a 500 × 800 mm section, M25 concrete, Fe415 steel and flexure/shear checks. Its reported capacity ratio reproduces: **217.17 ÷ 325.34 = 0.6675**, rounded to 0.67. The companion HTML and worksheet have inconsistent member/level labels. On p. 5, the printed shear expression gives 0.8219 MPa, while the displayed 0.7070 MPa corresponds to an effective-depth expression used in the HTML. This is a discrepancy in the older reference package, not a demonstrated defect in current RCDC. [Column validation package, PDF pp. 1, 4–5 and companion HTML](https://bentleysystems.service-now.com/sys_attachment.do?sys_id=3518062c9701ded436d5f33ef053afca).

The 30-page joint document, dated November 2019 by PDF metadata, includes worked beam capacity, joint equilibrium, drawings and model text. A selected check reproduces: **(1557.99 − 247.63) kN × 1000 ÷ 540000 mm² = 2.4266 MPa**, displayed as 2.43 MPa. However, some column capacities are obtained from RCDC interaction-surface screenshots. It is partly independent calculation evidence, not a wholly independent certification. The unit conversion must be explicit for the arithmetic to make sense. [Joint validation package, PDF pp. 7, 14–21](https://bentleysystems.service-now.com/sys_attachment.do?sys_id=a5f8c2ec9701ded436d5f33ef053afe9).

For a beginner, a demand/capacity ratio expresses demand relative to the reported capacity for a particular check and assumptions. It is not a direct percentage by which a member can be reduced. For a software product, every value should identify its model revision, member, level, load combination, units and origin. A reference value copied from the software being checked must be labelled separately from an independently calculated value.

#### Drawings, report interpretation and scope boundaries

Bentley distinguishes design grouping from physical geometry: similar columns may use the same reinforcement design while requiring separate elevation drawings because their attached beams differ. Automatic grouping checks specified similarities; manual grouping depends on engineer judgment. **Implication:** fewer design groups do not necessarily mean fewer drawing details or less review effort. [Grouping and elevations](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0116176).

A support example says a report can show zero bending moment when nominal reinforcement governs the reported requirement. That does not necessarily mean ETABS calculated zero moment. The attached explanatory workbook required authentication and was not accessed. Our interface should distinguish imported forces from the governing design condition and explain display conventions. [Beam-report explanation](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0116187).

Slab coverage must be specified by method and product. Ordinary RCDC documentation discusses one-/two-way and irregular slabs using particular design methods; this does not establish a general shell-result design workflow. Separately, RCDC FE ceased general availability in October 2024 and was scheduled out of WorkSuite in October 2025. Bentley identifies other applications for foundation and elevated-slab work. Do not add retired RCDC FE capabilities to an ordinary current RCDC comparison. [RCDC slab method](https://bentleysystems.service-now.com/community?id=kb_article&sysparm_article=KB0116230), [RCDC FE retirement](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0042758).

#### Customer evidence and buying economics

A Bentley-authored March 2018 case study names Toyo Engineering and attributes a 30% reduction in engineering resource hours to an integrated STAAD.Pro/Advanced Concrete Design workflow. It concerns a Malaysian industrial plant under European/Malaysian requirements. We read the document and visually inspected both pages on a public mirror. This is attributable vendor-published customer evidence, but not an independent experiment or a forecast for Indian ETABS building projects. [Toyo case study, pp. 1–2](https://cdn.featuredcustomers.com/CustomerCaseStudy.document/bentley_toyo-engineering_772183.pdf).

The observed annual starting prices put Structural WorkSuite **₹11,121 above STAAD.Pro Advanced**, a calculated difference of about 6.41%. That may matter if an office needs other included tools; it does not prove the broader bundle is economical for an RCDC-only user. Both are whole-package prices. Current standalone RCDC pricing, specific entitlement and applicable tax still need a matching quotation. [Bentley India packages](https://www.bentley.com/products/staad-pro/).

For an office already licensed for Advanced or WorkSuite, the additional license cost of using its RCDC entitlement may be zero; training, data preparation and checking remain costs. For a new buyer, the annual package price must be recovered through useful work. As an explicitly hypothetical illustration, valuing net recovered engineering capacity at ₹1,000/hour would require about **174 hours/year** to cover ₹1,73,563 alone. This is arithmetic, not an observed labor rate or saving, and excludes tax, setup and additional costs.

#### What this means for our proposed product

RCDC already sets a substantial benchmark for Indian RC calculations, reinforcement decisions, drawings and preservation of designs through revisions. A future Excel product should not claim these are missing from the market. Our possible advantage is narrower: make one recurring ETABS revision easier to inspect and complete through a clear Excel interface, consistent object mapping, explicit approval and verified fresh results. That remains a hypothesis to test against the incumbent workflow.

The next comparison should use one changed-load case and one changed-geometry case, recording total engineer/reviewer time, manual reconciliation, report differences and full operating cost. The public documents define useful tests, but this study has not executed them. Current ETABS compatibility, complete automatic round-trip behavior and the standalone purchase price remain consequential gaps.

### S-CONCRETE / Simcenter S-Frame Concrete — mass section checking

Now marketed by Siemens as Simcenter S-Frame Concrete, this product designs/checks beams, columns and walls, provides intermediate calculations and clause-based reports, and offers iterative section sizing. Multistory Designer imports ETABS forces for batch section design. Siemens explicitly lists IS 456 while stating that availability varies by element and release. [Simcenter S-Frame Concrete](https://www.siemens.com/en-us/products/simcenter/mechanical-simulation/s-frame/concrete/).

Official 2025 release notes add ETABS v22 import; current v23 compatibility, IS 13920 coverage and upstream model changes followed by global reanalysis were not established. [S-CONCRETE 2025 release notes](https://help.altair.com/sframe/s-concreteands-line_2025_releasenotes_english.pdf).

**Fit:** batch checking and section design with visible calculations. **Demo question:** show the exact Indian-code module/edition matrix and what happens when changed dimensions alter building stiffness.

### ETABS MATE — reinforcement detailing, checks and deliverables

**ETABS MATE close study: a substantial detailing application, with additional engineering checks, rather than merely a drawing exporter.** It is a strong comparator for the reinforcement-deliverable portion of our plan. Its separate application and imported-file workflow do not establish the Excel control panel or complete approved ETABS revision loop we intend. [Product description](https://www.etabsmate.com/etabsmate_en.htm).

The review examined the EN610 English manual, EN610 Quick Start, 2026 catalogue and 1.3.610 release note, including selected original page images. The lead independently inspected the material-import warning, revision instructions, reset command and a joint report. A research agent also examined older drawing samples, commercial terms and outside-use evidence. We did not run the software or reproduce a complete engineering calculation.

#### Follow a model through the documented workflow

ETABS performs the initial analysis and design. The Quick Start imports geometry from an **e2k file** and frame/wall design results from **Access or XML tables**, using **kgf and cm**. Additional result files can envelope requirements where element names agree. This combines demands; it is not evidence of replacing an old revision. Material strengths populate automatically only from materials named **CONC, REBAR and TIE**; otherwise defaults appear and require correction. Following model changes, the guide directs relabelling, reanalysis/redesign and fresh exports; derivative models must retain corresponding names. [Quick Start EN610, printed pp.3–13 and37](https://www.etabsmate.com/File/ETABS%20MATE%20Quick%20Start_EN.pdf).

For a beginner, imagine two linked workshop jobs. First, determine the strength needed. Then choose and describe reinforcement that can be assembled: bar sizes, positions, lengths, bends and connections. ETABS supplies demands to this workflow; a detailing application still needs engineering rules and review to turn them into usable construction information. A neatly drawn bar does not by itself demonstrate an adequate member.

The catalogue describes bar bending schedules with position, diameter, shape, length, quantity and weight, organized by floor and element type, plus Excel/text export. Here Excel is an output destination; that does not establish an Excel-hosted add-in or XLL architecture. [2026 catalogue, printed p.14](https://etabsmate.com/File/ETABS%20MATE%20Catalog_EN.pdf).

#### What is calculated, and what deserves scrutiny

The EN610 manual describes bar arrangements, cutoffs/development and joint-shear calculations; hooked-bar and joint defaults reference **ACI318-19**. No implemented or validated **IS456/IS13920** coverage was established. Three explicit qualifications matter: printed p.73 gives a support-steel application threshold of1cm² and says zero follows the code strictly; p.155 says its45°/15° joint classification angles require engineering judgment; p.163 describes material estimates as preliminary. [User Manual EN610, printed pp.54–58,70,73,148–155 and163](https://www.etabsmate.com/File/ETABS%20MATE%20User%20Manual_EN.pdf).

The manual's C3/Story1 joint report gives demand67,033.71kgf and reduced capacity60,966.1kgf. Our division gives **1.09952**, consistent with its displayed1.1. This checks the final arithmetic only; it does not validate the forces, reinforcement, classification or capacity method. The embedded report bears a2023 timestamp, so inclusion in a2026 manual is not proof of a newly executed case. [Joint report, printed p.154](https://www.etabsmate.com/File/ETABS%20MATE%20User%20Manual_EN.pdf).

In plain language, this ratio compares demand with the capacity used in that particular check. Approximately1.10 means demand is about10% higher. A useful report makes the assumptions and intermediate quantities inspectable, allowing a reviewer to investigate the reason. Reproducing a final division is only a small part of that review.

#### Revisions, manual edits and current versions

The1.3.610 release note supports ETABS23 imports and describes directional column-tie design. It adjusts spacing, cross-ties, double ties and diameter within configured limits. The command **Reset Ties Details of All Sections** explicitly discards user edits to column sections and regenerates calculated details. Separate commands regenerate or recheck secondary sections. These are internal detailing operations; their names do not establish changes written into ETABS. [Release note, printed pp.1,4–7](https://www.etabsmate.com/File/ETABS%20MATE%20Update%201.3.610.pdf).

The reviewed manuals did not establish a changed-model import that preserves and reconciles all deliberate MATE edits, or automatic ETABS write-back/reanalysis. This is an evidence gap, not a claim that an unexamined capability cannot exist. A useful demonstration would revise loads after a manual bar change and show exactly which values are retained, recalculated, rejected or flagged.

The current download page lists ETABS23/Windows11 but labels its public evaluation1.3.520. The ZIP pointer returned HTTP200 to a header-only request; no executable was downloaded or inspected. [Download centre](https://www.etabsmate.com/Download.htm). Registration instructions say purchasers receive activation files and the latest update after verification, so an older public evaluation may coexist with private delivery of updates. The delivered current build remains unverified. [Activation instructions](https://www.etabsmate.com/Register.htm).

#### Inspect the actual deliverable, not only the product claims

The official special-case PDF contains real reinforcement drawings and schedules, but it is historical: a sheet identifies v1.3.530 and19February2018. On its wall sheet, the10mm summary pairs1,697.2m of bar with141 twelve-metre bars. Our arithmetic gives141×12=1,692m; the stated stock count alone therefore does not account for all listed length. Rounding, waste and cutting assumptions are not explained. This is not a current-version defect finding or a verified purchase list. [Special-case drawing samples, physical p.3](https://etabsmate.com/File/Special%20Case%20Drawing%20Samples.pdf).

This distinction matters for buying: a quantity summary, a schedule of individual bar shapes and a feasible plan for cutting purchased stock answer different questions. The office should measure reconciliation and drawing-cleanup effort on its own project before valuing claimed automation savings.

Named projects and users are identifiable: the vendor portfolio and testimonials link Golden Palace with Pahlavan and Sari Mall with Lohrasbi. Those pages form one vendor-hosted evidence stream, rather than independent confirmations; claims involving both MATE and FOUNDA cannot establish MATE-only outcomes. [Project portfolio](https://etabsmate.ir/etabsmate_mega_structure.htm), [Vendor-hosted testimonials](https://etabsmate.ir/ETABSMATEcomment.htm).

Outside evidence also exists. Software Informer hosts comments dated2024 claiming repeated use, but identities, versions and projects are unverified and some wording repeats. [Software Informer comments](https://etabs-mate.software.informer.com/comments/). Omran Zagros advertises a completed three-hour workshop dated17December2024. This supports an external training channel, not independently checked engineering results or measured savings. [Workshop record](https://www.omranzs.com/product/etabsmate-workshop/). The bounded search found no independently verified project-level benchmark; it does not establish an absence of customers.

#### Price, licence and ongoing cost

| Advertised English offer | Activation price | Comparison meaning |
| --- | --- | --- |
| ETABS MATE | US$1,600 | The detailing application studied here |
| ETABS MATE + FOUNDA MATE | US$2,200 | Adds a separate foundation-focused product; not audited in this pass |
| MATE + FOUNDA + NICA | US$2,300 | A broader bundle; not equivalent to a complete verified Indian RC workflow |

[Published USD activation offers](https://www.etabsmate.com/price_en.htm). Standalone FOUNDA isUS$1,000; buying it with MATE separately totalsUS$2,600. TheUS$2,200 bundle savesUS$400 against those current individual offers. This is our price arithmetic, not measured engineering value. Country-specific payment arrangements, taxes and an Indian invoice remain unconfirmed.

The Persian licence permits unlimited use on the registered hardware, includes one year of free updates and states a three-year service period. Hardware transfer requires coordination and an unspecified fee. It excludes refunds/cancellation. Its commercial/third-party-use clause requires formal owner permission, but scope for ordinary professional client work remains ambiguous. The international offer does not resolve that wording. [FARASA agreement, clauses2,8,10–15](https://www.etabsmate.com/LicenseAgreement.htm).

The FAQ describes offline operation, unlimited reinstall/reactivation on the same computer and no annual support fee, while allowing later update charges. This does not establish free lifetime updates or override the agreement's service period. [Pre-purchase FAQ](https://www.etabsmate.com/faq.htm). Access import can require a matching database engine; the vendor presents XML as an alternative. [User FAQ](https://www.etabsmate.com/faq_users.htm).

**Fit for our own work:** shortlist it when drawings and schedules are the main bottleneck, conditional on code suitability, permitted client use, current delivery and review effort. **Fit for our possible product:** study its visible calculation assumptions, editable reinforcement and linked schedules. Import checks and preservation of deliberate edits are promising evaluation criteria, not yet proven market gaps or sales advantages.

| Our intended capability | What this study establishes | Remaining comparison |
| --- | --- | --- |
| Read ETABS information | Documented file import and result enveloping | Current project mapping and unit/material reconciliation |
| Design/check reinforcement | Documented detailing and selected checks | Exact Indian-code implementation and independent reference cases |
| Update and verify a model | Internal recalculation commands | Upstream changes, fresh analysis and reconciliation of overrides |
| Deliver reviewed outputs | Documented drawings, schedules and example calculation reports | Current output accuracy and total office review effort |

These rows synthesize the sources above; they are not software-test results. ETABS MATE is closer to the deliverable end of our proposed product than to its Excel controller. It does not displace StructPro as the Excel comparator or RCDC as the stronger documented Indian RC comparator in this study.

### VIS — useful design-interface benchmark

VIS serves ETABS/SAP2000/CSiBridge concrete design with Eurocode/Italian positioning. Its documented elements exclude slab and foundation design. [VIS for CSI programs](https://www.vis-concretedesign.com/vis-sap2000-etabs-csibridge/).

The January 2026 manual describes reimporting revised analysis models and transferring reinforcement where appropriate. Combinator can write load combinations into ETABS; that should not be confused with writing redesigned concrete members upstream. Reviewed codes did not establish IS 456/13920 support. [VIS User Manual 19.0](https://www.vis-concretedesign.com/wp-content/uploads/2026/01/User_Manual_1900.pdf).

**Fit:** learn from its interactive reinforcement workflow and outputs; it is a weaker documented match for an Indian-code purchase.

### IDEA StatiCa Concrete — specialist checks and difficult details

The ETABS concrete integration imports selected geometry, sections and forces into Detail, Member or Beam workflows. It is useful for specialist local engineering rather than automatically replacing an entire RC building-design office process. [ETABS concrete integration](https://www.ideastatica.com/bim-links/supported-integrations/etabsconcrete).

The matrix for IDEA StatiCa 26.0.4 explicitly lists ETABS 22/23 for concrete links. The exact link differs by destination product. [Supported integration versions](https://www.ideastatica.com/support-center/support-center-knowledge-base/bim-links-supported-versions-of-3rd-party-applications).

**Fit:** selected complex members/details. Indian concrete-code suitability and full ETABS write-back were not established; Indian steel-code support elsewhere must not be generalized to concrete.

### PROKON Concrete — modular calculations and schedules

PROKON offers concrete-member modules, calculation sheets with code references and reinforcement schedules. Its rectangular slab and rectangular column code lists include IS 456:2000; module coverage differs, and suite-wide IS 13920 support was not established. [PROKON Concrete](https://prokon.com/concrete/).

Reviewed official integration material did not establish a sufficiently specific modern ETABS read/write workflow. Excelcrib's separate bridge advertises ETABS2016–21 to GenCol3+ at$95/year, without identifying the dollar currency. GenCol's own specification names IS456:2000; a validated current Indian-code transfer, write-back and reanalysis sequence remains unestablished. The SideKick close study explains the engine/bridge distinction. [Excelcrib bridge](https://excelcrib.com/downloads/Plug-ins/ETABS-to-Prokon-GenCol.html), [GenCol code list](https://read.prokon.com/view/730985369/3/). **Fit:** modular office calculations and detailing alongside analysis software.

## 6. Optimization and emerging AI products

### ACE OCP — dedicated optimization with substantial historical evidence

**ACE OCP close study: one of the most directly relevant comparators for our proposed material-cost search and reanalysis stage.** Its documented workflow goes beyond retrieving finished ETABS results. It describes repeated analysis/design of newly generated models while retaining the reference model's analysis, material, loading and code assumptions. The research history adds substance to the product claim. Current purchase readiness is a separate unresolved question. [About ACE OCP](https://www.aceocp.com/about-ace-ocp/).

#### Follow the documented optimization loop

The official 13:03 presentation demonstrates SAP2000 and mentions ETABS input files. Its sequence opens a reference model, starts OCP through Tools, sets rates and allowed dimensions, and generates a model file per iteration. It evaluates the upper-bound, lower-bound and reference designs before continuing the search. On stopping, it saves the best-found model and produces a PDF comparison of assumptions and section changes. We read the complete caption transcript; this is historical demonstration evidence, not our own ETABS execution. [Official presentation, 8:40–12:21](https://www.youtube.com/watch?v=d3AK5IcWqZU).

In plain language, the engineer supplies the rules of the search: what may change, what must stay fixed, what counts as acceptable, and what cost is being minimized. The program tries alternatives inside those rules. Finding a cheaper candidate answers only the question that was defined. An omitted constraint does not become satisfied because the program displays a saving.

The January 2017 ETABS guide documents dimension bounds/locks and section grouping. Its RC objective includes concrete plus longitudinal and transverse reinforcement. Candidate EDB files go into a configurable project folder. Convergence controls limit non-improving cycles and analysis count. Two operational details matter: an infeasible reference can make the progress percentage differ from the results-form percentage; Run deletes earlier generated files while retaining parameters, whereas Reset removes both. Comparison outputs include feasibility, quantities and section changes. These are historical instructions, not verified behavior of a current build. [ETABS guide, physical pp.55–72](https://www.aceocp.com/wp-down/html/ACE_OCP_ETABS2016_Guide/files/assets/common/downloads/publication.pdf).

The FAQ recommends a feasible reference and acknowledges that a failing start can still yield a failing result. It advises reopening the resulting EDB/SDB and independently repeating analysis/design in CSI software. Its worldwide-use explanation relies on the host's regional settings; we found no named Indian-code validation case. The answer about certification points to published research, which does not establish certification of every shipping build or design. [ACE OCP FAQs](https://www.aceocp.com/aceocp-faqs/).

For our proposed product, retain three separate states: **candidate evaluated**, **specified checks passed**, and **engineer approved**. Also preserve run evidence before repeating a search. The reviewed material does not establish an enforced engineer-approval gate, original-file integrity guarantee, recovery from partial failure, or detection of stale analysis results. These are unanswered demonstration questions, not assertions that such safeguards are absent.

#### A beginner's example: less concrete can cost more

This is our own arithmetic example using invented quantities and rates, not a structural design or a market-price estimate. Assume concrete costs ₹6,000/m³ and reinforcement ₹70/kg. Suppose two hypothetical alternatives have these quantities:

| Alternative | Concrete cost | Reinforcement cost | Combined material cost |
| --- | --- | --- | --- |
| A | 10 m³ × ₹6,000 = ₹60,000 | 1,000 kg × ₹70 = ₹70,000 | ₹1,30,000 |
| B | 9 m³ × ₹6,000 = ₹54,000 | 1,200 kg × ₹70 = ₹84,000 | ₹1,38,000 |

B uses 10% less concrete but costs ₹8,000 more under this objective. Neither row is shown to pass engineering checks. Formwork, labour, congestion, procurement and construction sequencing are also outside this little calculation. This explains why our future tool should expose quantities, unit rates and excluded costs beside its percentage saving. The user must understand what “better” means in the selected comparison.

#### What the published savings evidence supports

Nikos D. Lagaros's foundational paper appeared online on 13 December 2013 and in the June 2014 journal issue. It concerns the research platform, rather than validating today's commercial executable. [Springer publication record](https://link.springer.com/article/10.1007/s00158-013-1027-1).

Its five comparisons use engineers' original SAP2000 files and matching analysis/design assumptions. Material rates are €250/m³ concrete, €2/kg reinforcement and €3/kg structural steel. Reported outcomes are below; times come from a two-node i7-950 cluster and are not modern-PC forecasts. [Author-posted manuscript, §8 and Table 3](https://www.researchgate.net/publication/271736805_A_general_purpose_real-world_structural_design_optimization_computing_platform).

| Research example | Material-cost reduction | FE analyses | Reported runtime |
| --- | --- | --- | --- |
| Composite three-storey building | 16.1% | 750 | 4.92 hours |
| Five-storey RC building | 21.8% | 480 | 5.85 hours |
| Aghia Paraskevi Town Hall | 27.6% | 660 | 44.33 hours |
| Bird's Nest | Nearly 10% | 420 | 5.29 hours |
| Water Cube | Nearly 10% | 900 | 40.27 hours |

These compare computed alternatives with implemented designs; construction of the alternatives is not established. The examples use European, American or British provisions, not Indian validation. The stated objective has no separate labour/formwork term. Changing rates changes the economic comparison. Named landmark models do not establish that their owners purchased the shipping product or realized these savings.

A later paper, published 10 May 2018, reports an unnamed Persian Gulf high-rise engagement requested by its owners, with approximately 8% cost reduction. That is stronger engagement evidence than an unexplained portfolio image, but neither client identity nor construction of the alternative is verified. The paper also reports a Jinan stadium comparison; its model element counts differ from the product website, so the two should not be silently treated as one identical model. [2018 publication](https://link.springer.com/article/10.1007/s00158-018-1998-z), [author manuscript, §7.2](https://www.researchgate.net/publication/324965158_The_environmental_and_economic_impact_of_structural_optimization).

Rande Robinson's 6 April 2017 hands-on article reports 52.3% material-cost improvement in 25 minutes 53 seconds using a vendor-supplied SAP2000 example. The author cautions that a well-developed starting design offers less scope. **ACE-Hellas sponsored the article.** It documents a reviewer operating the software, not an independent representative customer-ROI study. Its US$2,200 price is historical and is not used as a current quote. [Engineering.com review](https://www.engineering.com/reviewing-ace-ocp-a-simple-easy-to-use-program-for-the-aec-world/).

Outside academic use also exists. An Isra University 2021 thesis abstract identifies ETABS, PROKON, ACE-OCP and SCADA-Pro alongside manual and architectural changes. Its 9.25% total-project reduction belongs to that combined value-engineering exercise, not to ACE OCP alone. Full methods and implemented savings were not verified. [University thesis record](https://www.iu.edu.jo/iuthesis/search/thesis_details.php?id=457).

The related December 2021 conference abstract separates ACE-OCP/SCADA-Pro changes, reporting 8.23% structural-work cost reduction, from subsequent manual changes. It appears related to the thesis, so it is not counted as another independent adoption case. [Original proceedings, abstract p.12](https://cdn.iferp.in/conf-proceedings/2021/ICAKMPET_2021_%20Book.pdf). A July 2023 Epoka thesis record adds an eight-storey RC academic study using SCADA Pro and ACE-OCP; full-text access failed, so its numerical outcome remains unverified. [Institutional metadata](https://dspace.epoka.edu.al/handle/1/2555?show=full).

#### Current cost, compatibility and licence questions

On 3 September 2026, the shop's rental selections agreed with its variant data; Permanent did not. [ACE-Hellas shop](https://www.ace-hellas.gr/shop/product/ace-ocp-gia-etabs/).

| Licence option | Observed amount | Status |
| --- | --- | --- |
| Three months | €215 | Display and variant agree |
| Six months | €363 | Display and variant agree |
| Twelve months | €659 | Display and variant agree |
| Permanent | Unresolved | Selected display €659; permanent variant €1,480 |

**The earlier unqualified €1,480 permanent-price statement is withdrawn.** No checkout occurred. Calculated continuous access: four quarterly rentals €860; two half-year rentals €726; one annual term €659; three annual terms €1,977. Taxes, host software and other ownership costs are excluded; regional supply remains unresolved. The maintenance wording names SCADA Pro, so it establishes no OCP maintenance entitlement. [Maintenance terms](https://www.ace-hellas.gr/ipiresies/simvolea-sintirisis/).

The public download page still specifies ETABS 2016/17 x64, with 2016 at least v16.1.0. It advertises a 60-day noncommercial trial; the download path requires signup, where inspection stopped. No current ETABS 22/23 or Windows 11 support matrix was established. No executable was obtained or run. [Download requirements](https://www.aceocp.com/download-software/aceocp/), [ETABS download landing page](https://www.aceocp.com/download-software/software/?product_id=139). The About page requires always-on internet for licensing. Old public documentation and news do not prove discontinuation. [System requirements](https://www.aceocp.com/about-ace-ocp/), [news index](https://www.aceocp.com/pr/).

The EULA provides different fixed, floating and server entitlements depending on the order; the shop does not establish which its amounts buy. Its third-party-data and service restrictions need clarification for client projects and any proposed commercial integration. This is not a conclusion that ordinary consultancy is prohibited. The intended use and ordering agreement matter. OCP should not be assumed to be a freely reusable engine inside our XLL. [Licence agreement, §§2–3](https://www.aceocp.com/ace-ocp-software-license-agreement/).

#### What changes in our buying and building decision

For our own engineering work, ACE OCP merits evaluation if current compatibility, trial delivery and suitable licence rights can be established. Its public history supports spending evaluation time; it does not yet support purchasing for our modern Indian RC workflow. A useful trial would freeze the model, codes, units, rates and permitted changes, then independently rerun the winning EDB and account for setup/checking time.

For a possible product, “automatically try sizes and rerun ETABS” is already a documented competitive capability. ACE OCP is now a stronger dedicated-search comparator than our earlier brief profile suggested. StructPro remains closer to the Excel operating experience; RCDC contributes more specific Indian RC reference evidence; ConGro contributes a current beta assistant and separately initiated optimizer. This is a comparison of different parts of our intended product, not a single overall ranking.

Our proposed differentiation still needs customer evidence: a current, understandable Indian RC revision workflow with explicit quantities, traceable checks, recorded approval, preserved model/run history and verified revised results. Competitors' documentation gaps alone do not establish that customers lack these capabilities or would buy them from us.

### ConGro AI — chat agent and separately initiated optimizer

**ConGro close study: substantial automation overlap, with a consequential architecture correction.** The founder distinguishes the chat agent from an optimizer the user starts separately. We should compare both components with our proposed workflow without treating them as one autonomous agent that decides when to optimize.

#### Separate the assistant from the engineering loop

The founder's April description explains a desktop application that generates Python to control an open ETABS session through CSI OAPI, reads execution errors and retries. April's public launch establishes a product chronology, not validated engineering performance. This is a different interface architecture from our intended Excel-hosted XLL. [Founder description, 15 April 2026](https://congro.ai/blog/why-congro-ai/), [public launch, 28 April](https://congro.ai/blog/congro-ai-public-launch/).

In an attributable reply to Serra Cimilli-Erkmen, the founder says the chat agent handles modelling/analysis while the user separately triggers an optimizer applying coded engineering rules. The agent cannot initiate or operate that optimizer. His v0.60.8-beta demonstration account reports a mixed-material model, 61 calls, five completed analysis cases and four recovered errors, while explicitly excluding engineering validation. Both were read as indexed primary text; the original reply permalink and full video were unavailable. [Founder activity and clarification](https://www.linkedin.com/in/afrasayab).

An analogy is an assistant beside a programmed testing machine. The assistant helps prepare and inspect the work; the engineer starts the machine's defined procedure. Keeping those roles separate can make responsibilities clearer. It does not independently prove the programmed rules are correct or complete.

#### What the published optimizer does

The catalogue describes at most four rounds, ordered Walls → Steel/HSS → Concrete → Drift → Slabs, with reanalysis after changes. It stops below 2% change in a DEAD+SDL reaction-based weight measure. RC resizing uses ACI 318-14/19 and native ETABS Check mode, increasing reinforcement before dimensions; the drift search uses steel W-sections. Indian-code optimization was not established. [ETABS catalogue, operations 146–151](https://congro.ai/software/etabs/).

The same catalogue describes identity checks, selected backups and analysis-completion checks, but operation 152 saves the active model in place. It also gives differing visible/hidden-window advice and wall-rebar availability descriptions. Their conditions need clarification; they do not establish blanket rollback or universal API failures. Its version label remains 0.50.1-beta. [Operations 001–019, 117–118, 133–150 and 152](https://congro.ai/software/etabs/).

**Stabilization, a passing design and minimum cost are three different results.** Consider this invented teaching example, with an arbitrary weight index and one demand/capacity ratio:

| Iteration | Weight index | Governing demand/capacity ratio |
| --- | --- | --- |
| Previous | 1,000 | 1.12 |
| Current | 990 | 1.12 |

The weight index changed by only 1%, but demand still exceeds capacity. This is not a ConGro result or an allegation about its final-status handling. It illustrates why our evaluation must ask for separate answers: did the search stop, did every required check pass, and was any cost objective actually improved? A search can also stop because it reached a limit or found no permitted alternative. None of those outcomes should be hidden behind a single success label.

#### Approval and recovery are narrower than a complete review process

The July Agent Mode announcement promises confirmation before destructive actions, overwriting or discarding analysis results. That is useful, but does not establish approval before every write. It also describes per-action metering and a budget stop; those concern operation and expenditure, separately from engineering acceptance. [Agent Mode, 26 July 2026](https://congro.ai/blog/congro-ai-agent-mode-update/).

A backup helps recovery; working on a separate copy protects the original throughout the operation. Our proposed demonstration must show the exact file receiving edits. Likewise, retrying a command after an error needs read-back of the current state: if part of an earlier change succeeded, repeating it must not accidentally duplicate loads or objects. These are evaluation requirements, not established defects in ConGro.

#### The release history supplies specific verification cases

A founder post announcing v0.49.3-beta describes four corrections affecting engineering answers: seismic drift amplification, wall strength-reduction calculations, wind forces assigned to disconnected joints, and steel-deflection checks accepting members they could not verify. These are vendor-disclosed historical fixes. They are neither proof of current defects nor independently verified regression results. No accompanying reference models and expected outputs were established. [Founder release post, 1 June 2026](https://www.linkedin.com/posts/afrasayab_congro-ai-ai-for-structural-engineering-activity-7467302402027769856-BAg_).

These disclosures make a better demonstration brief than a general request to show compliance. We should ask the vendor to reproduce the relevant corrected cases on the offered build, provide the starting model and expected result, and show the final files and calculations. A solver completing its work does not establish that the intended loads, connections or assumptions were modelled correctly.

#### Distribution, support and data handling

The previously resolved 0.60.8-beta Windows installer remained accessible through an ordinary HTTPS header request in this pass: HTTP 200, 558,709,708 bytes, upload timestamp 31 July 2026. The executable body was not downloaded. The latest download redirect could not be revalidated because normal certificate checks failed; earlier resolution and current artifact existence are separate observations. Neither identifies a supported ETABS/Windows version matrix or proves installation/signing. [Versioned installer artifact](https://f005.backblazeb2.com/file/congro-ai-releases/ConGro%20AI%20Setup%200.60.8-beta.exe), [official download route](https://congro.ai/download).

The terms require a separate subscription for each person and do not promise an SLA or default code compliance. They restrict using the service or outputs to develop a competing product; intended evaluation rights would need clarification before any such experimentation. This study used public evidence and did not run the service. [Terms, 17 April 2026](https://congro.ai/terms/).

The privacy policy lists cloud chat processing and retention, but says model files/geometry/results are not collected beyond material explicitly pasted into chat. It does not clearly explain automatically retrieved model context. The optional diagnostic-upload statement must not be generalized to ordinary chat. Neither all-local operation nor undisclosed model uploading was established. [Privacy policy](https://congro.ai/privacy/).

#### Buying and product implications

Section 9 separates subscription prices, usage credits and refunds. The relevant economic test is the cost of a reviewed result, including setup, host licences and engineering time. A low monthly fee does not establish low total cost if substantial correction or checking is required. Conversely, a well-bounded repetitive task could justify the subscription without needing a complete building-design system.

For our own use, ConGro is a candidate for a controlled modelling/analysis and separately initiated optimization trial after compatibility and access questions are resolved. For our product research, it demonstrates why we should distinguish language-driven commands, fixed engineering checks, search logic and approval. No reproducible independent customer benchmark was established; no full ConGro video or runtime sequence was examined in this study.

The next decisive evidence is one version-linked changed-column test: original and working files identified, permitted edits previewed, final changes read back, expected analysis cases completed, reference checks compared, interruption recovered, and the actual credit ledger retained. That would test useful operation, engineering correctness and total cost together.

### GoCalc and Structon.AI — watchlist, limited evidence

GoCalc advertises separate AI and Excel add-in products. Its AI documentation describes live ETABS 20+ model actions and selectable AI providers. The public website contains unfinished template language, so commercial/support maturity remains uncertain. [GoCalc](https://gocalcsoft.somee.com/), [GoCalc AI for ETABS](https://gocalcsoft.somee.com/gocalcai_Etabs.html).

Official indexed text for Structon.AI describes an experimental, invitation-only service with design/automation claims; ETABS appears in its higher plan. Direct retrieval produced a JavaScript shell. It remains a discovery lead, not a purchase recommendation or verified price benchmark. [Structon.AI](https://structon.ai/).

## 7. Complete alternatives to the ETABS-led workflow

### Tekla Structural Designer

Tekla combines analysis/design, model-linked reports and Indian-code support in its own environment. It offers a 30-day trial. [Tekla Structural Designer India](https://www.tekla.com/in/products/tekla-structural-designer).

Its concrete autodesign documentation describes iterative reinforcement selection. Do not extend that to autonomous optimization of every RC member's dimensions. [Concrete member autodesign](https://support.tekla.com/nl/doc/tekla-structural-designer/2026/chb_autodesignprocessconcretemembers).

**Fit:** consider when we are willing to change the main analysis/design environment. Compare modelling assumptions, reviewer familiarity and deliverables as well as click counts.

### ProtaStructure

Prota's June 2026 announcement for Suite 2027 describes ETABS v13–23 import/export through files, Excel table exports and new Indian seismic-code support. These are vendor release claims; exchange completeness and applicability to a project need testing. [ProtaStructure Suite 2027 announcement](https://protasoftware.com/community/blog/prota-structure-suite-2027-new-features/).

The published code catalogue includes IS 456:2000 and IS 875:2015. [Prota design codes](https://protasoftware.com/products/international-design-codes-standards/).

**Fit:** an integrated modelling, design and detailing alternative. File interoperability can reduce re-entry but does not guarantee live synchronization or equivalent results after migration.

### CYPECAD

CYPECAD combines building analysis/design with reports, drawings and quantities. [CYPECAD](https://info.cype.com/en/software/cypecad/).

Its official catalogues document Indian seismic and ductile-detailing support, with license/module qualifications. [IS 1893 Part 1:2016](https://info.cype.com/en/codes/is-1893-part-1-2016/), [IS 13920:2016](https://info.cype.com/en/codes/is-139202016/).

**Fit:** another serious full-workflow alternative, particularly if drawing production matters. Evaluate selected modules and analysis assumptions rather than assuming the largest package is necessary. Migrating an established ETABS office also requires training and benchmark-model reconciliation.

## 8. Excel/XLL foundations and public projects

These belong in the build-versus-buy decision, but they are not ready-made replacements for qualified structural design software.

| Foundation | What it contributes | Commercial implication |
| --- | --- | --- |
| Excel-DNA | .NET-based Excel/XLL add-in development | Free framework; we still own the engineering, interface, installer and support. [Introduction](https://excel-dna.net/docs/introduction/) |
| PyXLL | Python integration in desktop Excel | US$35/user/month or US$349/user/year; end users also require licenses. [PyXLL pricing](https://www.pyxll.com/pricing.html) |
| xlwings | Excel/Python automation with free and paid offerings | Free local open-source use; Business is advertised at US$6,000/year for additional capabilities. [xlwings pricing](https://www.xlwings.org/pricing) |
| BHoM ETABS Toolkit | Open-source ETABS model/results integration | Useful integration foundation; supported versions and license obligations need matching to the intended distribution. [ETABS Toolkit](https://github.com/BHoM/ETABS_Toolkit) |
| ExcelCSIToolBoxAddIn | Public Excel/CSI add-in project | A learning/reference comparator; public code alone does not establish a supported commercial engineering product. [Repository](https://github.com/Anhbq1298/ExcelCSIToolBoxAddIn) |
| ETABS-mcp | Public AI-tool interface for ETABS actions | README claims broad actions and Indian-code presets. A clear reuse license and validated design scope were not established. [Repository](https://github.com/mdvaleed7/ETABS-mcp) |

Python in Excel is a different product: Microsoft's cloud execution restrictions prevent treating it as a direct controller of a local ETABS session. Desktop automation packages should be assessed separately. [Data security and Python in Excel](https://support.microsoft.com/en-us/excel/python/data-security-and-python-in-excel).

## 9. Public prices and licensing: compare the whole purchase

Prices below were observed on 3 September 2026. Currencies remain as published; no exchange-rate conversion is implied. These are public offers, including regional Indian page prices where stated, not vendor quotations for our requirements. Taxes, modules, support and availability differ. Subscription, perpetual, activation and custom-service prices are not interchangeable.

| Product | Published offer | Important qualification |
| --- | --- | --- |
| ETABS | Plus US$7,439; Nonlinear US$11,903; Ultimate US$17,855 perpetual | Annual maintenance separately listed; Ultimate three-month lease US$2,289. The host license is additional to most add-ins. [CSI sales](https://www.csiamerica.com/sales) |
| StructPro | Quote required; no verified numeric price | Floating access advertised, but EULA user/device terms need reconciliation; internet required; seven-day trial advertised; public installer link broken. [Purchase](https://www.structprollc.com/p/purchase.html), [EULA](https://www.structprollc.com/p/eula.html) |
| SideKick | India display ₹17,576 including GST; perpetual | One licence; current host support/delivery unverified. [Observed order display](https://excelcrib.onfastspring.com/ETABS-Sidekick-Perpetual) |
| CalcTree | Business US$34/user/month; Enterprise custom | The enterprise ETABS desktop connection is not established as included in the US$34 plan. [Pricing](https://www.calctree.com/pricing) |
| CivilAI | ₹50,000 one workflow; ₹2,00,000 connected workflows; ₹5,00,000 end-to-end | Advertised one-time custom service, with different support periods; delivery claims need demonstration. [Pricing](https://civilai.arpitkhandelwal.com/pricing) |
| ETABS MATE | US$1,600 activation; MATE/FOUNDA bundle US$2,200 | Unlimited use on registered hardware; updates free one year, service period three years. Transfer/update fees and client-use permission unresolved. [Price](https://www.etabsmate.com/price_en.htm), [Agreement](https://www.etabsmate.com/LicenseAgreement.htm) |
| RCDC | Standalone India price unknown; included in STAAD.Pro Advanced, starting ₹1,73,563/year, or Structural WorkSuite, starting ₹1,84,684/year | These are whole-package, 12-month, one-license prices. Basic STAAD.Pro at ₹97,887 has restricted RCDC functions. [Bentley India prices](https://www.bentley.com/products/staad-pro/), [current RCDC entitlement](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0050365) |
| S-CONCRETE | Current matching quote required | Confirm concrete modules, regional code coverage and host compatibility. |
| VIS | €1,000 Pro; €1,200 Advanced | VAT excluded; optional annual maintenance €200/€250. Confirm regional terms. [Pricing](https://www.vis-concretedesign.com/pricing/) |
| IDEA StatiCa Concrete | Matching product/region quote required | General ranges cover multiple products; 14-day trial advertised. [Pricing](https://www.ideastatica.com/pricing/) |
| PROKON Concrete | €1,629/year; advertised first year €815 | VAT excluded; promotion conditions apply. [Store](https://store.prokon.com/product/prokon-concrete/) |
| ACE OCP for ETABS | €215/3 months; €363/6 months; €659/12 months | Permanent price unresolved: display €659 versus configured €1,480. Modern compatibility, tax and regional terms unconfirmed. [Official shop](https://www.ace-hellas.gr/shop/product/ace-ocp-gia-etabs/) |
| ConGro AI | US$25/month for 1,500 credits; US$100/month for 7,500 | Annual website plan data lists US$250/US$1,000, with a conflicting discount banner; see below. No free trial advertised. [Plans and credits](https://congro.ai/) |
| GoCalc | US$49 for one year, separately for AI and Excel add-in | Provider costs may be additional for AI use. Early-product evidence caveats apply. [Products](https://gocalcsoft.somee.com/) |
| Tekla Structural Designer | ₹2,31,105/year plus tax | India page snapshot; dynamic prices varied between captures, so obtain a current quote. [India product page](https://www.tekla.com/in/products/tekla-structural-designer) |
| ProtaStructure | Quote required; rental/perpetual options | 30-day trial advertised. [Product and licensing](https://protasoftware.com/products/protastructure/) |
| CYPECAD | Starter €900; Basic €1,400; Advanced €3,500; Expert €6,600 | Package contents differ; captured listing did not establish term/tax or an India quotation. [CYPE shop](https://shop.cype.com/en/software/cypecad/) |

The price spread shows different purchases, not a single market clearing price. A small utility, specialist engineering package and bespoke office automation service solve different problems. A future product cannot justify its price by averaging these figures.

Total ownership cost should include host software, the add-on, setup, template conversion, training, checking, update maintenance, downtime and any metered AI charges. Existing host licenses may be a sunk cost for our own purchase, but new commercial customers still face the full dependency stack.

### One-year and three-year software costs

The following figures are **calculated illustrations, not quotations or complete ownership costs**. They assume one purchased license/account as applicable, unchanged prices, continuous subscriptions and the stated billing basis. They exclude taxes, foreign-exchange/payment fees, host software, onboarding and additional usage. Different products are not equivalent substitutes just because their totals fit in one table.

| Product / billing basis | First 12 months | Total over 36 months | What the figure covers |
| --- | --- | --- | --- |
| ETABS MATE — original hardware, no paid updates/transfers | US$1,600 | US$1,600 | Conditional base activation outlay, not full ownership cost or confirmed client-use quotation. [Price](https://www.etabsmate.com/price_en.htm), [Licence](https://www.etabsmate.com/LicenseAgreement.htm) |
| SideKick — perpetual, pre-tax | ₹14,894.92 | ₹14,894.92 | Displayed ₹17,576 less GST₹2,681.08; one purchase. [India offer](https://excelcrib.onfastspring.com/ETABS-Sidekick-Perpetual) |
| CalcTree Business — monthly billing | US$408 | US$1,224 | US$34 × 12 or 36; enterprise ETABS connector excluded. [CalcTree pricing](https://www.calctree.com/pricing) |
| ConGro Foundation — monthly billing | US$300 | US$900 | US$25 × 12 or 36; top-ups excluded. [Published plan data](https://congro.ai/assets/index-BvpOl7Dt.js) |
| ConGro Structure — monthly billing | US$1,200 | US$3,600 | US$100 × 12 or 36; top-ups excluded. [Published plan data](https://congro.ai/assets/index-BvpOl7Dt.js) |
| STAAD.Pro Advanced — annual package including RCDC | ₹1,73,563 | ₹5,20,689 | Whole package at current starting price, not a standalone RCDC price. [Bentley India pricing](https://www.bentley.com/products/staad-pro/) |
| Structural WorkSuite — annual package including RCDC | ₹1,84,684 | ₹5,54,052 | Broader whole package at current starting price. [WorkSuite pricing](https://www.bentley.com/products/structural-worksuite/) |
| PROKON Concrete — eligible first-year promotion | €815 | €4,073 | €815 + two renewals at today's €1,629 standard rate. [PROKON store](https://store.prokon.com/product/prokon-concrete/) |
| Tekla Structural Designer — annual | ₹2,31,105 | ₹6,93,315 | Three annual payments at the displayed rate; tax excluded. [Tekla India](https://www.tekla.com/in/products/tekla-structural-designer) |
| PyXLL — annual developer platform | US$349 | US$1,047 | One user's integration-platform license; no structural engineering application included. [PyXLL pricing](https://www.pyxll.com/pricing.html) |

The monthly-billing illustrations do not apply annual discounts. CalcTree's FAQ advertises 15% off annual subscriptions: applying that to US$34 × 12 gives **US$346.80/year**, or **US$1,040.40 over three years** if unchanged. This is still an arithmetic illustration, not an enterprise connector quotation. [CalcTree pricing FAQ](https://www.calctree.com/pricing).

**ConGro annual-price correction:** the earlier US$240/US$960 figures are withdrawn. The earlier successful same-day website-data extraction lists **US$250/year for Foundation and US$1,000/year for Structure**, with monthly allowances. Three unchanged annual payments total US$750/US$3,000; savings are 16.67%, conflicting with the 20% banner. Later certificate failures prevented rechecking the configuration. These remain published-data observations, not checkout quotations. [Pricing configuration and FAQ](https://congro.ai/assets/index-BvpOl7Dt.js).

The same earlier configuration lists credit packs of 600/1,500/3,300/7,000 for US$10/25/50/100. Packs require an active subscription; monthly credits are used first, with a rolling one-year pack expiry. Post-cancellation access and the pack exception to broad no-rollover policy wording remain unresolved. [Pack configuration](https://congro.ai/assets/index-BvpOl7Dt.js), [credit policy](https://congro.ai/terms/).

ConGro's ETABS meter charges 6 credits per message, 3 per read and 6 per change. Two reads and two changes therefore cost **24 credits**, excluding extras. Optimization lists 45 credits, with refunds of 22 for cancellation/failure, 45 for fatal abort and none for partial convergence. Nested action charges remain unclear. [Usage schedule](https://congro.ai/).

With no other spending, the monthly allowances cover at most **62 or 312 identical 24-credit requests**, respectively; each leaves 12 credits. This is an arithmetic budget illustration, not a cost per building or guaranteed usage for a prompt. Compare the actual ledger with the work completed, including unsuccessful attempts and verification.

Money refunds are separate from restored usage credits. Ordinary cancellation preserves access through the paid period without a prorated refund. The policy excludes dissatisfaction with AI output; it lists limited exceptions for billing errors, accidental annual renewal reported within seven days, qualifying outages and unauthorized charges. [Refund policy](https://congro.ai/refund-policy/).

If the office already holds an entitled STAAD.Pro Advanced or Structural WorkSuite license, RCDC may have **no additional software-license charge within that entitlement**; implementation and review effort still cost time. Bentley documents a separate RCDC license for ETABS users, but a current standalone India quote is still needed. Virtuoso subscriptions renew automatically, with cancellation notice required 30 days before renewal; applicable tax is calculated at checkout. [RCDC license selection](https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0111693), [Bentley subscription terms](https://www.bentley.com/en/products/licensing-and-subscriptions/).

For ETABS MATE, the constant US$1,600 illustration assumes the same hardware and no paid updates; keeping current releases, transferring hardware and establishing permitted client use can change the purchase. Fees are unknown. CYPECAD term/maintenance and quote-only products still prevent comparable three-year estimates. For custom services, future modifications/support also remain unknown. Unknown is not zero.

### Costs beyond the advertised license

| Cost item | How to include it in our comparison | Why it affects the decision |
| --- | --- | --- |
| Required software | Identify the exact ETABS edition/version, desktop Excel and optional CAD/design modules needed for the chosen workflow | An add-on price does not purchase the host applications |
| Setup and migration | Record configuration, template conversion, model mapping and training hours | A cheap license can require substantial initial work |
| Engineering checking | Measure reviewer time and manual corrections on the same benchmark task | Automation only saves time if its outputs can be reviewed efficiently |
| Ongoing operation | Add maintenance, support extensions, upgrades, metered AI credits and retraining | First-year promotions and included support may end |
| Team licensing | Confirm named-user, machine, account or concurrent-seat rules and volume pricing | Five engineers do not always require five identical subscriptions |
| Procurement | Confirm applicable tax, payment fees, currency, invoice terms and permitted use | A displayed foreign price is not the final payable Indian amount |

Use **first-year total cost = software/host fees + setup and training + review effort + usage charges + applicable procurement costs**. For three years, add the next two years of renewals, support, operation and review effort; do not repeat a perpetual purchase unless a required upgrade creates a new charge.

For our own product, development cost should be tracked separately: engineering specification, programming, reference calculations, test models, installation/deployment, documentation and continued version support. Excel-DNA's free license does not make that work free. We do not yet have enough scope or measured hours to attach a reliable build-cost estimate.

## 10. What to evaluate for our own engineering work

These are **conditional shortlists**, based on documented fit rather than a tested ranking.

| Our immediate problem | First comparison | Price reference | Cost and capability gate |
| --- | --- | --- | --- |
| Repetitive Excel/ETABS operations | Native ETABS, StructPro, SideKick | SideKick ₹17,576 including GST; StructPro quote | Host licenses, current-version support and total time saved |
| Indian RC design and detailing | RCDC; S-CONCRETE for section checks | RCDC standalone quote; Advanced bundle from ₹1,73,563/year | Existing entitlements, modules/codes, reinforcement control and usable outputs |
| Drawing/BBS production | CSI/CAD workflow, ETABS MATE, RCDC | MATE US$1,600 activation; other licenses/terms to confirm | Indian-code suitability, permitted client use, current delivery and drawing-cleanup effort |
| Reusable calculations and reports | CalcTree; current spreadsheet library | Business US$34/user/month; ETABS enterprise quote | Connector cost, template migration and result freshness |
| Repeated alternatives | Native ETABS, ACE OCP, ConGro | ACE annual rental €659; permanent unresolved; ConGro US$25/100 monthly plans | Compatibility, reanalysis, supported checks, licence rights and actual credit use |
| Replace the core workflow | Tekla, ProtaStructure, CYPECAD | Tekla ₹2,31,105/year; Prota quote; CYPE €900–6,600 packages | Purchased modules, license terms, migration and benchmark equivalence |

Price sources and qualifications are in section 9; these rows summarize purchasing routes and must not be added together as though every listed product is required.

**RCDC, StructPro, ConGro, ACE OCP, SideKick and ETABS MATE now have close studies at the public-evidence level.** They provide different benchmarks: Indian RC references, Excel operation, beta automation, historical material-cost search, productivity and reinforcement deliverables. Runtime evaluation remains open. VIS remains a parked comparison for reinforcement transfer after model revisions; its regional-code fit must remain separate from its workflow value. Research will resume only when the user requests it.

“Better” should mean a better result for a specified job. A specialist member checker can be better for a difficult local detail while being unsuitable as the office's main workflow. A cheap toolbox can be the best purchase when the missing task is only repetitive data manipulation.

## 11. Possible customers and product opportunities

The following segmentation is a hypothesis for interviews, not a measured market census.

| Potential customer | Likely user / decision maker | Need to test |
| --- | --- | --- |
| Small structural consultancy | Design engineer / principal | Whether recurring revisions consume enough time to justify a paid tool |
| Mid-size design office | Engineers and reviewers / technical director | Standardized calculations, controlled templates and reviewable changes |
| Larger multidisciplinary firm | Automation team / engineering and IT leadership | Deployment, version support, model governance and integration with existing tools |
| Detailing-focused team | Detailer/checker / team owner | Drawing/BBS throughput and compatibility with local office conventions |

A promising initial proposition is: **help an Indian RC design office complete one recurring ETABS revision with traceable calculations and a clearly reviewed model update**. Its possible advantages are hypotheses:

- Preserve trusted office spreadsheets while explicitly linking their inputs to identified model objects and result sets.
- Show proposed changes and reasons before application, and produce a readable difference report afterward.
- Identify stale analysis, mixed units, unsupported elements and incomplete checks instead of silently producing an apparently complete answer.
- Recheck a changed model and connect each final conclusion to the model revision, analysis run and calculation version used.
- Maintain a narrow, explicit matrix of supported ETABS/Excel versions and Indian-code provisions, with reproducible reference cases.

Competitors already advertise transparency, connected calculations and automation. These attributes become a business advantage only if users experience a demonstrable improvement over what they already own. A stronger claim would be “this particular revision takes less total effort with the same agreed review standard,” supported by measured trials.

Three possible business forms deserve comparison. A **small paid utility** has a narrow promise and lower onboarding burden. A **custom service** can address office-specific needs but may require substantial work for every customer. A **repeatable firm product** can scale only after common needs, reliable deployment and affordable support are demonstrated. The research does not yet establish which is viable.

## 12. Economics without an invented market size

No defensible count of Indian ETABS firms, paid seats or buyers for this precise workflow was established. Broad construction/BIM market figures would not answer that question. We should not claim a large addressable market by multiplying an unrelated industry total.

A simple illustration helps explain customer value. Assume five engineers each recover three useful hours per week for 46 weeks, valued at ₹750 per hour: **5 × 3 × 46 × ₹750 = ₹5,17,500 of annual engineering capacity**. Every input is an illustrative assumption, not a market finding or observed saving. Capacity becomes financial benefit only when the firm can use it for valuable work or avoid an actual cost. Training, checking and support effort must be deducted.

For a future product, build the estimate from observed evidence: reachable firms in a defined segment × fraction with the problem × plausible paid seats or firm contracts × tested annual price. Record support cost, acquisition effort and retention separately. Interviews establish the problem; successful paid pilots begin to establish commercial demand.

## 13. Parked research and a future demo test

Research is paused. The following activities remain future proposals; no outreach or trials have been performed or scheduled. The companion product blueprint records B01–B12 for screened/unstudied products and foundations, B13–B19 for unresolved close-study questions, and B20–B23 for engineering specification, benchmark, customer and economic evidence. Reopen only the item that could change a concrete decision; broad research is not a prerequisite for the specified P0 shell or P1 beam calculation.

- Interview roughly twelve relevant offices across small, medium and larger teams. This is a discovery sample, not a statistically representative survey. Ask them to reconstruct their last real model revision and show where time, re-entry and review accumulated.
- Ask what they already pay for, what their current tools fail to do, who approves purchases, and what evidence would justify switching. Avoid asking only whether they “like” an imagined AI product.
- Request or run comparable demonstrations of shortlisted products against the same defined tasks, with the same software versions, assumptions and required outputs.
- Record unresolved problems and buying commitments before selecting a product architecture or starting a large implementation.

Use the following benchmark scenarios as an evaluation design, with engineering acceptance criteria set by a qualified reviewer before testing:

| Scenario | What the demonstration must reveal | Evidence to retain |
| --- | --- | --- |
| Existing completed model | Correct object mapping, units, cases and combinations | Input manifest and extracted data comparison |
| One known member check | Transparent assumptions and supported code provisions | Independently checked reference calculation |
| Changed loads, same geometry | Whether prior reinforcement and reports are refreshed | Before/after forces, checks and report revisions |
| Changed member dimensions | Whether the tool updates the intended model and reruns analysis | Model differences and new analysis identifiers/results |
| Failed or unsupported case | Clear failure reporting without a false complete result | Warnings, skipped checks and recoverable state |
| Renamed objects or grouped members | Stable mapping and preservation of deliberate engineer choices | Change log and reviewed mapping |
| Alternative design comparison | Comparable objectives, constraints and complete costs | Feasible candidates, quantities and governing checks |
| Final office deliverable | Actual reviewer effort and drawing/report cleanup | Reviewed outputs and total elapsed engineering time |

Useful measurements are total engineer-plus-reviewer time, material discrepancies against reference results, successful task completion, manual corrections, onboarding effort, support incidents and total license/usage cost. “Clicks saved” or “AI generated the model” are insufficient on their own.

**Proceed with a purchase** when a product passes our real task and its ongoing cost is justified. **Proceed with a build** only when several target firms have a recurring unmet need, existing tools fail the same defined task, and potential customers will commit meaningful time or money to a pilot. **Narrow or stop the idea** if existing software already solves the problem economically, review effort cancels the savings, or every customer requires a different bespoke system.

## 14. Confidence and remaining gaps

The strongest evidence here is concrete official documentation: release histories, version matrices, manuals and public commercial terms. Product landing pages establish positioning but are weaker evidence of complete operation. Public repositories establish inspectable source availability, not validated engineering, permissive reuse or a support commitment.

Important unresolved items are current compatibility for several ETABS add-ons; exact bidirectional exchange and automatic reanalysis behaviour; Indian-code coverage by element, provision and edition; standalone RCDC pricing; regional procurement terms; independent product performance; customer adoption; willingness to pay; and the size of the reachable niche. Current RCDC entitlement in Advanced/WorkSuite is now documented, rather than left as an unknown.

Some source pages were indexed but not directly retrievable, and older product URLs redirected after branding changes. Newer release documents took precedence over older marketing where their meaning was clear. Conflicts that could not be resolved remain explicitly qualified. Price pages can change dynamically; they are purchase leads, not quotations.

The deeper review found seven specific evidence issues: CivilAI's service positioning was previously weighted like product proof; ConGro's agent and optimizer require separate evaluation, while build/pricing records disagree; StructPro has demonstrated model writes but uncertain availability/licensing; RCDC's historical direct link cannot establish a modern automatic round trip; ACE OCP has substantial historical evidence but unresolved modern compatibility/permanent pricing/client-project rights; SideKick's Indian order display differs from its dollar headline, while related design tools are separate products; and ETABS MATE has substantive detailing/check documentation but material defaults, edit resets and qualified licence rights. Each is reflected in its profile and cost comparison.

For StructPro, evidence includes the live website, seven complete tutorial transcripts and selected frames; not all fourteen lessons or every visual sequence were examined. No current installer or independent runtime/code validation was obtained. ConGro evidence includes public documentation, founder release disclosures, indexed founder activity and normal-HTTPS artifact headers. Certificate failures prevented browser demonstration review and latest-pointer revalidation; direct founder-profile retrieval was also unavailable. No access or certificate check was bypassed. For Bentley's Update Analysis demonstration, public metadata was accessible but the attachment required authentication. These limits distinguish document examination from runtime verification.

ACE OCP evidence includes the 2017 guide's text, the complete official presentation transcript, original research manuscripts, a sponsored review, academic records and live shop selections. PDF screenshot retrieval failed; a normal local manual download returned403. The Epoka full thesis and Isra full methods were unavailable. We did not bypass access or certificate checks, sign up or execute models. Historical research, sponsored demonstration, academic use, current compatibility and actual construction outcomes remain separate evidence categories.

SideKick's 2020 video was sampled at eight points; no complete transcript or full visual review was obtained. Its India order display was independently checked through visible UI and public response data, without customer details, payment or submission. No installer or activation was tested. The separate spColumn bridge's example archive returned HTTP 403 and was not examined. CSI/PROKON/StructurePoint documentation supports underlying concepts and engine boundaries, not validation of Excelcrib's implementation. Searches found no attributable independent SideKick case study or newer compatibility declaration; neither absence of users nor discontinuation is inferred.

The study focuses on products close to the proposed ETABS/Excel/RC workflow. It is not an exhaustive catalogue of every structural program or private in-house tool. Broader solver markets, undisclosed firm automation and emerging products can add competitors. No claim of market leadership, exclusive capability, guaranteed safety, minimum material cost or validated return on investment is made.

ETABS MATE sources include current document editions with older embedded examples. The Quick Start/manual metadata is June2026; release-note modification metadata is July2026. These are document timestamps, not authenticated software release dates. Selected source pages were visually inspected; complete product execution and independent code validation were not performed. Vendor-hosted project testimonials, outside comments and a training record were kept separate from engineering benchmarks. Licence language is a qualified translation, not a determination that ordinary consulting work is prohibited. The public evaluation was checked by headers only; purchaser-delivered updates, transfer prices and international terms remain unverified.

RCDC adds calculation/revision evidence, StructPro and SideKick add Excel-operation examples, ConGro adds beta automation and historical regression cases, ACE OCP adds documented candidate-analysis search, and ETABS MATE adds detailing/check and drawing evidence. None proves our complete proposed workflow in a current ETABS session. Research remains paused. VIS and the other remaining studies are recorded in the companion backlog; the immediate use of the evidence is to improve the product specification and preserve clear development gates.
