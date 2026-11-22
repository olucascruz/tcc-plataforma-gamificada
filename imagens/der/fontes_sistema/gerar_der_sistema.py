"""Gera o DER resumido do banco do sistema gamificado (11 tabelas de domínio) em SVG e PNG (Chrome headless).
Resumido: cada tabela mostra só as chaves e os campos que a identificam; o detalhamento completo
(todos os campos, tipos e restrições) está no Dicionário de Dados do TCC.
Linha contínua = chave estrangeira real; linha tracejada = relação lógica (sem FK no esquema).
Uso: python gerar_der_sistema.py <pasta_de_saida>"""
import os, subprocess, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
W, H = 1060, 860
HEAD, ROW, TW = 40, 36, 260
XA, XB, XC = 40, 400, 760
BLUE, BODY, LINE = "#2f6697", "#f3f3f3", "#7a7a7a"
FONT = "Segoe UI, Arial, sans-serif"

TABLES = {
    "participants": (XA, 40, [("id", "PK"), ("name", ""), ("total_xp", "")]),
    "participant_badges": (XA, 260, [("participant_id", "PK FK"), ("badge_id", "PK FK")]),
    "badges": (XA, 444, [("id", "PK"), ("name", "")]),
    "user_roles": (XA, 628, [("email", "PK"), ("role", "")]),
    "results": (XB, 40, [("id", "PK"), ("avaliacao_id", "lógica"), ("participant_id", "lógica"), ("score", "")]),
    "participant_answers": (XB, 296, [("id", "PK"), ("result_id", "FK"), ("question_id", "FK"), ("selected_option_id", "FK")]),
    "question_options": (XB, 552, [("id", "PK"), ("question_id", "FK"), ("is_correct", "")]),
    "turmas": (XC, 40, [("id", "PK"), ("name", ""), ("code", "UQ")]),
    "turma_avaliacoes": (XC, 260, [("turma_id", "PK FK"), ("avaliacao_id", "PK FK")]),
    "avaliacoes": (XC, 444, [("id", "PK"), ("title", ""), ("pass_mark", "")]),
    "questions": (XC, 664, [("id", "PK"), ("avaliacao_id", "FK"), ("text", "")]),
}

parts = []
def add(s): parts.append(s)

def ry(t, f):
    x, y, fields = TABLES[t]
    return y + HEAD + [c[0] for c in fields].index(f) * ROW + ROW / 2

def left(t): return TABLES[t][0]
def right(t): return TABLES[t][0] + TW
def top(t): return TABLES[t][1]
def bottom(t): return TABLES[t][1] + HEAD + ROW * len(TABLES[t][2])

def draw_table(name):
    x, y, fields = TABLES[name]
    h = HEAD + ROW * len(fields)
    add('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="#c8c8c8" filter="url(#sh)"/>' % (x, y, TW, h, BODY))
    add('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s"/>' % (x, y, TW, HEAD, BLUE))
    add('<rect x="%d" y="%d" width="%d" height="6" fill="%s"/>' % (x, y + HEAD - 6, TW, BLUE))
    add('<text x="%d" y="%d" font-family="%s" font-size="19" font-weight="bold" fill="#fff">%s</text>' % (x + 14, y + 27, FONT, escape(name)))
    for i, (fname, key) in enumerate(fields):
        cy = y + HEAD + i * ROW + ROW / 2
        add('<text x="%d" y="%.1f" font-family="%s" font-size="18" font-weight="%s" fill="#1e1e1e">%s</text>'
            % (x + 14, cy + 6, FONT, "bold" if "PK" in key else "normal", escape(fname)))
        if key:
            add('<text x="%d" y="%.1f" font-family="%s" font-size="13" font-weight="bold" fill="%s" text-anchor="end">%s</text>'
                % (x + TW - 14, cy + 5, FONT, BLUE, escape(key)))

