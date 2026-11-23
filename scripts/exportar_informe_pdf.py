"""
Convierte docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md a un PDF académico APA 7
con todas las 13 figuras embebidas y ecuaciones LaTeX renderizadas mediante KaTeX
y Chrome Headless (Playwright).
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.md"
PDF_PATH = ROOT / "docs/CAPITULOS_5_6_7_INFORME_FINAL_APA7.pdf"
TMP_HTML = ROOT / "docs/_tmp_informe_apa7.html"


def embed_images_as_data_uri(md_text: str, base_dir: Path) -> str:
    def _repl(match: re.Match[str]) -> str:
        alt, rel_path = match.group(1), match.group(2)
        img_file = (base_dir / rel_path).resolve()
        if not img_file.exists():
            return match.group(0)
        b64 = base64.b64encode(img_file.read_bytes()).decode("ascii")
        ext = img_file.suffix.lstrip(".").lower() or "png"
        return f"![{alt}](data:image/{ext};base64,{b64})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _repl, md_text)


def main() -> None:
    raw_md = MD_PATH.read_text(encoding="utf-8")
    md_with_imgs = embed_images_as_data_uri(raw_md, MD_PATH.parent)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Capítulos 5, 6 y 7 — SentinelNutri-HVC (APA 7)</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" />
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
  <style>
    @page {{
      size: A4;
      margin: 20mm 18mm 20mm 18mm;
    }}
    body {{
      font-family: "Times New Roman", Georgia, "Liberation Serif", serif;
      font-size: 10.5pt;
      line-height: 1.48;
      color: #1a1a1a;
      max-width: 100%;
      margin: 0;
    }}
    h1 {{
      font-size: 16pt;
      color: #0f2c59;
      border-bottom: 2px solid #0f2c59;
      padding-bottom: 6px;
      margin-top: 0;
    }}
    h2 {{
      font-size: 13.5pt;
      color: #0f4c81;
      margin-top: 22px;
      page-break-after: avoid;
    }}
    h3 {{
      font-size: 11.5pt;
      color: #1b3a57;
      margin-top: 16px;
      page-break-after: avoid;
    }}
    h4 {{
      font-size: 10.5pt;
      color: #2c3e50;
      margin-top: 12px;
      page-break-after: avoid;
    }}
    p {{
      text-align: justify;
      margin: 6px 0 9px 0;
    }}
    ul, ol {{
      margin: 6px 0 10px 0;
      padding-left: 22px;
    }}
    li {{
      margin-bottom: 4px;
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 9pt;
      background: #f4f6f8;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0 14px 0;
      font-size: 8.6pt;
      line-height: 1.3;
      page-break-inside: auto;
    }}
    thead {{
      display: table-header-group;
    }}
    tr {{
      page-break-inside: avoid;
    }}
    th {{
      border-top: 1.5px solid #1a1a1a;
      border-bottom: 1px solid #1a1a1a;
      background: #f3f6fa;
      padding: 5px 6px;
      text-align: left;
      font-weight: bold;
    }}
    td {{
      border-bottom: 0.5px solid #d5dbe3;
      padding: 4px 6px;
      vertical-align: top;
    }}
    tbody tr:last-child td {{
      border-bottom: 1.5px solid #1a1a1a;
    }}
    img {{
      display: block;
      max-width: 100%;
      max-height: 130mm;
      width: auto;
      height: auto;
      margin: 8px auto 6px auto;
      border: 0.6px solid #cfd8dc;
      border-radius: 3px;
      page-break-inside: avoid;
    }}
    hr {{
      border: none;
      border-top: 1px solid #cfd8dc;
      margin: 14px 0;
    }}
    a {{
      color: #0f4c81;
      text-decoration: none;
    }}
    .katex-display {{
      margin: 10px 0;
      overflow-x: auto;
    }}
  </style>
</head>
<body>
  <div id="content"></div>
  <script>
    const rawMd = {json.dumps(md_with_imgs, ensure_ascii=False)};
    // Proteger bloques de LaTeX antes de marked para evitar que _ o * se interpreten como cursiva
    const mathBlocks = [];
    let safeMd = rawMd.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (_, m) => {{
      const idx = mathBlocks.length;
      mathBlocks.push({{ display: true, tex: m }});
      return `@@MATH_BLOCK_${{idx}}@@`;
    }});
    safeMd = safeMd.replace(/\\$([^\\$\\n]+?)\\$/g, (_, m) => {{
      const idx = mathBlocks.length;
      mathBlocks.push({{ display: false, tex: m }});
      return `@@MATH_INLINE_${{idx}}@@`;
    }});

    marked.setOptions({{ gfm: true, breaks: false }});
    let html = marked.parse(safeMd);

    html = html.replace(/@@MATH_(BLOCK|INLINE)_(\\d+)@@/g, (_, kind, idxStr) => {{
      const item = mathBlocks[Number(idxStr)];
      try {{
        return katex.renderToString(item.tex, {{
          displayMode: item.display,
          throwOnError: false,
        }});
      }} catch (e) {{
        return item.tex;
      }}
    }});

    document.getElementById("content").innerHTML = html;
    window.__RENDER_DONE__ = true;
  </script>
</body>
</html>
"""

    TMP_HTML.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel="chrome")
            except Exception:
                browser = p.chromium.launch(channel="msedge")
            page = browser.new_page()
            page.goto(TMP_HTML.resolve().as_uri(), wait_until="networkidle", timeout=60000)
            page.wait_for_function("window.__RENDER_DONE__ === true", timeout=30000)
            page.wait_for_timeout(1500)
            img_count = page.locator("img").count()
            page.pdf(
                path=str(PDF_PATH),
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template="<div style='font-size:8px;color:#666;width:100%;text-align:right;padding-right:18mm;'>SentinelNutri-HVC · Capítulos 5, 6 y 7 (APA 7)</div>",
                footer_template="<div style='font-size:8px;color:#666;width:100%;text-align:center;'>Página <span class='pageNumber'></span> de <span class='totalPages'></span></div>",
                margin={"top": "20mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
            )
            browser.close()
            print(f"PDF_OK: {PDF_PATH} | size={PDF_PATH.stat().st_size} bytes | imgs={img_count}")
    finally:
        if TMP_HTML.exists():
            TMP_HTML.unlink()


if __name__ == "__main__":
    main()
