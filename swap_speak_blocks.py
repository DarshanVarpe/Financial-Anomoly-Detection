"""Replace only the `speak` blocks in mock-rahul-aegis.json using the per-step
mapping provided.  Every other field — title, description, meta, action,
selector, highlight, pause, descriptions on each step — must stay byte-identical.

After writing, the script flattens both versions and reports any field outside
`speak.*` that mutated, then exits non-zero if a violation is found.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "mock-rahul-aegis.json"
DST = ROOT / "mock-rahul-aegis.json"  # in-place

# ---------------------------------------------------------------------------
# Per-step speak replacements supplied by the user
# ---------------------------------------------------------------------------
REPLACEMENTS = {
    "intro": {
        "before": "Hi, I'm Rahul. I help fraud investigators review suspicious transactions, understand why they were flagged, and take the right action with a clear audit trail. I'll walk you through the full FraudOS workflow: dashboard overview, flagged transaction review, read-only descriptions, compliance reports, model performance, threshold configuration, and the home utilities.",
    },
    "home-live-activity": {
        "before": "We are starting on the FraudOS home screen. The two desktop utilities are Notes and Calendar, and the main fraud modules are available from the dock at the bottom.",
        "after": "On the right, this Live Activity feed shows every important fraud event as it happens. When a transaction is confirmed as fraud or cleared as safe, the event appears here with the time and investigator action.",
    },
    "open-dashboard": {
        "before": "I am opening the Dashboard from the dock now.",
        "after": "The fraud dashboard is open. This is where I first check the overall fraud picture before reviewing individual transactions.",
    },
    "dashboard-banner": {
        "before": "At the top, this banner confirms which dashboard we are on and which detection models are active.",
        "after": "The dashboard is running with Isolation Forest, LSTM, and Azure OpenAI. Together, these models help identify unusual transaction patterns and explain why a transaction was flagged.",
    },
    "kpi-grid": {
        "before": "These four KPI cards give me the quick summary for today's fraud activity. I check these before taking action so I know the current volume, flagged count, confirmed fraud count, and false positive rate.",
    },
    "kpi-total": {
        "before": "This first card shows the total number of transactions currently in the database.",
        "after": "It helps confirm that the transaction feed is active and that we are looking at the right data volume for today's review.",
    },
    "kpi-flagged": {
        "before": "This second card shows how many transactions were flagged by the fraud model.",
        "after": "These are the transactions that crossed the risk threshold and now need a human review before a final decision is made.",
    },
    "kpi-fraud": {
        "before": "This third card shows confirmed fraud.",
        "after": "These are transactions that an investigator has already reviewed and marked as fraud. Every confirmation is stored with the score, timestamp, and decision details.",
    },
    "kpi-fprate": {
        "before": "This fourth card shows the false positive rate.",
        "after": "This number matters because it tells us how often legitimate transactions are being flagged. If it gets too high, we may need to tune the thresholds later.",
    },
    "dashboard-timeseries": {
        "before": "This chart shows flagged transactions over the last twenty-four hours.",
        "after": "The main line shows total flagged transactions, and the fraud line shows how many were actually confirmed. The gap between them is where false positives usually appear.",
    },
    "dashboard-riskdist": {
        "before": "This donut chart groups flagged transactions by risk level.",
        "after": "Critical and high-risk transactions are the ones I review first because the model is more confident that something unusual is happening.",
    },
    "dashboard-table": {
        "before": "This table gives a read-only preview of the flagged transactions.",
        "after": "Each row shows the transaction ID, amount, location, model scores, ensemble score, and status. The highest-risk transaction here is the large Hong Kong wire transfer with an ensemble score of zero point nine seven.",
    },
    "open-transactions": {
        "before": "Now I am opening the Transactions queue. This is where I actually review and decide on each flagged transaction.",
        "after": "The review queue is open. Here I can confirm fraud, clear a false positive, or escalate a transaction for more investigation.",
    },
    "transactions-toolbar": {
        "before": "This toolbar helps narrow the queue.",
        "after": "I can search by transaction ID, location, or amount, and I can filter by model, score band, or review status. This makes it easier to focus on the highest-priority cases.",
    },
    "transactions-status-filter": {
        "before": "I am opening the status filter so I can focus on transactions that still need review.",
    },
    "transactions-table": {
        "before": "This is the main transaction review table. Each row includes the transaction details, model scores, AI explanation, current status, and available actions.",
        "after": "Before I click Fraud, Clear, or Escalate, I read the explanation and compare it with the risk score. The goal is to make a decision that is explainable, not just automatic.",
    },
    "transaction-fraud-action": {
        "before": "I am reviewing the top transaction, TXN-20240424-0064. It is a large wire transfer from Hong Kong, initiated from a new device, with an ensemble score of zero point nine seven. That is a critical-risk pattern, so I am confirming it as fraud.",
        "during": "High score, new country, new device, and large transfer amount. This is strong fraud evidence.",
        "after": "Fraud confirmed. The row status has updated, the live feed has logged a detection event, the confirmed fraud count has increased, and the decision is now available in the audit trail.",
    },
    "transaction-clear-action": {
        "before": "Now I am reviewing TXN-20240424-0091. The model flagged it because the amount is high and the device is unfamiliar, but investigator context says the customer was travelling and approved the purchase.",
        "after": "I cleared it as a false positive. The row status is now Cleared, the live feed shows a cleared event, and the decision becomes useful feedback for improving the model.",
    },
    "open-description": {
        "before": "Next, I am opening the Description page.",
        "after": "This page shows the same flagged transaction data, but without action buttons. It is useful for audits, demos, and stakeholder reviews where nobody should accidentally change a transaction status.",
    },
    "description-table": {
        "before": "This is the read-only transaction table.",
        "after": "You can inspect the same transaction IDs, scores, locations, explanations, and statuses, but there are no Fraud, Clear, or Escalate buttons here. This keeps the page safe for review-only use.",
    },
    "open-reports": {
        "before": "Now I am opening Compliance Reports.",
        "after": "The Reports screen is open. This is where daily compliance evidence and historical fraud reports are stored.",
    },
    "reports-today": {
        "before": "This card is today's compliance report.",
        "after": "It summarizes processed transactions, flagged cases, confirmed fraud, false positive rate, review completion, and how helpful the AI explanations were during investigation.",
    },
    "reports-download-today": {
        "before": "I am downloading today's compliance report.",
        "after": "The report PDF has been downloaded and can be used as evidence for compliance review.",
    },
    "reports-archive": {
        "before": "This archive stores previous daily reports.",
        "after": "Each row has the report date, transaction volume, flagged count, fraud count, false positive rate, F1 score, and a download option. If compliance asks for a past report, I can retrieve it from here.",
    },
    "open-model": {
        "before": "Next, I am opening Model Performance.",
        "after": "This screen shows how the fraud models are performing and gives us the audit log of investigator decisions.",
    },
    "model-cards": {
        "before": "These three cards show the individual model performance.",
        "after": "Isolation Forest focuses on unusual single-point anomalies, LSTM looks at transaction sequence patterns, and the Ensemble combines both signals. I use these numbers to understand whether the detection system is accurate or over-flagging.",
    },
    "model-card-ensemble": {
        "before": "The Ensemble Model is the main production decision model.",
        "after": "It has the strongest overall balance: high precision, high recall, a strong F1 score, and the lowest false positive rate among the three models. That is why its score drives the final fraud flag.",
    },
    "model-fp-trend": {
        "before": "This chart tracks the false positive rate over the last eight weeks.",
        "after": "The trend is moving in the right direction. False positives started high, then dropped toward the target line as thresholds were tuned.",
    },
    "model-audit-log": {
        "before": "This is the investigator audit log.",
        "after": "Every decision is recorded here with transaction reference, action, model score, timestamp, and notes. The fraud confirmation and clearance actions I performed earlier are now visible in this log.",
    },
    "open-thresholds": {
        "before": "Now I am opening Threshold Configuration.",
        "after": "This is where threshold changes are reviewed before approval. The goal is to reduce false positives without damaging fraud recall.",
    },
    "threshold-admin-badge": {
        "before": "Before approving anything, I check the Admin Role Active badge.",
        "after": "The admin role is active, so approval actions are allowed. If this badge were missing, I would stop here and not attempt any threshold approval.",
    },
    "threshold-table": {
        "before": "This table lists the threshold proposals by category.",
        "after": "For each proposal, I compare the current threshold, proposed threshold, expected false positive impact, recall impact, status, and available action. I never approve a change that pushes recall below the required floor.",
    },
    "threshold-approve-action": {
        "before": "I am reviewing the Crypto Exchange proposal. The threshold moves from zero point seven zero to zero point seven five. It reduces false positives by ten percent, while recall only drops by zero point eight percent.",
        "during": "False positives improve, and recall stays within the safe range.",
        "after": "Approved. The proposal status has changed from Pending to Approved, and the threshold change is now submitted for the weekly approval cycle.",
    },
    "threshold-blocked-row": {
        "before": "This last row is blocked automatically.",
        "after": "The proposed Wallet Transfer Domestic change would reduce recall too much. Since it would fall below the allowed recall floor, the system removes the approval option. I do not override that block.",
    },
    "threshold-rules-note": {
        "before": "This note summarizes the threshold approval rules.",
        "after": "Every threshold change needs sign-off. Any proposal that would reduce recall below the allowed limit is blocked. Approved, pending, and blocked changes are all stored for audit.",
    },
    "return-home": {
        "before": "I am returning to the home desktop.",
        "after": "We are back at the home screen. Notes and Calendar are available here for investigation notes and follow-up scheduling.",
    },
    "desktop-notes-icon": {
        "before": "I am opening Notes.",
        "after": "The Notes modal is open. Investigators can use this to capture investigation context or decision rationale during review.",
    },
    "notes-close": {
        "before": "Closing Notes.",
    },
    "desktop-calendar-icon": {
        "before": "Now I am opening Calendar.",
        "after": "The Calendar is open. This can be used to schedule case follow-ups, review reminders, or escalation dates.",
    },
    "calendar-close": {
        "before": "Closing Calendar.",
    },
    "outro": {
        "before": "That completes the FraudOS walkthrough. We reviewed the live activity feed, dashboard metrics, transaction queue, read-only description page, compliance reports, model performance, threshold configuration, Notes, and Calendar. The most important takeaway is that every fraud decision is explainable, reviewable, and recorded. What would you like to inspect next?",
    },
}

# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------
text = SRC.read_text(encoding="utf-8")
tour = json.loads(text)

original_steps = {s["id"]: json.loads(json.dumps(s)) for s in tour["steps"]}
original_top_level = {k: v for k, v in tour.items() if k != "steps"}

for step in tour["steps"]:
    sid = step["id"]
    if sid not in REPLACEMENTS:
        print(f"  WARNING - no replacement for step '{sid}', leaving untouched")
        continue
    step["speak"] = REPLACEMENTS[sid]

# Pretty-print with 2-space indent, preserve UTF-8
DST.write_text(
    json.dumps(tour, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

# ---------------------------------------------------------------------------
# Verify nothing outside `speak.*` changed
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

final = json.loads(DST.read_text(encoding="utf-8"))

violations = []

# Top-level fields must be byte-identical
for k, v in original_top_level.items():
    if json.dumps(v, sort_keys=True) != json.dumps(final.get(k), sort_keys=True):
        violations.append(f"top-level field '{k}' changed (FORBIDDEN)")

# Per-step: every leaf key not under speak.* must be byte-identical
final_steps = {s["id"]: s for s in final["steps"]}
allowed_changes = 0
for sid, orig in original_steps.items():
    new = final_steps.get(sid)
    if new is None:
        violations.append(f"step '{sid}' missing in output")
        continue
    of = flatten(orig)
    nf = flatten(new)
    for k in set(of) | set(nf):
        if of.get(k) != nf.get(k):
            if k.startswith("speak"):
                allowed_changes += 1
            else:
                violations.append(f"step '{sid}' :: '{k}' changed (FORBIDDEN)")

print(f"Wrote {DST.name} ({DST.stat().st_size:,} bytes, {len(tour['steps'])} steps)")
print(f"Allowed changes inside speak.* : {allowed_changes}")
if violations:
    print(f"\n{len(violations)} VIOLATIONS:")
    for v in violations:
        print(f"  - {v}")
    raise SystemExit(1)
print("\nVerification passed: only speak.* fields were modified.")
