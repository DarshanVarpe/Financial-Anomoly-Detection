"""Convert FraudOS humanoid spec markdown to a polished PDF using Playwright/Chromium.

Why Playwright instead of xhtml2pdf:
- xhtml2pdf has known bugs with table-layout: text bleeds across cells
- Playwright uses real Chromium rendering — same engine as the browser
- Gives consistent typography, proper word-wrap, clean page breaks, embedded images

CSS is modelled on the official Virtual Humanoid Flow Template (PDF) layout:
- A4 landscape with uniform 1.4 cm margins
- Calibri/Arial sans-serif body, 9pt
- White-on-navy table headers, alternating row stripes
- All tables span 100% width with the same padding and font
- Screenshots constrained to a fixed reasonable width so Section 10 does not
  dominate the document
"""
import sys
from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

import os
import time

ROOT = Path(__file__).parent
SRC = ROOT / "Fraud_OS_Virtual_Humanoid_User_flow.md"
DST = ROOT / "Fraud_OS_Virtual_Humanoid_User_flow.pdf"
HTML_TMP = ROOT / "_humanoid_tmp.html"


def _safe_replace(target: Path, new_path: Path) -> None:
    """Replace target with new_path, working around Windows file locks."""
    if not target.exists():
        new_path.replace(target)
        return
    try:
        new_path.replace(target)
    except PermissionError:
        # File is open (e.g., PDF viewer holds a lock).  Write a timestamped
        # variant beside it and tell the user.
        ts = time.strftime("%H%M%S")
        fallback = target.with_name(f"{target.stem}__{ts}{target.suffix}")
        new_path.replace(fallback)
        print(f"!! {target.name} is locked. Saved as {fallback.name} instead.")
        print(f"   Close the PDF viewer and rename {fallback.name} -> {target.name}.")

CSS = """
@page {
    size: A4 landscape;
    margin: 1.3cm 1.2cm 1.5cm 1.2cm;
}

* { box-sizing: border-box; }

html, body {
    font-family: Calibri, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 9.2pt;
    line-height: 1.35;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 22pt;
    color: #0b3d91;
    margin: 0 0 6pt 0;
    padding-bottom: 4pt;
    border-bottom: 2pt solid #0b3d91;
    page-break-after: avoid;
}
h2 {
    font-size: 13pt;
    color: #0b3d91;
    margin: 14pt 0 4pt 0;
    padding-top: 4pt;
    border-top: 1pt solid #c0c8d8;
    page-break-after: avoid;
    page-break-inside: avoid;
}
h3 {
    font-size: 10.5pt;
    color: #1f4e91;
    margin: 9pt 0 3pt 0;
    page-break-after: avoid;
    page-break-inside: avoid;
}
h4 {
    font-size: 9.8pt;
    color: #1f4e91;
    margin: 6pt 0 2pt 0;
    page-break-after: avoid;
}

p { margin: 3pt 0; }
em { color: #555; }
hr { border: 0; border-top: 1pt solid #c0c8d8; margin: 9pt 0; }
ul, ol { margin: 3pt 0 3pt 16pt; padding: 0; }
li { margin: 1pt 0; }

/* Inline code (selectors) */
code {
    font-family: Consolas, "Courier New", Courier, monospace;
    font-size: 8pt;
    background-color: #eef2f7;
    padding: 0.5pt 3pt;
    border-radius: 2pt;
    color: #0b3d91;
    word-break: break-all;
    white-space: nowrap;
}

/* Code blocks (JSON) */
pre {
    font-family: Consolas, "Courier New", Courier, monospace;
    font-size: 7.8pt;
    background-color: #f4f6fa;
    border: 0.5pt solid #c0c8d8;
    padding: 6pt 8pt;
    margin: 4pt 0;
    line-height: 1.32;
    white-space: pre-wrap;
    word-break: break-word;
    page-break-inside: avoid;
}
pre code {
    background: transparent;
    padding: 0;
    color: #1a1a1a;
    font-size: 7.8pt;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Tables — uniform layout */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 4pt 0 8pt 0;
    font-size: 8pt;
    table-layout: auto;
    page-break-inside: auto;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th {
    background-color: #1f4e91;
    color: #ffffff;
    font-weight: 600;
    padding: 4pt 6pt;
    border: 0.5pt solid #1f4e91;
    text-align: left;
    vertical-align: top;
    font-size: 8.4pt;
}
td {
    padding: 3.5pt 6pt;
    border: 0.5pt solid #c0c8d8;
    vertical-align: top;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: normal;
    hyphens: auto;
}
tbody tr:nth-child(even) td { background-color: #f7f9fc; }

/* Code inside table cells — slightly smaller, allow break */
td code, th code {
    font-size: 7.4pt;
    padding: 0.5pt 2pt;
    word-break: break-all;
    white-space: normal;
}

strong { color: #0b3d91; }

/* Section 10 screenshots — constrained so they don't dominate */
img {
    display: block;
    max-width: 22cm;
    width: 100%;
    height: auto;
    border: 0.5pt solid #c0c8d8;
    margin: 5pt auto 8pt auto;
    page-break-inside: avoid;
}

/* Force major sections to start on a fresh page where it makes the document
   feel more uniform (like the original template). The template puts each
   numbered section near the top of a page. */
h2 { page-break-before: auto; }

/* Footer rendered via Playwright's footer template (cleaner than HTML) */
"""

FOOTER_TEMPLATE = """
<div style="font-size:8pt; color:#666; width:100%; padding:0 1.2cm; display:flex; justify-content:space-between; font-family:Calibri,Arial,sans-serif;">
    <span>FraudOS &mdash; AEGIS.AI &middot; Virtual Humanoid User Flow Specification</span>
    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>
"""

HEADER_TEMPLATE = "<div></div>"  # empty header


def main() -> int:
    md_text = SRC.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )
    html_doc = (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head><body>{html_body}</body></html>"
    )
    HTML_TMP.write_text(html_doc, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        # file:// URL so relative image paths resolve (screenshots/scr-*.png)
        file_url = HTML_TMP.resolve().as_uri()
        page.goto(file_url, wait_until="networkidle")
        tmp_pdf = ROOT / "_humanoid_tmp.pdf"
        page.pdf(
            path=str(tmp_pdf),
            format="A4",
            landscape=True,
            margin={"top": "1.3cm", "bottom": "1.5cm", "left": "1.2cm", "right": "1.2cm"},
            print_background=True,
            display_header_footer=True,
            header_template=HEADER_TEMPLATE,
            footer_template=FOOTER_TEMPLATE,
            prefer_css_page_size=False,
        )
        browser.close()

    HTML_TMP.unlink(missing_ok=True)
    _safe_replace(DST, tmp_pdf)
    final = DST if DST.exists() else next(ROOT.glob(f"{DST.stem}__*.pdf"))
    print(f"Wrote {final} ({final.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
