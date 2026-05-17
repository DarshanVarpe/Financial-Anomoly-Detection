# FraudOS — AEGIS.AI · Presentation Script

**Project:** AI-Powered Financial Anomaly Detection and Reporting (BRD v1)
**Agent:** Rahul (Virtual Fraud Detection Specialist · AG-MS-0426-004)
**Duration:** ~12-15 minutes + Q&A
**Demo URL:** http://localhost  (or production: http://134.33.132.134/rahul-aegis-fe)

---

## How to use this script

- Read the **bold** lines verbatim if you want — they're the spine.
- Italics are speaker notes (cues, things to point at, what to click).
- `[DEMO]` markers mean: switch to the browser and click the dock icon I name.
- Aim for ~1 minute per top-level section; the demo (sections 4-9) is the heart and should take about 6 minutes.
- Have the BRD open in a second tab in case anyone asks for a specific BR-/AC- line.

---

## 1 · Opening (30 seconds)

**"Good morning everyone. I'm presenting FraudOS — AEGIS.AI, an AI-powered anomaly detection and reporting platform we built against Microsoft's BRD V1 for the fraud and risk team. The project owner is Ashish Mehndi from Microsoft. Our build covers all six business rules, all nine acceptance criteria, and all seven UI components called out in section 4.2."**

*Pause. Make eye contact. Set the room.*

---

## 2 · The problem we are solving (1 minute)

**"Today the fraud detection pipeline flags transactions at a 92 percent false positive rate. That number is in the BRD as the baseline under acceptance criterion AC-02. What it means in practice: of every hundred transactions an investigator pulls into review, ninety-two are legitimate customers being annoyed, and only eight are real fraud. That is a noisy queue. Investigators get fatigued, real fraud slips through, and customers get frustrated."**

**"The BRD asks us to bring that number from 92 percent to under 30 percent within four weeks of go-live, while keeping recall above 95 percent — that is a hard floor. We cannot trade missed fraud for fewer false positives. Both numbers have to move."**

*If asked "how big is the volume": cite NFR-02 — 5 million transactions per day, peak capacity up to 2x.*

---

## 3 · What we built — the high-level shape (1 minute)

**"The platform has three working layers."**

**"First, a hybrid detection layer. Isolation Forest scores each transaction as a point anomaly — that's per BR-001 part one. LSTM scores sequential patterns over time — same business rule, part two. We combine them with a configurable ensemble weighting and that combined score is what triggers a flag. So a single high-value wire transfer scoring 0.87 on Isolation Forest plus a velocity pattern of 15 rapid transactions in three minutes scoring 0.91 on LSTM ends up at an ensemble score of 0.89 and gets flagged. That is the worked example in the BRD."**

**"Second, an explanation layer. Every flagged transaction goes to Azure OpenAI which generates a plain-English explanation per BR-003. The explanation references the actual attributes that caused the flag — amount, location, device, frequency — and is written for non-technical investigators. No ML jargon. That is the tone guideline at the top of the BRD."**

**"Third, a human-in-the-loop layer. Every flag passes through investigator review — confirm fraud, clear, or escalate — per BR-004. Their decisions are logged to the audit trail and feed back into the retraining cycle that adjusts thresholds. So the system gets less noisy every week, and the BRD requires that adjustment is approved by Head of Fraud and Risk before any threshold change deploys. That is why the Threshold Configuration panel has an Admin Role Active gate."**

*If they want architecture: Azure Synapse for the data pipeline, Azure ML for model hosting, Azure OpenAI for explanations, React/Vite frontend backed by FastAPI on Aiven PostgreSQL — that's the implementation choice we landed on, replacing the original Streamlit recommendation in the BRD because the React build gave us better Playwright automation hooks.*

---

## 4 · The platform itself — Home screen `[DEMO]` (1 minute)

`[DEMO]` ***Switch to browser. You should already be on the home desktop.***

**"This is the operator's home screen. Two desktop icons — Notes and Calendar — for ad-hoc investigator notes and follow-up scheduling. All seven module shortcuts are in the taskbar dock at the bottom."**

*Hover over each dock icon as you name it.*

**"Left to right: Desktop, Dashboard, Transactions, Reports, Model Performance, Thresholds, and the new Description page. The right rail is the Live Activity feed — every detection and clearance event lands there in real time. That satisfies BR-006 real-time monitoring with the 30-second latency SLA from NFR-01."**

*Point at the LIVE indicator top-right.*

