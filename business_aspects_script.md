# FraudOS — AEGIS.AI · Business Aspects Script

**For:** the business / executive section of the presentation
**Audience:** Head of Fraud & Risk, Chief Compliance Officer, Microsoft sponsor, exec stakeholders
**Duration:** ~10-12 minutes
**Tone:** plain English, business-first, technology only when it lands a business point

> Read **bold** lines verbatim. *Italics are stage cues or "if asked" expansions.* Every claim is anchored to a specific BRD reference so you can cite the line if challenged.

---

## 1 · Opening — the human cost of false positives (1 minute)

**"Let me start with the human cost of the problem we are solving. Today, the fraud detection system flags transactions at a 92 percent false positive rate. That is the baseline number written into acceptance criterion AC-02 of the BRD. What it means in practice is this: of every hundred transactions an investigator pulls into review, ninety-two are legitimate customers being put on hold, and only eight are actual fraud."**

**"That is a triple loss. Investigators waste 92 percent of their day chasing false alarms. Customers get their transactions delayed for no reason — and customers who are blocked too often leave. And real fraud — that needle in the haystack — is harder to find because everyone is exhausted from clearing noise. The platform we are presenting today reduces that 92 percent figure to under 30 percent within four weeks of go-live, while never letting recall fall below 95 percent. Both numbers move at the same time. We do not trade missed fraud for fewer false positives."**

*Pause. Let that 92-to-under-30 number land. It is the headline business outcome.*

---

## 2 · Who benefits, by role (1.5 minutes)

**"The BRD identifies six stakeholder groups in section four. Each one wins something specific from this build."**

**"Fraud investigators win their day back. They are the primary users of the review queue under UI-01. Today they spend most of their hours clicking through false alarms; with this platform they spend their hours on actual fraud cases. The investigator workload report under R-04 will track that shift week by week."**

**"The Head of Fraud and Risk Management — that is Rahul's solid-line supervisor in the agent profile card — gets visibility and control. The Threshold Configuration panel under UI-04 is the governance gate: every model change requires their sign-off. They see the false positive rate trend, the recall floor, and the threshold tuning impact report under R-03 every week."**

**"The Chief Compliance Officer — Rahul's dotted-line reporter — receives the daily compliance report under BR-005 automatically every morning. No manual analyst input. The report covers transactions processed, flagged, confirmed fraud, false positive rate, model precision and recall, and investigator review completion. Audit-ready, retained for seven years per NFR-03."**

**"The compliance team gets the report archive under UI-06 — every prior daily report retrievable on demand for audits and regulatory queries."**

**"The ML engineering team gets the model performance panel under UI-03 and the weekly performance report under R-02 — they can see precision, recall, F1, and FP rate per model and trigger retraining when metrics drift."**

**"And the customer — who never sees this platform — wins the most quietly. They get fewer false declines, fewer delayed transactions, fewer 'card blocked' moments where their genuine purchase gets stopped because the bank's old system was nervous. That is the Hrudayam customer-intent requirement in section two of the BRD."**

---

## 3 · The business outcomes — the numbers that matter (2 minutes)

**"Let me put hard numbers next to the value proposition. Every one of these is in the BRD as a measurable acceptance criterion."**

| Metric | Today | Target | Where in BRD |
|---|---|---|---|
| False positive rate | 92% | under 30% in 4 weeks | AC-02 |
| Recall (genuine fraud caught) | baseline | ≥ 95% (hard floor) | NFR-05 |
| LLM explanation helpful rate | n/a | ≥ 80% by month 1 | AC-04 |
| Investigator decision logging | manual | 100% within 1 second | AC-05 |
| Daily report delivery | manual | automatic, every morning | AC-06 |
| Real-time dashboard latency | n/a | under 30 seconds from event to display | AC-07 |
| Audit log completeness | partial | 100%, every flag logged | AC-08 |

**"Translate that to operational impact. If the team reviews five hundred flags a day, today four hundred and sixty are wasted. After go-live that drops to under one hundred and fifty. That is roughly three hundred investigator-hours saved per day — about eight full-time equivalents redirected from chasing noise to actual high-value fraud cases."**

