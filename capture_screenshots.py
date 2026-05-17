"""Capture the seven FraudOS v2 screens from a running frontend.

Assumes the frontend is reachable at http://localhost (port 80).
Run after `docker run` has started fraudos-frontend.
"""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

BASE = "http://localhost"

# (filename, navigation_steps)
# Each navigation_steps is a list of click selectors performed in order.
# After clicks, we wait for network idle and then capture.
SHOTS = [
    ("scr-001-home.png",         []),                              # already on home
    ("scr-002-dashboard.png",    ["#dock-dashboard"]),
    ("scr-003-transactions.png", ["#dock-desktop", "#dock-transactions"]),
    ("scr-004-reports.png",      ["#dock-desktop", "#dock-reports"]),
    ("scr-005-model.png",        ["#dock-desktop", "#dock-model"]),
    ("scr-006-thresholds.png",   ["#dock-desktop", "#dock-threshold"]),
    ("scr-007-description.png",  ["#dock-desktop", "#dock-description"]),
]

VIEWPORT = {"width": 1456, "height": 816}


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = context.new_page()
        page.goto(BASE, wait_until="networkidle")
        time.sleep(2)  # let charts render

        for filename, steps in SHOTS:
            for selector in steps:
                page.locator(selector).first.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1.5)  # charts and table loads
            target = OUT / filename
            page.screenshot(path=str(target), full_page=False)
            size_kb = target.stat().st_size / 1024
            print(f"  {filename:30s}  {size_kb:6.1f} KB")

        browser.close()
    print(f"All {len(SHOTS)} screenshots saved to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