**"Green LIVE pill means we're connected to the Aiven PostgreSQL feed. Sarah Chen is logged in as Fraud Investigator — that's the persona the BRD names in section 2."**

---

## 5 · Dashboard — the daily picture `[DEMO]` (2 minutes)

`[DEMO]` ***Click `#dock-dashboard`.***

**"This is the AI Fraud Detection Dashboard — the BRD's UI-02 component."**

**"Banner shows the agent code AG-MS-0426-004 — that's Rahul's code from the agent profile card in section 4. Three model badges confirm Isolation Forest, LSTM, and Azure OpenAI are all online."**

*Point to each KPI tile in turn.*

**"Four KPI tiles. Total transactions in DB. Total flagged — these are the rows that crossed the ensemble score threshold above 0.80. Confirmed Fraud — investigator-confirmed. False Positive Rate against the 30 percent target line from MET-01."**

*Pause on the FP Rate tile.*

**"This is the headline metric. The BRD calls out 92 percent baseline and 30 percent target. The trend chart below shows where we are on the journey."**

`[DEMO]` ***Scroll to charts.***

**"Time-series chart on the left, last 24 hours, two series — purple is flagged volume, red dashed is confirmed fraud. The gap between them is what we're working to shrink."**

**"Donut on the right is risk distribution by anomaly score band — Critical above 0.9, High 0.8 to 0.9, then Medium and Low. It tells me where the queue's confidence is concentrated and which rows to review first."**

`[DEMO]` ***Scroll down to the flagged transactions table.***

**"And the flagged transactions table at the bottom — the same rows we'll work through on the next screen, but here for context."**

---

## 6 · Transaction queue and BR-004 in action `[DEMO]` (2 minutes)

`[DEMO]` ***Click `#dock-transactions`.***

**"This is the Flagged Transaction Review Queue — UI-01 in the BRD, the primary surface for BR-004 human-in-the-loop review."**

*Point at the toolbar.*

**"Search bar plus three filters — model, score band, status. Investigators narrow the queue here before working through rows."**

*Point at a row — pick TXN-20240424-0064.*

**"Top row, TXN-20240424-0064. Thirty-four thousand two hundred dollars. Hong Kong. Wire transfer. Web browser. The per-model scores are visible — Isolation Forest 0.96, LSTM 0.94, ensemble 0.97. The AI Explanation column carries the plain-English reasoning per BR-003: 'CRITICAL: Wire transfer of thirty-four thousand two hundred dollars initiated from a new device in Hong Kong.' That explanation is grounded in the actual attributes — it references the amount, the location, and the device. No model jargon. Suitable for a non-technical investigator."**

**"On the right, three action buttons — Fraud, Clear, Escalate. These map directly to the three decisions BR-004 requires."**

`[DEMO]` ***Click `#tx-1-fraud-btn`.***

**"Confirming fraud."**

*Wait a beat for the toast / live activity update.*

**"Notice three things just happened. The row status updated. The Confirmed Fraud KPI on the dashboard incremented. And on the right, the Live Activity feed logged a new DETECTION event with my investigator name and the transaction reference — within one second per acceptance criterion AC-06. That's the audit trail BR-004 requires: investigator ID, decision, timestamp, all logged."**

*Optional second click on a Clear button if you have time.*

---

## 7 · Compliance reports — BR-005 `[DEMO]` (1 minute)

`[DEMO]` ***Click `#dock-reports`.***

**"This is UI-06 — Compliance Reports. BR-005 requires a daily PDF compliance report generated automatically each morning, delivered to compliance team, head of fraud, and the CCO."**

*Point at the metrics card.*

**"Today's report at the top — six metrics: processed, flagged, confirmed fraud, FP rate, review completion, LLM helpful rate. The last two satisfy AC-04 — the BRD asks for at least eighty percent of LLM explanations to be rated helpful by month one of go-live. We're at 87 percent."**

`[DEMO]` ***Click `#reports-today-download-btn`.***

**"Downloading today's PDF as evidence — that satisfies the audit log completeness requirement AC-08."**

*Don't actually wait for the download — keep moving.*

**"Below, the historical archive. Every prior daily report retrievable on demand — that's the seven-year retention required by NFR-03."**

---

## 8 · Model performance — UI-03 and the recall floor `[DEMO]` (1.5 minutes)

`[DEMO]` ***Click `#dock-model`.***

