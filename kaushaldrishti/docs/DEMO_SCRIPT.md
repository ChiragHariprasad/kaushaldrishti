# KaushalDrishti — 3-Minute Live Judging Demo Script

**Ministry of Skill Development & Entrepreneurship (MSDE)**  
**Smart India Hackathon 2026 | Problem Statement SIH26246**

---

### **Overview of the Presentation**
- **Target Duration:** 3 minutes sharp.
- **Presenter Role:** Demonstrating the live system through the **Golden Path**.
- **Core Message:** *"KaushalDrishti is not a mock dashboard with random charts. It is an auditable, deterministic LMIS built on closed-form Kalman information fusion, Beta-posterior supply models, conformal prediction intervals, and honest labelling."*

---

### **0:00 – 0:30 | The Hook & Core Philosophy**

> **[Show Screen 1: National Overview]**
>
> "Good morning, respected judges. In skill planning across 144 pilot districts in Karnataka, Tamil Nadu, and Uttar Pradesh, ministries face a fundamental challenge: vacancy data from job portals is noisy, private portals over-represent white-collar jobs, and training programs take 12 months to graduate.
>
> To solve this for MSDE, we built **KaushalDrishti** on three non-negotiable principles:
> 1. **Honesty over polish:** Notice the amber badge in the header and on every data card — every single metric carries an immutable `data_mode` label (`live`, `public_aggregate`, `partner`, or `synthetic`). We never disguise synthetic data as live APIs.
> 2. **Zero LLMs in the runtime inference path:** All calculations are closed-form mathematics and deterministic state machines with sub-10ms latency.
> 3. **No placement data cheating:** Placement statistics are structurally excluded from supply equations because employed workers are not available supply."

---

### **0:30 – 1:10 | Golden Path Navigation (National → District → Trade)**

> **[Click Step 2: Karnataka → Step 3: Bengaluru Urban]**
>
> "Let’s follow our **Golden Path evaluation flow**, accessible directly via this top guide banner in $\le 3$ clicks per level.
>
> We start at the National Overview, click into **Karnataka**, and select **Bengaluru Urban** (LGD: 556). 
> 
> Filtering by the **Automotive sector**, we identify our primary critical bottleneck: **EV Service Technician** (QP: `ASC/Q1402`, NCO: `7231.0101`). Notice the tag `verified: false` — per government standards, indicative taxonomy mappings are never falsified as official."

---

### **1:10 – 1:55 | Forecast Centre & "Why" Exact Attribution**

> **[Show Screen 3: Forecast Centre → Click "Explain Why"]**
>
> "In the Forecast Centre, our Labour Demand Index (LDI) is **72.4**, indicating an **Acute Shortage**. 
>
> Look at the forecast trajectory: our Min-Pinball Ensemble forecasts **198 vacancies/month** against a certified institutional supply of **162 graduates**, yielding a net deficit of **+36** ($p_S = 84\%$, Severity = 40.0). Notice the shaded bands: these are **split-conformal prediction intervals** guaranteeing 80% coverage.
>
> Now, if an officer asks *'Why is there a shortage?'*, we don't give a black-box answer. Clicking **Explain Why** opens our exact attribution breakdown:
> - NCS Portal contributed **42.1%** of the fused information weight.
> - Karnataka Kaushalkar contributed **31.8%**.
> - Apprenticeship Portal contributed **17.5%**.
>
> We also display the 6 driver descriptors ($V, G, R, P, B, I$) and deterministic multilingual explanations in **English, Hindi, Kannada, and Tamil**."

---

### **1:55 – 2:35 | Policy Scenario Lab (+15% Seats & Stock-Flow Lags)**

> **[Click "Test in Policy Scenario Lab" → Screen 5]**
>
> "Now comes policy action. A District Skill Development Officer wants to know: *'If we increase ITI seats by 15%, will the shortage disappear?'*
>
> In typical tools, supply jumps immediately. But in the real world, training takes time! In our **Policy Scenario Lab**, we model strict **stock-flow delay dynamics**:
> - EV Technician training requires an **$L = 12$-month cohort duration**.
> - Therefore, for Months 1 through 11, supply stays completely flat because existing cohorts are already locked in!
> - At Month 12, the first expanded cohort graduates, cutting the deficit by 50%.
> - At Month 18, with our new centre coming online after a 6-month build lag, the banner updates: **'GAP CLOSES IN CYCLE: Cycle 2 (Month 18)'**, achieving a balanced market."

---

### **2:35 – 3:00 | Auditable Proofs, Backtests & 1-Click Export**

> **[Show Screen 6: Methodology & Validation → Click "Print District Brief" → Click "Export CSV"]**
>
> "Finally, how do you know the model works?
>
> In our **Methodology & Validation Centre**, we present the results of **31,680 rolling-origin backtests** across our 48-month panel:
> - At 6-month horizon: Empirical 80% coverage is **81.7%** (within $\pm 5\%$ of target).
> - Across 30 planted ground-truth shock episodes in `planted.json`, our state machine achieved **100% detection recall** with an average lead time of **1.2 months**.
>
> For officers on the ground, clicking **Print District Brief** generates a 1-page executive summary ready for District Skill Committee meetings, and clicking **Export CSV** downloads the entire auditable dataset in seconds.
>
> KaushalDrishti delivers actionable, transparent, and honest intelligence for India's skilling mission. Thank you!"
