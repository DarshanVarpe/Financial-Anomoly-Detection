Screenshots for FraudOS Virtual Humanoid User Flow Specification (v2)

Save the seven UI screenshots here using these EXACT filenames so they
embed correctly in Section 10 of the PDF:

    scr-001-home.png            - FraudOS Home Desktop (Notes/Calendar icons + dock)
    scr-002-dashboard.png       - AI Fraud Detection Dashboard (KPI tiles + charts)
    scr-003-transactions.png    - Flagged Transaction Review Queue (with Fraud/Clear buttons)
    scr-004-reports.png         - Compliance Reports (today + archive table)
    scr-005-model.png           - Model Performance Panel (3 cards + FP trend)
    scr-006-thresholds.png      - Threshold Configuration Panel (Admin Role + 5 categories)
    scr-007-description.png     - Transaction Description (read-only, no Actions column)

Recommended:
  - PNG format
  - Width 1600-1920 px
  - File size under 1 MB each (PDF stays compact)
  - Capture from http://134.33.132.134/rahul-aegis-fe (production) or http://localhost (local Docker)

After saving, regenerate the PDF:
    python md_to_pdf.py

If a file is missing the PDF will still build, but Section 10 will show
broken-image markers next to the detailed text descriptions.