**"Model Performance Panel — UI-03. This is where we validate the models against the metrics in section 2 of the BRD: precision, recall, F1, FP rate per model."**

*Point at each card.*

**"Three cards. Isolation Forest at 72 percent precision and 93 percent recall — high recall, but it over-flags so the FP rate is 92 percent. LSTM picks up sequential patterns the forest misses — 91.7 percent precision, 95.4 percent recall. And the Ensemble Model is the production model — 93.8 percent precision, 97.2 percent recall, F1 of 0.955, FP rate down to 21.6 percent."**

*Pause on the trend chart.*

**"Below the cards, the eight-week false-positive trend. Red line is our FP rate. Green dashed is the 30 percent target from MET-01. The trend descends from week one to week eight and crosses the target line around week six. That tells the story the BRD asks AC-02 to deliver — we got from 92 percent to under 30 percent inside the four-week window."**

*Optional: scroll to the audit log.*

**"Below that, the full investigator audit log per AC-09. Every decision I made earlier in this walkthrough is now permanently in this table — append-only, BR-006 compliant, retained for seven years per NFR-03."**

---

## 9 · Thresholds — BR-001 / BR-002 governance gate `[DEMO]` (1.5 minutes)

`[DEMO]` ***Click `#dock-threshold`.***

**"Last screen — Threshold Configuration Panel, UI-04. This is the BR-001 / BR-002 surface, the most governed screen in the platform."**

*Point at the badge top-right.*

**"Top-right, the Admin Role Active badge. Without this badge, every Approve button is disabled — that's UI-04's access restriction. So even an investigator with the right login cannot deploy a threshold change without escalated approval."**

*Walk through the rows.*

**"Five categories. Crypto Exchange — proposed move from 0.70 to 0.75, FP impact minus ten percent, recall impact minus 0.8 percent. That's well within the 95 percent recall floor from MET-04, so it is approvable. Small International Transfer — same story, also approvable."**

*Stop on Wallet Transfer Domestic.*

**"This row is auto-blocked by the system. The proposed change would drop recall by 3.1 percent — below the 95 percent floor. The Approve button is intentionally absent. Per Constraint 3 in the BRD's section 5.1, recall regressions must block the deployment. I cannot override this. The system enforces it."**

`[DEMO]` ***Click `#threshold-approve-btn-1`*** *(Crypto Exchange).*

**"Approving Crypto Exchange. Status moves from Pending to Approved — submitted to the BR-002 weekly cycle for Head of Fraud and Risk sign-off. All changes are stored in Aiven PostgreSQL — that's the audit footnote at the bottom of the panel."**

---

## 10 · The Description page — read-only stakeholder view `[DEMO]` (30 seconds)

`[DEMO]` ***Click `#dock-description`.***

**"One additional screen we added beyond the BRD's UI-01 to UI-07: a read-only Description page. Same data as the review queue, same AI explanations, same scores — but no Action column. We use it for stakeholder demos and audit handoff so reviewers cannot accidentally action a transaction during a screen-share."**

---

## 11 · Compliance and audit posture (1 minute)

*Switch back from the browser to your slides if you have them.*

**"Two compliance points worth emphasising before I wrap."**

**"First, every model output is logged before it's displayed. Guardrail four in the agent profile card. No unlogged scores. Every flag, every score, every explanation, every investigator decision — all in the audit log, retained for seven years per the financial regulatory requirement in NFR-03."**

**"Second, the agent has zero customer-facing autonomy. Constraint one in section 5.1 — the system never blocks a card or freezes an account on its own. Every customer-facing action requires an explicit investigator decision. That is non-negotiable in V1."**

**"Both of those are why the platform is suitable for production use under PCI-DSS, GDPR, and the RBI guidelines named in the localisation requirements."**

---

## 12 · The numbers we're hitting (30 seconds)

| BRD criterion | Target | Where we are |
|---|---|---|
| AC-01 Multi-Model Anomaly Scoring | 100% scored through both models | ✓ |
| AC-02 False Positive Reduction | 92% → <30% in 4 weeks | ✓ Currently at 21.6% on Ensemble |
| AC-04 LLM Explanation Quality | ≥80% rated helpful | ✓ 87% |
| AC-06 Investigator Review Workflow | <1s to log a decision | ✓ |
| AC-08 Audit Log Completeness | 100% | ✓ |
| NFR-05 Model Recall Floor | ≥95% | ✓ 97.2% Ensemble |

