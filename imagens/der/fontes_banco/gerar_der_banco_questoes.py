"""Gera o DER do banco de questões (8 tabelas) em SVG e PNG (Chrome headless).
Uso: python gerar_der_banco_questoes.py <pasta_de_saida>"""
import os, subprocess, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
W, H = 1180, 960
HEAD, ROW = 32, 32
BLUE, BODY, LINE, MUTED = "#2f6697", "#f3f3f3", "#8a8a8a", "#6b6b6b"

TABLES = {
    "areas": (40, 40, 250, [("id", "INTEGER", "PK"), ("name", "TEXT", "")]),
    "processes": (400, 40, 280, [("id", "INTEGER", "PK"), ("area_id", "INTEGER", "FK"), ("name", "TEXT", "")]),
    "activities": (800, 40, 280, [("id", "INTEGER", "PK"), ("process_id", "INTEGER", "FK"), ("name", "TEXT", "")]),
    "documents": (40, 300, 250, [("id", "TEXT", "PK"), ("code", "TEXT", ""), ("title", "TEXT", ""),
                                  ("revision", "INTEGER", ""), ("implantacao", "TEXT", ""), ("regenerated_week", "TEXT", "")]),
    "document_processes": (400, 300, 280, [("document_id", "TEXT", "PK,FK"), ("process_id", "INTEGER", "PK,FK")]),
    "questions": (400, 470, 300, [("id", "TEXT", "PK"), ("pipeline", "TEXT", ""), ("document_id", "TEXT", "FK"),
                                  ("process_id", "INTEGER", "FK"), ("question_type", "TEXT", ""), ("statement", "TEXT", ""),
                                  ("explanation", "TEXT", ""), ("source_excerpt", "TEXT", ""), ("source_pages", "TEXT", ""),
                                  ("document_revision", "INTEGER", ""), ("is_active", "INTEGER", ""), ("retired_at", "TEXT", "")]),
    "question_options": (800, 470, 300, [("question_id", "TEXT", "PK,FK"), ("letter", "TEXT", "PK"), ("text", "TEXT", ""),
                                         ("is_correct", "INTEGER", ""), ("rationale", "TEXT", "")]),
    "question_flags": (800, 740, 300, [("question_id", "TEXT", "FK"), ("flag", "TEXT", ""), ("detail", "TEXT", "")]),
}

parts = []
def add(s): parts.append(s)

def row_y(table, field):
    x, y, w, fields = TABLES[table]
    i = [f[0] for f in fields].index(field)
    return y + HEAD + i * ROW + ROW / 2

def edge(table, side):
    x, y, w, fields = TABLES[table]
    return x if side == "l" else x + w

def draw_table(name):
    x, y, w, fields = TABLES[name]
    h = HEAD + ROW * len(fields)
    add('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="#d0d0d0" filter="url(#sh)"/>' % (x, y, w, h, BODY))
    add('<path d="M%d,%d h%d v%d h-%d z" fill="%s"/>' % (x, y + HEAD, w, 0, w, BLUE))
    add('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s"/>' % (x, y, w, HEAD, BLUE))
    add('<rect x="%d" y="%d" width="%d" height="6" fill="%s"/>' % (x, y + HEAD - 6, w, BLUE))
    add('<text x="%d" y="%d" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#fff">%s</text>' % (x + 12, y + 21, escape(name)))
    for i, (fname, ftype, key) in enumerate(fields):
        cy = y + HEAD + i * ROW + ROW / 2
        bold = "bold" if "PK" in key else "normal"
        add('<text x="%d" y="%d" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="%s" fill="#222">%s</text>' % (x + 12, cy + 4.5, bold, escape(fname)))
        add('<text x="%d" y="%d" font-family="Consolas, monospace" font-size="11.5" fill="%s" text-anchor="end">%s</text>' % (x + w - 12, cy + 4, MUTED, ftype))
        if key:
            tag = key.replace(",", " ")
            tx = x + 12 + len(fname) * 7.4 + 8
            add('<text x="%.1f" y="%.1f" font-family="Segoe UI, Arial, sans-serif" font-size="9.5" font-weight="bold" fill="%s">%s</text>' % (tx, cy + 3.5, "#2f6697", tag))

def poly(points, parent_end=True):
    d = "M" + " L".join("%.1f,%.1f" % p for p in points)
    add('<path d="%s" fill="none" stroke="%s" stroke-width="1.2"/>' % (d, LINE))
    # extremidade "pai" (barra) no início e "pé de galinha" no fim
    (x0, y0), (x1, y1) = points[0], points[1]
    dx, dy = (x1 - x0), (y1 - y0)
    n = max(abs(dx), abs(dy)) or 1
    ux, uy = dx / n, dy / n
    bx, by = x0 + ux * 8, y0 + uy * 8
    add('<path d="M%.1f,%.1f l%.1f,%.1f m%.1f,%.1f l%.1f,%.1f" stroke="%s" stroke-width="1.2"/>' % (bx - uy * 5, by + ux * 5, uy * 10, -ux * 10, 0, 0, 0, 0, LINE))
    (xa, ya), (xb, yb) = points[-2], points[-1]
    dx, dy = (xb - xa), (yb - ya)
    n = max(abs(dx), abs(dy)) or 1
    ux, uy = dx / n, dy / n
    px, py = xb - ux * 11, yb - uy * 11
    for s in (-6, 0, 6):
        add('<path d="M%.1f,%.1f L%.1f,%.1f" stroke="%s" stroke-width="1.2"/>' % (px - uy * s, py + ux * s, xb, yb, LINE))

add('<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity="0.18"/></filter></defs>')
add('<rect width="%d" height="%d" fill="#fcfcfc"/>' % (W, H))

# relações (pai -> filho)
ra, rp = edge("areas", "r"), edge("processes", "l")
poly([(ra, row_y("areas", "id")), (345, row_y("areas", "id")), (345, row_y("processes", "area_id")), (rp, row_y("processes", "area_id"))])
poly([(edge("processes", "r"), row_y("processes", "id")), (740, row_y("processes", "id")), (740, row_y("activities", "process_id")), (edge("activities", "l"), row_y("activities", "process_id"))])
poly([(edge("documents", "r"), row_y("documents", "id")), (edge("document_processes", "l"), row_y("document_processes", "document_id"))])
px = 500
poly([(px, TABLES["processes"][1] + HEAD + ROW * 3), (px, TABLES["document_processes"][1])])
poly([(560, TABLES["document_processes"][1] + HEAD + ROW * 2), (560, TABLES["questions"][1])])
poly([(edge("questions", "r"), row_y("questions", "id")), (edge("question_options", "l"), row_y("question_options", "question_id"))])
poly([(edge("questions", "r"), row_y("questions", "id")), (765, row_y("questions", "id")), (765, row_y("question_flags", "question_id")), (edge("question_flags", "l"), row_y("question_flags", "question_id"))])

for t in TABLES:
    draw_table(t)

svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (W, H, W, H, "".join(parts))
os.makedirs(OUT, exist_ok=True)
sv = os.path.join(OUT, "der_banco_questoes.svg")
open(sv, "w", encoding="utf8").write(svg)
png = os.path.abspath(os.path.join(OUT, "db_banco_questoes_diagram.png"))
html = os.path.join(OUT, "_tmp.html")
open(html, "w", encoding="utf8").write('<html><body style="margin:0">%s</body></html>' % svg)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                "--window-size=%d,%d" % (W, H), "--screenshot=" + png, "file:///" + os.path.abspath(html).replace("\\", "/")],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.remove(html)
print("ok", png)