def poly(points, dashed=False):
    """Linha do pai (barra no início) para o filho (pé de galinha no fim)."""
    d = "M" + " L".join("%.1f,%.1f" % p for p in points)
    add('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" %s/>' % (d, LINE, 'stroke-dasharray="8 5"' if dashed else ""))
    (x0, y0), (x1, y1) = points[0], points[1]
    n = max(abs(x1 - x0), abs(y1 - y0)) or 1
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    bx, by = x0 + ux * 10, y0 + uy * 10
    add('<path d="M%.1f,%.1f l%.1f,%.1f" stroke="%s" stroke-width="1.6"/>' % (bx - uy * 7, by + ux * 7, uy * 14, -ux * 14, LINE))
    (xa, ya), (xb, yb) = points[-2], points[-1]
    n = max(abs(xb - xa), abs(yb - ya)) or 1
    ux, uy = (xb - xa) / n, (yb - ya) / n
    px, py = xb - ux * 14, yb - uy * 14
    for s in (-8, 0, 8):
        add('<path d="M%.1f,%.1f L%.1f,%.1f" stroke="%s" stroke-width="1.6"/>' % (px - uy * s, py + ux * s, xb, yb, LINE))

add('<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity="0.18"/></filter></defs>')
add('<rect width="%d" height="%d" fill="#fcfcfc"/>' % (W, H))

# --- chaves estrangeiras reais ---
poly([(830, bottom("turmas")), (830, top("turma_avaliacoes"))])                 # turmas 1:N turma_avaliacoes
poly([(950, top("avaliacoes")), (950, bottom("turma_avaliacoes"))])             # avaliacoes 1:N turma_avaliacoes
poly([(890, bottom("avaliacoes")), (890, top("questions"))])                    # avaliacoes 1:N questions
poly([(left("questions"), ry("questions", "id")), (720, ry("questions", "id")),
      (720, ry("participant_answers", "question_id")), (right("participant_answers"), ry("participant_answers", "question_id"))])
poly([(left("questions"), ry("questions", "id")), (700, ry("questions", "id")),
      (700, ry("question_options", "question_id")), (right("question_options"), ry("question_options", "question_id"))])
poly([(530, top("question_options")), (530, bottom("participant_answers"))])    # question_options 1:N participant_answers
poly([(530, bottom("results")), (530, top("participant_answers"))])            # results 1:N participant_answers
poly([(170, bottom("participants")), (170, top("participant_badges"))])
poly([(170, top("badges")), (170, bottom("participant_badges"))])

# --- relações lógicas (sem FK no esquema) ---
poly([(left("avaliacoes"), ry("avaliacoes", "id")), (740, ry("avaliacoes", "id")),
      (740, ry("results", "avaliacao_id")), (right("results"), ry("results", "avaliacao_id"))], dashed=True)
poly([(right("participants"), ry("participants", "id")), (350, ry("participants", "id")),
      (350, ry("results", "participant_id")), (left("results"), ry("results", "participant_id"))], dashed=True)

for t in TABLES:
    draw_table(t)

# legenda
lx, ly = XB, 740
add('<rect x="%d" y="%d" width="%d" height="96" rx="4" fill="#fff" stroke="#c8c8c8"/>' % (lx, ly, TW))
add('<text x="%d" y="%d" font-family="%s" font-size="16" font-weight="bold" fill="#222">Legenda</text>' % (lx + 14, ly + 25, FONT))
add('<path d="M%d,%d h40" stroke="%s" stroke-width="1.8"/>' % (lx + 14, ly + 51, LINE))
add('<text x="%d" y="%d" font-family="%s" font-size="15" fill="#222">chave estrangeira</text>' % (lx + 64, ly + 56, FONT))
add('<path d="M%d,%d h40" stroke="%s" stroke-width="1.8" stroke-dasharray="8 5"/>' % (lx + 14, ly + 77, LINE))
add('<text x="%d" y="%d" font-family="%s" font-size="15" fill="#222">relação lógica (sem FK)</text>' % (lx + 64, ly + 82, FONT))

svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (W, H, W, H, "".join(parts))
os.makedirs(OUT, exist_ok=True)
sv = os.path.join(OUT, "der_sistema_gamificado.svg")
open(sv, "w", encoding="utf8").write(svg)
png = os.path.abspath(os.path.join(OUT, "db_sistema_gamificado_diagram.png"))
html = os.path.join(OUT, "_tmp.html")
open(html, "w", encoding="utf8").write('<html><body style="margin:0">%s</body></html>' % svg)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                "--window-size=%d,%d" % (W, H), "--screenshot=" + png, "file:///" + os.path.abspath(html).replace("\\", "/")],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.remove(html)
print("ok", png)