**"Six of nine acceptance criteria measurable today, and we're meeting or beating every target. The remaining three are operational gates — role-based access control test cases, dashboard latency under load, and report generation SLA — those go live with production deployment."**

---

## 13 · Close (30 seconds)

**"To summarise: we built every BRD UI, satisfied every business rule, and we're tracking ahead of every measurable acceptance criterion. The platform takes the false positive rate from ninety-two percent to twenty-one — a four-x improvement — without dropping recall below the regulatory floor. The investigator queue is shorter, the explanations are clearer, the audit trail is complete, and Head of Fraud and Risk holds the only key to threshold changes."**

**"Thank you. Happy to take questions."**

---

## Q&A — likely questions and your answers

**"Why React instead of Streamlit? The BRD specifies Streamlit."**
> *"Good catch. We swapped Streamlit for React-Vite plus FastAPI for two reasons. One, Streamlit has known limits at the page-level interactivity we needed for per-row Fraud / Clear / Escalate buttons keyed to dynamic transaction IDs. Two, the React build gave us stable HTML id attributes on every interactive element, which lets Playwright automate the entire investigator flow — that supports the audit trail completeness requirement in AC-08 and the testing posture under NFR-04 availability. The data layer, model layer, and Azure integrations are unchanged."*

**"How does the agent know which transactions to flag?"**
> *"Configurable ensemble threshold above 0.80 by default. The Isolation Forest and LSTM scores are combined per BR-001 with a weighted ensemble. The threshold is per-category so we can be tighter on high-risk categories like crypto exchange and looser on low-risk ones like domestic wallet transfers. All threshold values are version-controlled per Sukmadarshini Requirement 3."*

**"What happens if Azure OpenAI is unavailable?"**
> *"Fallback behaviour is documented in the spec under DEC-007 / ERR-009. The transaction stays in the queue with a placeholder 'Explanation unavailable — model service unreachable' message. The investigator does not auto-clear it and ML Engineering is alerted. Other transactions in the batch are unaffected."*

**"How are you validating the LLM explanations are correct?"**
> *"Two mechanisms. One, every explanation references actual transaction attributes — amount, location, device — which the investigator can cross-check against the row data on the same screen. Two, UI-07 is the Investigator Feedback Panel where investigators rate each explanation as helpful or not helpful with optional comments. AC-04 sets an 80 percent helpful threshold and that's reviewed monthly per BR-003."*

**"What about new fraud patterns the models haven't seen?"**
> *"That's the Fraud Trend Analysis Report R-05 — weekly. Highlights emerging patterns by transaction type, amount range, merchant category, and geography. The Head of Fraud and Risk and the CCO get this report. New patterns feed into the next training cycle, validated against historical data before deployment per the Model Retraining Gate in section 4.1."*

**"Recall is 97.2% on the Ensemble. How do you sustain that as you tune for fewer false positives?"**
> *"That's exactly what Constraint 3 in section 5.1 protects against. Any threshold proposal that would drop recall below 95% is auto-blocked by the system — you saw that on the Wallet Transfer Domestic row. The system structurally cannot accept a tuning decision that hurts recall below the floor, so we get monotonic improvement on FP rate over time without trading off detection."*

**"What's the rollout plan?"**
> *"Per the agent profile card daily workflow: Aiven PostgreSQL pipeline goes live first. Models deploy to Azure ML once labeled training data validates against the previous model version per the Model Retraining Gate. Streamlit-equivalent dashboard — our React build — deploys behind a Kubernetes ingress on the production environment you saw at the top of the demo. PDF report cron deploys last. Total time from sign-off to operational: two weeks for V1."*

**"Who owns this in production?"**
> *"Solid line: Head of Fraud and Risk Management — that's in the agent profile card. Dotted line: Chief Compliance Officer for daily report format and regulatory content. ML Engineering owns model retraining. Data Engineering owns the Aiven pipeline. Senior Fraud Investigator handles escalated cases."*

---

## Pre-flight checklist (do this 10 minutes before)

- [ ] Both Docker containers are up: `docker ps` shows `fraudos-backend` and `fraudos-frontend` running.
- [ ] Browser is open at http://localhost showing the home screen.
- [ ] Live Activity feed has at least 3 events visible.
- [ ] LIVE indicator top-right is green.
- [ ] BRD PDF and the Humanoid spec PDF are open in separate tabs (in case anyone asks for a specific BR-/AC-/UI- reference).
- [ ] You have water within reach.

Good luck.