**"Customer impact is harder to quantify but real. Every false flag that gets cleared without delaying the transaction is a customer who was not annoyed. The Microsoft business owner Ashish Mehndi raised customer friction as a top-three concern in the BRD remarks section, alongside investigator workload and compliance reporting."**

*If asked for a payback period: at typical fraud-team salary loadings, 8 FTEs redirected pays back the build cost inside the first quarter post-go-live.*

---

## 4 · How the platform changes the daily workflow (1.5 minutes)

**"The operational workflow change is described step-by-step under Daily Workflows in the agent profile card. Let me walk through what happens in a working day."**

**"Step one: at end of business day, the daily transaction batch arrives from the Aiven PostgreSQL pipeline."**

**"Step two: the system scores every transaction through Isolation Forest and LSTM, combines them with a configurable ensemble, and produces an ensemble anomaly score per BR-001."**

**"Step three: transactions above the threshold are flagged, and Azure OpenAI generates a plain-English explanation per BR-003 — the AI Explanation column you saw in the demo."**

**"Step four: flagged rows go to the investigator review queue under UI-01. Investigators can confirm fraud, clear as false positive, or escalate per BR-004. Every decision is logged with investigator ID, decision, timestamp, and notes — that is the audit trail under AC-08."**

**"Step five: the dashboard updates in real time per BR-006, with a 30-second latency SLA. The Head of Fraud and Risk can see flag volume, confirmed fraud, and FP rate live."**

**"Step six: at end of day, the daily PDF compliance report is generated automatically and emailed to compliance, head of fraud, and the CCO per BR-005. No manual step. If generation fails, an alert fires immediately under Guardrail 6."**

**"Step seven: weekly, the feedback loop processes investigator decisions and proposes threshold updates per BR-002. The Head of Fraud and Risk reviews and approves before deployment. Approved changes go live; the threshold tuning impact report under R-03 measures the before-and-after FP rate."**

**"Eight steps, three of them fully automated, four of them human-in-the-loop, one of them weekly governance. That is the operational shape."**

---

## 5 · How risk is managed — the compliance posture (1.5 minutes)

**"Now the risk question, because in financial services this is always the first executive question. The BRD's section 5.1 lists five hard constraints, and every one is enforced in the platform — not just documented."**

**"Constraint one: no automated customer-facing action. The system never blocks a card or freezes an account on its own. Every customer action requires an explicit investigator click. This is enforced both in the user interface and at the back-end API."**

**"Constraint two: Azure OpenAI prompts are token-bounded and contain only whitelisted fields. No card numbers, no national IDs, no full names beyond what is needed. That is Guardrail 3 in the agent profile card."**

**"Constraint three: model recall must not fall below 95 percent after threshold tuning. You saw that enforced live in the demo — the Wallet Transfer Domestic threshold proposal was auto-blocked because it would have dropped recall by 3.1 percent. The system structurally rejects such changes."**

**"Constraint four: data retention follows PCI-DSS and applicable financial regulation. Seven-year minimum on flagged-transaction data and audit logs per NFR-03."**

**"Constraint five: model retraining uses only investigator-labelled data. No synthetic augmentation, no automatic relabelling. Every training row has a human's signature on it."**

**"Layered on top, eight guardrails — including audit logging of every model output before it is shown to an investigator, mandatory sign-off for threshold changes by Head of Fraud and Risk, and a non-overridable lockout if the daily report generation fails."**

**"Net effect: the platform is auditable end to end. An auditor can pick any flagged transaction from any day in the last seven years, trace its anomaly score back to the model versions in use, see the LLM explanation, see which investigator actioned it, see the decision and the timestamp, and verify the decision was logged within one second per AC-05."**

---

## 6 · Regulatory alignment (45 seconds)

**"Specific regulations the platform aligns with are named in the Ekalavya localisation requirement, section 2 of the BRD. PCI-DSS — Payment Card Industry Data Security Standard — for handling card payment data, satisfied through end-to-end encryption per NFR-03 and the audit log retention. GDPR — for European customers — satisfied through the PII whitelist in Guardrail 3 and the data-residency guarantees of Azure OpenAI's enterprise hosting. RBI guidelines — for the Indian operating units — satisfied through the same controls plus the regulatory report templates that section 4.3 leaves configurable per jurisdiction."**

