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
      size: letter;
      margin: 25.4mm 25.4mm 25.4mm 25.4mm;
    }}
    body {{
      font-family: "Times New Roman", Times, Georgia, serif;
      font-size: 12pt;
      line-height: 2.0;
      color: #000000;
      background: #ffffff;
      max-width: 100%;
      margin: 0;
    }}
    h1 {{
      font-size: 12pt;
      font-weight: bold;
      text-align: center;
      color: #000000;
      margin: 0 0 12pt 0;
    }}
    h2 {{
      font-size: 12pt;
      font-weight: bold;
      text-align: center;
      color: #000000;
      margin-top: 18pt;
      margin-bottom: 6pt;
      page-break-after: avoid;
    }}
    h3 {{
      font-size: 12pt;
      font-weight: bold;
      text-align: left;
      color: #000000;
      margin-top: 14pt;
      margin-bottom: 4pt;
      page-break-after: avoid;
    }}
    h4 {{
      font-size: 12pt;
      font-weight: bold;
      font-style: italic;
      text-align: left;
      color: #000000;
      margin-top: 12pt;
      margin-bottom: 4pt;
      page-break-after: avoid;
    }}
    p {{
      text-align: left;
      margin: 0 0 8pt 0;
    }}
    ul, ol {{
      margin: 4pt 0 10pt 0;
      padding-left: 24pt;
    }}
    li {{
      margin-bottom: 3pt;
    }}
    code {{
      font-family: "Times New Roman", Times, serif;
      font-size: 11pt;
      background: transparent;
      color: #000000;
      padding: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 10pt 0 14pt 0;
      font-size: 9.5pt;
      line-height: 1.35;
      color: #000000;
      page-break-inside: auto;
    }}
    thead {{
      display: table-header-group;
    }}
    tr {{
      page-break-inside: avoid;
    }}
    th {{
      border-top: 1.2pt solid #000000;
      border-bottom: 0.8pt solid #000000;
      background: #ffffff;
      color: #000000;
      padding: 5pt 5pt;
      text-align: left;
      font-weight: bold;
    }}
    td {{
      border: none;
      padding: 4pt 5pt;
      vertical-align: top;
      color: #000000;
    }}
    tbody tr:last-child td {{
      border-bottom: 1.2pt solid #000000;
    }}
    img {{
      display: block;
      max-width: 100%;
      max-height: 125mm;
      width: auto;
      height: auto;
      margin: 8pt auto 6pt auto;
      border: 0.5pt solid #000000;
      page-break-inside: avoid;
    }}
    hr {{
      border: none;
      border-top: 0.8pt solid #000000;
      margin: 12pt 0;
    }}
    a {{
      color: #000000;
      text-decoration: none;
    }}
    .katex-display {{
      margin: 10pt 0;
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
            katex_errors = page.locator(".katex-error").count()
            if katex_errors:
                bad = [page.locator(".katex-error").nth(i).inner_text() for i in range(katex_errors)]
                raise RuntimeError(f"KaTeX render errors ({katex_errors}): {bad}")
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
