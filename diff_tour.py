"""Standalone structural diff between fraudos_tour_structural.json and
fraudos_tour.json.

Pass condition: only `description`, `speak.before`, and `speak.after` differ
on each step.  Everything else (id, action, selector, highlight, pause,
speak.during, top-level title / description / meta) must be byte-identical.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
A = ROOT / "fraudos_tour_structural.json"
B = ROOT / "fraudos_tour.json"

ALLOWED = {"description", "speak.before", "speak.after"}


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


a = json.loads(A.read_text(encoding="utf-8"))
b = json.loads(B.read_text(encoding="utf-8"))

print("=" * 78)
print("Structural diff: fraudos_tour_structural.json  vs  fraudos_tour.json")
print("=" * 78)

# --- Top-level checks ----------------------------------------------------
print("\n[ top-level fields ]")
for key in ("title", "description", "meta"):
    same = json.dumps(a.get(key), sort_keys=True) == json.dumps(b.get(key), sort_keys=True)
    print(f"  {key:14s} {'IDENTICAL' if same else 'DIFFERS (forbidden)'}")

# --- Step count ----------------------------------------------------------
print(f"\n[ step count ]  structural={len(a['steps'])}  enhanced={len(b['steps'])}")
assert len(a["steps"]) == len(b["steps"]), "step counts differ"

# --- Per-step structural diff -------------------------------------------
violations = []
allowed_changes = []  # list of (sid, field) tuples that legitimately changed

for sa, sb in zip(a["steps"], b["steps"]):
    sid = sa["id"]
    if sa["id"] != sb["id"]:
        violations.append(f"step order mismatch at id '{sid}' vs '{sb['id']}'")
        continue
    flat_a = flatten(sa)
    flat_b = flatten(sb)
    keys = set(flat_a.keys()) | set(flat_b.keys())
    for k in sorted(keys):
        if flat_a.get(k) != flat_b.get(k):
            if k in ALLOWED:
                allowed_changes.append((sid, k))
            else:
                violations.append(f"step '{sid}' :: field '{k}' was modified (FORBIDDEN)")

# --- Report --------------------------------------------------------------
print(f"\n[ allowed-field changes ]  {len(allowed_changes)} mutations across 41 steps")
breakdown = {}
for sid, field in allowed_changes:
    breakdown[field] = breakdown.get(field, 0) + 1
for field in sorted(breakdown):
    print(f"  {field:25s} {breakdown[field]:3d} steps")

print(f"\n[ forbidden-field changes ]  {len(violations)}")
if violations:
    for v in violations:
        print(f"  [FAIL] {v}")
else:
    print("  [OK] none")

# --- Final verdict -------------------------------------------------------
print("\n" + "=" * 78)
if violations:
    print("FAIL — JSON 2 modified fields outside the allowed set.")
    raise SystemExit(1)
else:
    print("PASS — JSON 2 differs from JSON 1 only in description / speak.before / speak.after.")
    print("       All structural fields (id, action, selector, highlight, pause,")
    print("       speak.during, title, top-level description, meta) are byte-identical.")
print("=" * 78)