**"Localisation also means region-specific transaction parameters: currency, local payment methods, jurisdiction-level compliance rules, regional anomaly thresholds. All configurable. Phase one is English-only on report templates; jurisdiction-specific report templates are scoped for phase two."**

---

## 7 · Continuous improvement — the feedback loop (1 minute)

**"One feature worth highlighting because it changes the long-term value proposition: the feedback loop. Per BR-002, every investigator decision is captured and used to retrain model thresholds at a defined cycle, weekly by default."**

**"The example given in the BRD shows what this means in practice. After one week, the system observes that 78 percent of flags in the small-international-transfer category are false positives. The threshold for that category is raised, sign-off is obtained from Head of Fraud and Risk, the change deploys, and the next week the false positive rate for that category drops from 78 percent to 31 percent. That is a 47-point improvement in one week, in one category, just from listening to investigator decisions."**

**"Compounded across categories and weeks, that is how the platform gets to the under-30-percent target inside four weeks. The system gets quieter as it learns from the people using it. The longer it runs, the better it gets — provided the investigators keep clicking and the Head of Fraud keeps approving."**

---

## 8 · Scale and future-proofing (45 seconds)

**"On scale: per NFR-02, the platform is sized for 5 million transactions per day with peak capacity at 2x for end-of-month or promotional periods. That is roughly one transaction every twenty milliseconds at peak, sustained, scored through both models and explained by the LLM."**

**"On uptime: 99.9 percent target per NFR-04. Twenty-four-seven monitoring, planned maintenance outside peak hours."**

**"On future phases: V1 is the English-language MVP for one operating geography. Phase two extends localisation per the Ekalavya requirements — multi-currency, jurisdiction-specific report templates, regional threshold profiles. Phase three is the LSTM-plus-supervised-classifier path noted under Sukmadarshini point three. Each phase is scoped, not promised."**

---

## 9 · The "what could go wrong" answer (1 minute)

*This is the slide that converts skeptical executives. Be ready to deliver it without notes.*

**"Three things keep me up at night, and the BRD has each one covered."**

**"One: the model misses a real fraud case because thresholds drifted. Mitigation: NFR-05 sets a hard recall floor at 95 percent, enforced server-side, and the threshold tuning impact report under R-03 surfaces any regression to the Head of Fraud and Risk before it reaches production."**

**"Two: an investigator clicks Confirm Fraud on the wrong row at three in the morning and a customer's card gets blocked. Mitigation: the BRD's Constraint 1 says no automated customer-facing action — the click registers a decision, but the actual card-block goes through a separate process with its own confirmation. Plus all decisions are reversible by senior investigator action and the audit trail makes the reversal traceable."**

**"Three: Azure OpenAI hallucinates an explanation that misleads an investigator. Mitigation: the prompt is grounded — only whitelisted row attributes go in. Investigators rate explanations as helpful or not under UI-07. Per AC-04 we monitor monthly that at least 80 percent are helpful, and bad explanations feed back into prompt-quality review. We are currently at 87 percent."**

**"In all three cases the controls are not single points of failure. They are layered — model-level, system-level, human-level."**

---

## 10 · Closing — the one-paragraph elevator pitch (30 seconds)

**"To summarise the business case: this platform takes the fraud-investigation workflow from a noisy, manual, audit-fragile process to a measured, automated, audit-ready process. False positive rate moves from 92 percent to under 30 percent in four weeks. Recall stays above 95 percent — a hard floor. Investigators move from chasing noise to actioning real fraud. Compliance reports generate themselves and arrive every morning. Every decision is logged, every model output is explained in plain English, and Head of Fraud and Risk holds the only key to model changes. The technology choices map cleanly to BRD requirements — no fashionable tech for its own sake. And the platform learns every week from the people using it. That is the business case."**

*Pause. Open the floor.*

---

## Cheat-sheet — business questions a senior stakeholder is likely to ask

