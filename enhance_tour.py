"""Enhance the FraudOS tour JSON with richer narration drawn from the humanoid
spec PDF, while leaving every other field byte-identical.

Allowed mutations per step:
    description
    speak.before
    speak.after

Forbidden mutations:
    id, action, selector, highlight, pause, speak.during, top-level title,
    top-level description, meta block.

After writing, the script diffs structural vs enhanced and prints any
violation it finds.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "fraudos_tour_structural.json"
DST = ROOT / "fraudos_tour.json"

# ---------------------------------------------------------------------------
# Per-step enhancements drawn from Fraud_OS_Virtual_Humanoid_User_flow.md
# Sections 8 (detailed examples), 9 (happy-flow matrix), 10 (visual inventory),
# 11 (home page detail), 12 (dashboard detail), 17 (narration patterns).
# ---------------------------------------------------------------------------

ENHANCED = {
    "intro": {
        "description": "Opening line with no UI action — sets the stage as Agent Rahul, the virtual humanoid for the FraudOS — AEGIS.AI fraud detection platform.",
        "speak": {
            "before": "Hello, I am Rahul, the virtual humanoid for the FraudOS — AEGIS.AI fraud detection platform. Today I will walk you through how I review flagged transactions, validate model performance, and submit threshold approvals — the full Fraud Investigation Happy Flow as specified in the Business Requirements Document version one MVP release two.",
        },
    },
    "home-live-activity": {
        "description": "Frame the right-rail Live Activity feed on SCR-001-HOME (#commentaryFeed) — the real-time DETECTION and CLEARED event stream that satisfies BR-006.",
        "speak": {
            "before": "We start on the FraudOS home screen. The desktop carries only two utility icons — Notes and Calendar — and module navigation is performed via the taskbar dock at the bottom. On the right rail is the Live Activity feed, which streams every detection and clearance event as they happen.",
            "after": "Per BR-006 real-time monitoring, every fraud event lands here within one second of the action — DETECTION entries when fraud is confirmed, CLEARED entries when a flagged transaction is dismissed as a false positive, all timestamped and tied to the investigator who made the call.",
        },
    },
    "open-dashboard": {
        "description": "Open the AI Fraud Detection Dashboard (SCR-002-DASHBOARD) by clicking #dock-dashboard in the taskbar dock.",
        "speak": {
            "before": "I will now open the Dashboard. The desktop in this build only carries Notes and Calendar; everything else has moved to the taskbar dock at the bottom of the viewport, so I am clicking the Dashboard icon there.",
            "after": "The AI Fraud Detection Dashboard is now open. I can see the agent code AG-MS-0426-004, the model badges for Isolation Forest, LSTM, and Azure OpenAI, and the four KPI tiles for transactions, flagged, confirmed fraud, and false positive rate.",
        },
    },
    "dashboard-banner": {
        "description": "Read the dashboard hero banner (#dashboard-hero-banner) to confirm screen, agent code AG-MS-0426-004, and the three model badges.",
        "speak": {
            "before": "First, the banner up top. This confirms we are on the right screen and shows the agent code along with the active model badges.",
            "after": "Title reads 'AI Fraud Detection Dashboard', agent code AG-MS-0426-004 is visible top-right, and all three model badges are present — Isolation Forest, LSTM, and Azure OpenAI. The data feed is live from Aiven PostgreSQL.",
        },
    },
    "kpi-grid": {
        "description": "Frame the four-tile KPI row (#dashboard-kpi-grid) — the headline metrics for today's fraud activity.",
        "speak": {
            "before": "Below the banner, four KPI tiles. Each one summarises a different angle on today's fraud activity, and per the spec I read all four before interpreting any chart or taking any action."
        },
    },
    "kpi-total": {
        "description": "Read the Total Transactions in DB tile (#dashboard-kpi-total) — live count from Aiven PostgreSQL.",
        "speak": {
            "before": "First tile, total transactions in the database.",
            "after": "Live count from Aiven PostgreSQL — this confirms the data pipeline is healthy and we are looking at today's volume.",
        },
    },
    "kpi-flagged": {
        "description": "Read the Total Flagged tile (#dashboard-kpi-flagged) — transactions where the ensemble model scored above 0.80 per UI-02.",
        "speak": {
            "before": "Second tile, total flagged transactions.",
            "after": "These are everything the ensemble model scored above 0.80 — the threshold defined in UI-02 — and which therefore needs investigator review under BR-004 human-in-the-loop.",
        },
    },
    "kpi-fraud": {
        "description": "Read the Confirmed Fraud tile (#dashboard-kpi-fraud) — investigator-confirmed cases per BR-004.",
        "speak": {
            "before": "Third tile, confirmed fraud.",
            "after": "These are cases an investigator has personally confirmed as fraud through BR-004 review. Each one is recorded in the audit log with a timestamp, score, and decision.",
        },
    },
    "kpi-fprate": {
        "description": "Read the False Positive Rate tile (#dashboard-kpi-fprate) and compare to Target <30% per MET-01.",
        "speak": {
            "before": "Fourth tile, false positive rate.",
            "after": "Target sits at below thirty percent per MET-01. If we are above that line, the ensemble is over-flagging legitimate transactions and we will need to consider threshold adjustments on the Threshold Configuration panel.",
        },
    },
    "dashboard-timeseries": {
        "description": "Frame the Flagged Transactions Over Time line chart (#dashboard-timeseries-chart) — last 24 hours, two series.",
        "speak": {
            "before": "Below the tiles, the Flagged Transactions Over Time chart for the last twenty-four hours, refreshed live.",
            "after": "Purple line is total flagged, red dashed line is confirmed fraud. The gap between them is the false-positive volume — that is the surface we are working to shrink.",
        },
    },
    "dashboard-riskdist": {
        "description": "Frame the Risk Distribution donut (#dashboard-riskdist-chart) by anomaly score band.",
        "speak": {
            "before": "Beside the chart, the Risk Distribution donut, broken down by anomaly score band.",
            "after": "Critical band is greater than 0.9, High is 0.8 to 0.9, then Medium and Low. The dominant band tells me where the queue's confidence is concentrated and which cases I should review first.",
        },
    },
    "dashboard-table": {
        "description": "Frame the flagged transactions table (#dashboard-tx-table) — full row inventory with model scores and status.",
        "speak": {
            "before": "Below the charts, the flagged transactions table — the same eight rows we will work through on the review queue, but read-only here for context.",
            "after": "Each row shows TX ID, amount, location, the per-model scores including the ensemble score, and the current investigator status. TXN-20240424-0064 stands out at thirty-four thousand two hundred dollars from Hong Kong with an ensemble score of 0.97 — that is our top-priority review.",
        },
    },
    "open-transactions": {
        "description": "Open the Flagged Transaction Review Queue (SCR-003-TX-QUEUE) by clicking #dock-transactions — the BR-004 human-in-the-loop review surface (UI-01).",
        "speak": {
            "before": "Now let us move to the detailed review queue, where I act on each transaction one by one. Clicking the Transactions icon in the taskbar dock per UI-01 / BR-004.",
            "after": "The Flagged Transaction Review Queue is open. This is the BR-004 surface where I confirm or clear each flagged transaction, with the AI explanation alongside per UI-05.",
        },
    },
    "transactions-toolbar": {
        "description": "Frame the queue toolbar (#transactions-toolbar) — search input plus three filter dropdowns for narrowing the work surface.",
        "speak": {
            "before": "Up top, the toolbar — search by ID, location, or amount, plus three filter dropdowns for model, score band, and status.",
            "after": "I narrow the queue here before working through the rows. For example, filtering to only Ensemble-scored transactions surfaces the highest-confidence detections first.",
        },
    },
    "transactions-status-filter": {
        "description": "Open the status filter dropdown (#transactions-status-select) to focus on the unreviewed subset of the queue.",
        "speak": {
            "before": "Filtering by status to focus on what is still unreviewed — this is how I make sure no flagged transaction is missed before end of day.",
        },
    },
    "transactions-table": {
        "description": "Frame the queue table (#transactions-table) — TX ID, amount, location, merchant, device, model, IF Score, LSTM Score, Ensemble, AI Explanation, Status, Actions.",
        "speak": {
            "before": "Each row carries the full context I need: TX ID, amount, location, merchant, device, the per-model scores from Isolation Forest, LSTM and the ensemble, the plain-English AI explanation per BR-003 / UI-05, and the current status.",
            "after": "On the right of each row are three action buttons — Fraud, Clear, and Escalate. I read the AI explanation before clicking any of them, every time.",
        },
    },
    "transaction-fraud-action": {
        "description": "Confirm fraud on the highest-confidence row by clicking #tx-1-fraud-btn after reading the AI explanation. Records a DETECTION event in the Live Activity feed within one second per AC-06 and increments the Confirmed Fraud KPI tile.",
        "speak": {
            "before": "Top row — TXN-20240424-0064. The AI explanation says this is a critical-risk wire transfer of thirty-four thousand two hundred dollars initiated from a new device in Hong Kong. The ensemble score is 0.97, the highest confidence band. I will confirm this as fraud per BR-004 human-in-the-loop review.",
            "after": "Fraud confirmed. The row status has updated, the Live Activity panel on the right has logged a new DETECTION event within one second per AC-06, the Confirmed Fraud KPI tile has incremented by one, and the action is recorded in the audit log on the Model Performance panel per AC-09.",
        },
    },
    "transaction-clear-action": {
        "description": "Clear a borderline row as a false positive by clicking #tx-2-clear-btn after reading the AI explanation. The decision is recorded in the audit log (AC-09) and feeds back into the retraining pipeline as a negative example per BR-004.",
        "speak": {
            "before": "Next row — TXN-20240424-0091. This is an eight thousand four hundred dollar purchase at an electronics store in Lagos, Nigeria. The amount is six times the customer's usual spend and the device is unfamiliar, but investigator context confirms the customer was travelling and authorised this purchase. I will clear this as a false positive.",
            "after": "Cleared. The row status reads Cleared, Live Activity has logged a CLEARED event, and the decision is recorded in the audit log per AC-09. This feeds back into the retraining pipeline as a negative example per BR-004 and contributes to the false positive rate visible on the dashboard.",
        },
    },
    "open-description": {
        "description": "Open the read-only Transaction Description page (SCR-007-DESCRIPTION) by clicking #dock-description. Same data as the queue without the Actions column — for stakeholder demos and audit handoff.",
        "speak": {
            "before": "Next, the Description page from the taskbar. This view shows the same flagged transactions as the queue but without any action buttons, so we can review the inventory in stakeholder demos and audit walkthroughs without any risk of an accidental Fraud or Clear click.",
            "after": "The Description page is open. Same eleven columns as the review queue — TX ID through Status — but the Actions column has been intentionally omitted. The shared TransactionRow component renders without action buttons when showActions is false.",
        },
    },
    "description-table": {
        "description": "Frame the read-only #description-table — eleven-column read-only mirror of the review queue with no Actions column.",
        "speak": {
            "before": "All flagged transactions in inspection mode — same data, same scores, same AI explanations as the queue.",
            "after": "No Fraud, Clear, or Escalate buttons by design. This is the surface we share when screen-recording compliance demos or handing the inventory to auditors who should not have action capability.",
        },
    },
    "open-reports": {
        "description": "Open Compliance Reports (SCR-004-REPORTS) by clicking #dock-reports — the daily report and historical archive satisfying UI-06 / BR-005 / R-01.",
        "speak": {
            "before": "Next, Compliance Reports — the daily compliance evidence delivered to Compliance, Head of Fraud and Risk, and the CCO. Clicking Reports in the taskbar dock per UI-06 / BR-005.",
            "after": "Compliance Reports is open. Today's report up top, historical archive below.",
        },
    },
    "reports-today": {
        "description": "Frame today's Daily Compliance Report card (#reports-today-card) with the six headline metrics: processed, flagged, confirmed fraud, FP rate, review completion, LLM helpful rate.",
        "speak": {
            "before": "Today's compliance report — six metrics in one card. Processed, Flagged, Confirmed Fraud, FP Rate, Review Completion, and LLM Helpful Rate.",
            "after": "Auto-generated and delivered to the Compliance Team, Head of Fraud and Risk, and the CCO per BR-005. Review Completion at ninety-four-point-two percent and LLM Helpful Rate at eighty-seven percent are both well above target.",
        },
    },
    "reports-download-today": {
        "description": "Click #reports-today-download-btn to download today's compliance PDF per BR-005 / R-01. Captured as evidence per AC-09.",
        "speak": {
            "before": "Downloading today's compliance report PDF per BR-005. This goes into the evidence archive per AC-09 audit log completeness.",
            "after": "PDF downloaded. Saved as today's compliance evidence and timestamped against this session.",
        },
    },
    "reports-archive": {
        "description": "Frame the Report Archive table (#reports-archive-table) — every prior daily report with date, transactions, flagged, fraud, FP rate, F1 score, and download.",
        "speak": {
            "before": "Below today, the historical archive — every prior daily report. Date, transaction volume, flagged count, fraud count, FP rate, F1 score, and a download button per row.",
            "after": "Each row's download button is keyed to its date — for example, hash reports-archive-download-btn-2026-04-29. I can re-download any day's report on demand if compliance asks for it.",
        },
    },
    "open-model": {
        "description": "Open the Model Performance Panel (SCR-005-MODEL-PERF) by clicking #dock-model — three model cards, weekly FP trend, and the BR-006-compliant audit log per UI-03 / R-02.",
        "speak": {
            "before": "Next, Model Performance — where I validate the detection models against MET-01 to MET-06. Clicking Model Perf in the taskbar dock per UI-03 / R-02.",
            "after": "Model Performance Panel is open. Three model cards across the top, the weekly false-positive trend chart in the middle, and the full investigator audit log at the bottom.",
        },
    },
    "model-cards": {
        "description": "Frame the three model cards (#model-perf-grid) — Isolation Forest, LSTM Network, and Ensemble Model — each showing Precision, Recall, F1 Score, and FP Rate.",
        "speak": {
            "before": "Three model cards, side by side. Isolation Forest for point-anomaly detection, LSTM Network for sequential patterns, and the Ensemble Model that combines them.",
            "after": "Each card shows Precision, Recall, F1 Score, and FP Rate. I read all three before discussing performance because the production decision uses the ensemble, but understanding each component model tells us why the ensemble behaves the way it does.",
        },
    },
    "model-card-ensemble": {
        "description": "Spotlight the Ensemble Model card (#model-perf-card-ensemble) — the production decision model, leading on F1 and FP rate.",
        "speak": {
            "before": "The Ensemble Model is the production decision model — it combines the Isolation Forest and LSTM signals into a single ensemble score above 0.80 that triggers a flag.",
            "after": "Ensemble shows ninety-three-point-eight percent precision, ninety-seven-point-two percent recall, F1 score 0.955, and FP rate twenty-one-point-six percent. Best F1 and lowest FP rate of the three — meeting all the targets in NFR-05.",
        },
    },
    "model-fp-trend": {
        "description": "Frame the False Positive Rate Trend Weekly chart (#model-fp-chart) — eight weeks of ensemble FP rate against the 30% target line per MET-01.",
        "speak": {
            "before": "Below the cards, the weekly false-positive trend — eight weeks of ensemble FP rate plotted against the thirty percent target line from MET-01.",
            "after": "The red line descends from around eighty-five percent at week one toward roughly twenty-two percent at week eight, crossing the green target line around week six. The trajectory is right — threshold tuning over the past two months is paying off.",
        },
    },
    "model-audit-log": {
        "description": "Frame the Audit Log table (#model-audit-table) — append-only record of every investigator decision per AC-09 / BR-006.",
        "speak": {
            "before": "At the bottom, the Audit Log — every investigator decision recorded with TX reference, action, score, timestamp, and notes per AC-09.",
            "after": "Append-only and BR-006 compliant. For example, TXN-20240424-0064 FRAUD at 0.97 timestamped twelve thirty-two twenty-four; TXN-20240424-0079 CLEARED at 0.85 timestamped twelve thirty-three thirteen. Every action I took on the queue earlier in this walkthrough is now permanently recorded here.",
        },
    },
    "open-thresholds": {
        "description": "Open the Threshold Configuration Panel (SCR-006-THRESHOLDS) by clicking #dock-threshold — restricted submission interface satisfying UI-04 / BR-001 / BR-002.",
        "speak": {
            "before": "Last screen — Threshold Configuration. This is where I submit threshold change proposals for the Head of Fraud and Risk to sign off, per UI-04 / BR-001 / BR-002.",
            "after": "Threshold Configuration Panel is open. Five threshold categories, each with a current and proposed value plus the FP and recall impact.",
        },
    },
    "threshold-admin-badge": {
        "description": "Validate the Admin Role Active badge (#threshold-admin-badge) before any approval click — required by UI-04 access restrictions.",
        "speak": {
            "before": "Before clicking any Approve button, I must verify the Admin Role Active badge in the top-right of the panel. UI-04 requires this badge for any threshold submission.",
            "after": "Admin Role is active. If this badge were absent, every Approve button would be disabled and decision DEC-004 would have me stop and report the role limitation rather than retry.",
        },
    },
    "threshold-table": {
        "description": "Frame the threshold table (#threshold-table) — five categories with current, proposed, FP impact, recall impact, status, and action.",
        "speak": {
            "before": "Five categories: Crypto Exchange, E-commerce High Value, High-Value Card Present, Small International Transfer, and Wallet Transfer Domestic.",
            "after": "For each row, I read Current, Proposed, FP Impact, Recall Impact, and Status before deciding whether to approve. Per Constraint 3, any proposal that would push recall below ninety-five percent is automatically blocked by the system — I never override that.",
        },
    },
    "threshold-approve-action": {
        "description": "Approve a pending threshold whose recall impact stays within tolerance, by clicking #threshold-approve-btn-1 — submits the change to the BR-002 weekly cycle.",
        "speak": {
            "before": "First pending row — Crypto Exchange. Proposed change is 0.70 to 0.75. FP impact is minus ten percent — a real win on false positives — and recall impact is minus zero-point-eight percent, well within the ninety-five percent recall floor per MET-04. Safe to approve.",
            "during": "FP impact down ten percent, recall impact under one percent.",
            "after": "Approved. Status has changed from Pending to Approved and the change has been submitted to the Head of Fraud and Risk via the BR-002 weekly approval cycle. All changes are stored in Aiven PostgreSQL.",
        },
    },
    "threshold-blocked-row": {
        "description": "Spotlight an auto-blocked row (#threshold-row-5) — Wallet Transfer Domestic — whose recall impact breaches the 95% floor (Constraint 3). Validate-only, do not click.",
        "speak": {
            "before": "Last row — Wallet Transfer Domestic. The system has automatically blocked this proposal.",
            "after": "Recall impact would be minus three-point-one percent, dropping recall below the ninety-five percent floor defined in MET-04 and Constraint 3. The Approve button is intentionally absent and the Action cell shows 'Recall risk — blocked'. Per decision DEC-003, I do not attempt to override this — the auto-block is correct system behaviour.",
        },
    },
    "threshold-rules-note": {
        "description": "Read the rules footnote (#threshold-rules-note) at the bottom of the panel — every change needs Head of Fraud & Risk sign-off; sub-95% recall proposals are auto-blocked; all changes stored in Aiven PostgreSQL.",
        "speak": {
            "before": "And the rules footnote at the bottom of the panel makes the policy explicit.",
            "after": "Every change requires Head of Fraud and Risk sign-off. Any proposal reducing recall below ninety-five percent is automatically blocked. Every change — approved, pending, or blocked — is stored in Aiven PostgreSQL for audit.",
        },
    },
    "return-home": {
        "description": "Return to the home desktop by clicking #dock-desktop — completes the canonical SCR-001 → SCR-002 → SCR-003 → SCR-004 → SCR-005 → SCR-006 happy flow and surfaces the Notes / Calendar utilities.",
        "speak": {
            "before": "Coming back to the home desktop to close the tour.",
            "after": "Home desktop is back. The Notes and Calendar icons are the two utility modals available to investigators for ad-hoc notes and case follow-up dates.",
        },
    },
    "desktop-notes-icon": {
        "description": "Open the Notes modal (#notes-modal) with a single click on #desktop-notes-icon — investigation notes persisted to localStorage key fraudos-notes.",
        "speak": {
            "before": "A single click on the Notes icon opens the Notes modal — used for ad-hoc investigation notes that persist across sessions in the browser's localStorage.",
            "after": "Notes modal is open. I can record an investigation note here so the rationale for a decision is preserved alongside the audit log.",
        },
    },
    "notes-close": {
        "description": "Close the Notes modal by clicking #notes-close-btn.",
        "speak": {
            "before": "Closing the Notes modal."
        },
    },
    "desktop-calendar-icon": {
        "description": "Open the Calendar modal (#calendar-modal) with a single click on #desktop-calendar-icon — case follow-up scheduling persisted to localStorage key fraudos-cal-events.",
        "speak": {
            "before": "And the Calendar — same single-click pattern. Used for case follow-up dates and scheduled reviews.",
            "after": "Calendar is open on the current month. Each day has its own id like calendar-day-2026-04-29, and events are persisted to localStorage so they survive a refresh.",
        },
    },
    "calendar-close": {
        "description": "Close the Calendar modal by clicking #calendar-close-btn.",
        "speak": {
            "before": "Closing the Calendar modal."
        },
    },
    "outro": {
        "description": "Closing summary with no UI action — recap of the seven screens covered and the recommended next-action.",
        "speak": {
            "before": "That is the full Fraud Investigation Happy Flow as defined in the BRD. We covered the home desktop, the dashboard with its KPI tiles and charts, the review queue where I confirmed fraud and cleared two false positives, the read-only Description page, the Compliance Reports, Model Performance with the audit log, and the Threshold Configuration panel where I submitted approvals and validated the auto-blocked recall risk. Recommended next step is to monitor the false positive rate over the next twenty-four hours after the approved threshold changes take effect through the BR-002 weekly cycle. If the rate drops below thirty percent, MET-01 target is met. Anything you would like me to dig into?",
        },
    },
}

# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

with SRC.open(encoding="utf-8") as fp:
    tour = json.load(fp)

ALLOWED_FIELDS = {"description", "speak.before", "speak.after"}

original_steps = {s["id"]: json.loads(json.dumps(s)) for s in tour["steps"]}

for step in tour["steps"]:
    sid = step["id"]
    if sid not in ENHANCED:
        print(f"  WARNING - no enhancement defined for step '{sid}'")
        continue
    enh = ENHANCED[sid]
    if "description" in enh:
        step["description"] = enh["description"]
    if "speak" in enh:
        if "speak" not in step:
            step["speak"] = {}
        for key in ("before", "after"):
            if key in enh["speak"]:
                step["speak"][key] = enh["speak"][key]

with DST.open("w", encoding="utf-8") as fp:
    json.dump(tour, fp, indent=2, ensure_ascii=False)
    fp.write("\n")

# ---------------------------------------------------------------------------
# Verification: diff each step, allow only the three permitted fields to differ
# ---------------------------------------------------------------------------

def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out

violations = []
with DST.open(encoding="utf-8") as fp:
    new_tour = json.load(fp)
new_steps = {s["id"]: s for s in new_tour["steps"]}

for sid, orig in original_steps.items():
    new = new_steps.get(sid)
    if new is None:
        violations.append(f"step '{sid}' missing in enhanced output")
        continue
    of = flatten(orig)
    nf = flatten(new)
    keys = set(of.keys()) | set(nf.keys())
    for k in keys:
        if of.get(k) != nf.get(k):
            if k not in ALLOWED_FIELDS:
                violations.append(f"step '{sid}': field '{k}' was modified (FORBIDDEN)")

# Also verify top-level fields didn't change
for k in ("title", "description", "meta"):
    if json.dumps(tour.get(k)) != json.dumps(new_tour.get(k)):
        violations.append(f"top-level '{k}' was modified")

print(f"Wrote {DST.name} ({DST.stat().st_size:,} bytes, {len(tour['steps'])} steps)")
if violations:
    print(f"\n{len(violations)} VIOLATIONS:")
    for v in violations:
        print(f"  - {v}")
else:
    print("Verification passed: only description / speak.before / speak.after were modified.")
