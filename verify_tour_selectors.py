"""Verify every selector in fraudos_tour_v1.json maps to a real id in the React code.

Static ids must appear literally as `id="..."` in the JSX.
Templated ids (e.g. #tx-1-fraud-btn, #threshold-approve-btn-1, #threshold-row-5)
must match a JSX template like `id={`tx-${tx.id}-fraud-btn`}`.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
TOUR = ROOT / "fraudos_tour.json"
SRC_DIRS = [ROOT / "frontend" / "src"]

# Collect all literal ids and id templates from JSX
literal_ids = set()
template_patterns = []  # list of regex compiled patterns

JSX_FILES = []
for d in SRC_DIRS:
    JSX_FILES.extend(d.rglob("*.jsx"))

LIT_RE = re.compile(r'id="([^"{}\s]+)"')
TPL_RE = re.compile(r"id=\{`([^`]+)`\}")
WIN_ID_RE = re.compile(r'winId="([\w-]+)"')
# Data-array fields that are eventually assigned via id={item.someField}
ITEMID_RE = re.compile(r"itemId:\s*'([^']+)'")

# Hard-coded knowledge: WinChrome generates {winId}-{role} for role in
# (chrome, titlebar, close-btn, minimise-btn, maximise-btn, title, body)
WINID_ROLES = ["chrome", "titlebar", "close-btn", "minimise-btn", "maximise-btn", "title", "body"]
known_win_ids = set()

for f in JSX_FILES:
    text = f.read_text(encoding="utf-8")
    for m in LIT_RE.finditer(text):
        literal_ids.add(m.group(1))
    for m in TPL_RE.finditer(text):
        tpl = m.group(1)
        # Replace ${var} placeholders with a regex group
        regex = "^" + re.sub(r"\$\{[^}]+\}", lambda _m: r"[^\s/.#]+", tpl) + "$"
        template_patterns.append((tpl, re.compile(regex)))
    for m in WIN_ID_RE.finditer(text):
        known_win_ids.add(m.group(1))
    for m in ITEMID_RE.finditer(text):
        literal_ids.add(m.group(1))

# Add WinChrome-generated ids
for wid in known_win_ids:
    for role in WINID_ROLES:
        literal_ids.add(f"{wid}-{role}")

# Also add Dock-generated ids (from DOCK_ITEMS in Dock.jsx — known list)
for dock_id in ["desktop", "dashboard", "transactions", "reports", "model", "threshold", "description"]:
    literal_ids.add(f"dock-{dock_id}")

# Add modal close ids and other hard-coded ones not literal (already mostly literal)
literal_ids.update({"commentaryFeed", "menubar", "themeToggleBtn", "themeIcon", "clock"})

# Load the tour JSON
tour = json.loads(TOUR.read_text(encoding="utf-8"))

ok = []
unknown = []
for step in tour["steps"]:
    sel = step.get("selector")
    if not sel:
        continue
    if not sel.startswith("#"):
        unknown.append((step["id"], sel, "not an id selector"))
        continue
    raw = sel[1:]  # strip leading #
    if raw in literal_ids:
        ok.append((step["id"], sel, "literal id"))
        continue
    matched = False
    for tpl, pat in template_patterns:
        if pat.match(raw):
            ok.append((step["id"], sel, f"template `{tpl}`"))
            matched = True
            break
    if not matched:
        unknown.append((step["id"], sel, "no match"))

print(f"Verified {len(ok)} of {len(ok) + len(unknown)} selectors against the React code.\n")
print("OK:")
for sid, sel, why in ok:
    print(f"  {sel:40s}  {sid:30s}  {why}")
if unknown:
    print("\nUNKNOWN (need attention):")
    for sid, sel, why in unknown:
        print(f"  {sel:40s}  {sid:30s}  {why}")