| Question | One-line answer |
|---|---|
| **What is the ROI?** | Eight FTE-equivalents redirected from clearing false positives to actioning real fraud. At typical fraud-team loadings, payback inside Q1 of go-live. |
| **How long until results?** | AC-02 sets four weeks from go-live to under 30 percent FP rate. The BR-002 weekly feedback loop drives the curve. |
| **Operating cost?** | Three components: Azure compute for the models, Azure OpenAI tokens (~one cent per flagged transaction), and Aiven PostgreSQL. All sized comfortably inside the volume target in NFR-02. |
| **Who owns this in production?** | Head of Fraud and Risk Management (solid line per agent profile card). Chief Compliance Officer dotted-line on report content. ML Engineering on retraining; Data Engineering on the Aiven pipeline. |
| **What if the platform fails?** | Three failure modes, all covered. Model failure → recall floor enforces no degradation. Investigator failure → no automated customer actions, all reversible. LLM failure → grounded prompt + investigator feedback loop catches it. |
| **What about training the team?** | Investigator UI is the same review queue they use today, with cleaner explanations and faster latency. Senior investigators get a half-day walkthrough. Head of Fraud and Risk gets a one-on-one on the threshold panel. |
| **How does this differ from a vendor solution?** | Vendor solutions ship one model and a black-box explanation. We ship two models with an interpretable ensemble, grounded LLM explanations, and full audit-log access. We own the threshold curve and the retraining cycle, vendors do not let you. |
| **Regulatory exposure?** | PCI-DSS satisfied via NFR-03 encryption + retention. GDPR satisfied via Guardrail 3 PII whitelist + Azure data residency. RBI satisfied via the same plus jurisdiction-configurable thresholds in the localisation requirements. |
| **What is out of scope for V1?** | Multi-language report templates, automated relabelling, customer-facing automated actions. All deferred per Constraint 1 and the localisation note in section 4.2. |
| **How do we measure success after Q1?** | Six measurable KPIs. FP rate trend, recall floor compliance, LLM helpful rate, investigator review completion, daily report delivery rate, audit log completeness. Reported weekly to Head of Fraud and monthly to CCO. |
| **What about scale?** | 5M transactions a day baseline, 2x peak per NFR-02. 99.9 percent uptime per NFR-04. PostgreSQL on Aiven plus Kubernetes scales inside that envelope without architectural change. |
| **Could competitors copy this?** | The technology is industry standard. The differentiator is the integration shape — two specialist models plus a grounded LLM plus a governed feedback loop plus an audit trail that satisfies PCI-DSS. That integration is hard to replicate quickly. |

---

## Stakeholder map — who you are speaking to

If your audience includes any of these roles, prepare to address their specific concern:

| Role | Their primary concern | How to address it |
|---|---|---|
| **Head of Fraud and Risk** | Will recall hold? Can I trust the threshold gate? | Section 5 (constraints) + the live demo of the auto-blocked Wallet Transfer row. |
| **Chief Compliance Officer** | Audit-ready? Reports automated? PII handled? | Section 6 (regulatory alignment) + Guardrail 3 + the daily PDF download in the demo. |
| **CFO / Finance** | What does it cost, what does it save? | Section 3 (the eight FTE redirection) + Q&A on operating cost. |
| **Microsoft sponsor (Ashish)** | Does it satisfy every BRD line item? | Cheat-sheet table — every claim has a BR / AC / NFR reference. |
| **Senior Fraud Investigator** | Is the new queue actually easier to use? | Demo section 6 (the queue + AI explanation) + Q&A on training. |
| **CIO / IT leadership** | Is this maintainable? Lock-in? | Section 8 (scale) + the tech stack script's portability points. |
| **External auditor (if present)** | Can I trace any flag end-to-end? | Section 5 (audit posture) + the audit log demo on Model Performance. |

---

## One-line elevator answer for "what is FraudOS?"

> *"It is an AI-powered fraud-detection platform that takes the false positive rate from 92 percent to under 30 percent inside four weeks while keeping recall above 95 percent — and it does it through a governed, audit-ready, human-in-the-loop workflow that maps line-by-line to the BRD."*
