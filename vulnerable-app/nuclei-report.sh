#!/usr/bin/env bash
# DAT250 - run Nuclei against the vulnerable app and build ONE self-contained HTML report.
#
# Why this instead of "nuclei -me ... ; pandoc index.md":
#   * nuclei -me writes only a summary index.md + one .md per finding; pandoc on the
#     index gives you a bare table, and its links point at the .md files (they 404 in a
#     browser). This script exports JSON Lines (-jle) and renders every finding inline,
#     with no external links.
#
#   ./nuclei-report.sh                      # defaults below
#   ./nuclei-report.sh http://127.0.0.1:5000 werkzeug,headers
set -euo pipefail

URL="${1:-http://127.0.0.1:5000}"
TAGS="${2:-werkzeug,headers}"
OUT="report.html"
JSONL="findings.jsonl"

command -v nuclei >/dev/null || { echo "nuclei not installed"; exit 1; }

echo ">>> scanning $URL (tags: $TAGS)"
# -duc: don't auto-update templates mid-demo (stable finding count).
# -jle: write JSON Lines to a file; terminal output is unchanged.
# '|| true': a non-zero exit (findings present) must not stop the script.
nuclei -u "$URL" -tags "$TAGS" -duc -jle "$JSONL" || true

echo ">>> rendering $OUT from $JSONL"
python3 - "$JSONL" "$OUT" "$URL" <<'PY'
import json, sys, html, datetime
src, out, url = sys.argv[1], sys.argv[2], sys.argv[3]

rows = []
try:
    with open(src) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
except FileNotFoundError:
    rows = []

order  = ["critical", "high", "medium", "low", "info", "unknown"]
colors = {"critical":"#7b1fa2","high":"#c62828","medium":"#e07b00",
          "low":"#9e9400","info":"#1565d8","unknown":"#5f6368"}
counts = {k: 0 for k in order}
for r in rows:
    sev = (r.get("info", {}).get("severity") or "unknown").lower()
    counts[sev] = counts.get(sev, 0) + 1

def esc(x): return html.escape(str(x))

badges = "".join(
    f'<span style="display:inline-block;background:{colors[k]};color:#fff;'
    f'border-radius:6px;padding:8px 16px;margin:4px 6px 4px 0;font-size:14px;'
    f'font-weight:bold;text-transform:capitalize">{k}: {counts[k]}</span>&nbsp;'
    for k in order)

blocks = []
for r in rows:
    info = r.get("info", {})
    sev  = (info.get("severity") or "unknown").lower()
    c    = colors.get(sev, colors["unknown"])
    # Title = template name, plus the specific matcher for multi-matcher templates
    title = info.get("name") or r.get("template-id", "finding")
    matcher = r.get("matcher-name") or r.get("matcher_name")
    if matcher:
        title = f"{title} \u2014 {matcher}"
    b = [
        '<div style="margin:16px 0;border:1px solid #e3e3e3;border-radius:6px;overflow:hidden">',
        f'<div style="background:{c};color:#fff;padding:8px 12px;font-weight:700">'
        f'[{sev.upper()}] {esc(title)}</div>',
        '<div style="padding:10px 12px;font-size:14px;line-height:1.5">',
        f'<b>Host:</b> {esc(r.get("host",""))}<br>',
        f'<b>Template:</b> {esc(r.get("template-id",""))}<br>',
        f'<b>Matched at:</b> {esc(r.get("matched-at", r.get("matched","")))}',
    ]
    for label, key in (("Request", "request"), ("Response", "response")):
        if r.get(key):
            b.append(
                f'<div style="margin-top:8px"><b>{label}:</b>'
                f'<pre style="background:#f4f4f4;border:1px solid #e3e3e3;'
                f'padding:8px;white-space:pre-wrap;font-size:12px;margin:4px 0 0">'
                f'{esc(r[key])}</pre></div>')
    b += ['</div></div>']
    blocks.append("".join(b))

doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Nuclei Vulnerability Scan Report</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:30px auto;color:#1a1a2e;padding:0 16px">
<h1 style="text-align:center;margin:0">Nuclei Vulnerability Scan Report</h1>
<p style="text-align:center;color:#666;margin:6px 0 2px">Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S} &middot; Target: {esc(url)}</p>
<h2 style="margin-top:26px">Summary &ndash; {len(rows)} finding(s)</h2>
<div style="margin:6px 0 4px">{badges}</div>
<h2>Findings</h2>
{''.join(blocks) if blocks else '<p>No findings.</p>'}
</body></html>"""
open(out, "w").write(doc)
print(f"    {len(rows)} findings written to {out}")
PY

echo ">>> done:  open $OUT      (PDF:  wkhtmltopdf $OUT report.pdf)"