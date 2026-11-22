import textwrap, subprocess, os, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"
C_PERSON, C_SYS, C_EXT, C_DB, C_BOUND, C_BSTROKE = "#08427B", "#1168BD", "#8C8496", "#23A2D9", "#FFF2CC", "#D6B656"


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(
            '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker></defs>')

    def text(self, cx, y, s, size=12, bold=False, color="#fff", anchor="middle"):
        self.parts.append('<text x="%s" y="%s" font-family="Arial, Helvetica, sans-serif" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s">%s</text>'
                          % (cx, y, size, "bold" if bold else "normal", color, anchor, escape(s)))

    def block(self, cx, top, title, tech, desc, w, size=12, color="#fff", title_size=16):
        y = top + title_size
        self.text(cx, y, title, title_size, True, color)
        y += size + 6
        if tech:
            self.text(cx, y, tech, size, False, color); y += size + 8
        if desc:
            n = max(10, int(w / (size * 0.52)))
            for line in textwrap.wrap(desc, n):
                self.text(cx, y, line, size, False, color); y += size + 3
        return y

    def box(self, x, y, w, h, title, tech, desc, fill, rx=12, title_size=16):
        self.parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="#0B3E75" stroke-width="1"/>' % (x, y, w, h, rx, fill))
        self.block(x + w / 2, y + 14, title, tech, desc, w - 24, title_size=title_size)

    def person(self, x, y, w, h, title, desc):
        self.parts.append('<circle cx="%s" cy="%s" r="34" fill="%s"/>' % (x + w / 2, y + 34, C_PERSON))
        self.parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="38" fill="%s"/>' % (x, y + 58, w, h - 58, C_PERSON))
        self.block(x + w / 2, y + 70, title, "[Usuário]", desc, w - 30)

    def db(self, x, y, w, h, title, tech, desc):
        ry = 16
        self.parts.append('<path d="M%s,%s v%s a%s,%s 0 0 0 %s,0 v-%s" fill="%s" stroke="#0E6E9A"/>' % (x, y + ry, h - 2 * ry, w / 2, ry, w, h - 2 * ry, C_DB))
        self.parts.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="#0E6E9A"/>' % (x + w / 2, y + ry, w / 2, ry, C_DB))
        self.block(x + w / 2, y + ry + 18, title, tech, desc, w - 30)

    def boundary(self, x, y, w, h, label, fill=C_BOUND, stroke=C_BSTROKE, anchor="middle", bottom=False):
        self.parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="26" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, w, h, fill, stroke))
        tx = {"middle": x + w / 2, "start": x + 22, "end": x + w - 22}[anchor]
        self.text(tx, (y + h - 16) if bottom else (y + 26), label, 16, True, "#222", anchor)

    def arrow(self, pts, label=None, lx=None, ly=None, both=False, lw=150, dashed=False):
        d = "M" + " L".join("%s,%s" % p for p in pts)
        self.parts.append('<path d="%s" fill="none" stroke="#222" stroke-width="1.4" %s marker-end="url(#a)" %s/>'
                          % (d, 'stroke-dasharray="6 4"' if dashed else "", 'marker-start="url(#a)"' if both else ""))
        if label:
            lines = textwrap.wrap(label, max(8, int(lw / 6.4)))
            if lx is None:
                a, b = pts[0], pts[1]; lx, ly = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            hh = 15 * len(lines) + 6; ww = max(len(l) for l in lines) * 6.3 + 12
            self.parts.append('<rect x="%s" y="%s" width="%s" height="%s" fill="#fff" fill-opacity="0.95" stroke="#bbb" stroke-width="0.6"/>' % (lx - ww / 2, ly - hh / 2, ww, hh))
            for i, l in enumerate(lines):
                self.text(lx, ly - hh / 2 + 15 * (i + 1) - 1, l, 11.5, False, "#111")

    def save(self, name):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s"><rect width="100%%" height="100%%" fill="#fff"/>%s</svg>'
               % (self.w, self.h, self.w, self.h, "".join(self.parts)))
        p = os.path.join(OUT, name + ".svg")
        open(p, "w", encoding="utf8").write(svg)
        png = os.path.join(OUT, name + ".png")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--window-size=%d,%d" % (self.w, self.h), "--screenshot=" + png, "file:///" + p.replace("\\", "/")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        print(name, os.path.exists(png))


# ---------------- Nível 1: contexto ----------------
s = Svg(1020, 760)
s.person(40, 20, 290, 150, "Trainee", "Colaborador em capacitação")
s.person(340, 20, 290, 150, "Instrutor", "Cria avaliações, gerencia turmas e acompanha o desempenho")
s.box(100, 270, 440, 110, "Sistema gamificado", "[Software System]", "Plataforma de avaliação gamificada", C_SYS)
s.box(640, 270, 280, 110, "Pipeline de geração de questões", "[Software System]", "Gera questões a partir dos documentos e as mantém atualizadas por rotina semanal", C_SYS)
s.box(40, 580, 260, 135, "SSO", "[Software System]", "Dosso, autenticação corporativa sobre o Microsoft Entra ID", C_EXT)
s.box(360, 580, 360, 135, "Databricks", "[Software System]", "Plataforma de dados e IA: banco da aplicação (Lakebase), banco de questões (Delta), revisões dos documentos e modelos de IA (AI Gateway)", C_EXT)
s.box(760, 580, 220, 135, "SoftExpert", "[Software System]", "Gestão de documentos e procedimentos corporativos", C_EXT)
# legenda (canto superior direito, antes vazio)
s.parts.append('<rect x="700" y="40" width="280" height="96" rx="6" fill="#fff" stroke="#bbb" stroke-width="0.8"/>')
s.text(840, 60, "Legenda", 12, True, "#222")
for i, (cor, rot) in enumerate([(C_PERSON, "Usuário"), (C_SYS, "Sistema desenvolvido neste trabalho"), (C_EXT, "Sistema externo (corporativo)")]):
    s.parts.append('<rect x="716" y="%s" width="18" height="14" rx="3" fill="%s"/>' % (72 + i * 20, cor))
    s.text(742, 84 + i * 20, rot, 11.5, False, "#222", "start")
s.arrow([(185, 170), (185, 270)], "Realiza avaliações e acompanha o desempenho via HTTPS", 185, 222, lw=170)
s.arrow([(485, 170), (485, 270)], "Seleciona e revisa questões do banco, cria avaliações e visualiza relatórios via HTTPS", 485, 222, lw=190)
s.arrow([(200, 380), (200, 580)], "Autentica usuários via HTTPS", 200, 480, lw=130)
s.arrow([(440, 380), (440, 580)], "Lê e grava dados (questões, avaliações, resultados) via protocolo PostgreSQL", 440, 480, lw=160)
s.arrow([(680, 380), (680, 580)], "Consulta revisões e grava/inativa questões via API SQL (HTTPS); gera e revisa questões com IA via HTTPS", 680, 480, lw=190)
s.arrow([(880, 380), (880, 580)], "Baixa os documentos (PDF) via HTTPS", 880, 480, lw=130)
s.save("nivel1_cmodel_v2")

# ---------------- Nível 2: contêineres ----------------
s = Svg(1240, 910)
s.person(35, 20, 190, 150, "Trainee", "Realiza avaliações e participa da gamificação")
s.person(235, 20, 190, 150, "Instrutor", "Seleciona questões e acompanha métricas")
s.boundary(20, 215, 360, 400, "Sistema gamificado", bottom=True)
s.box(50, 275, 300, 100, "Frontend", "[Container: React 18, TypeScript, Vite]", "Interface web (SPA) para trainees e instrutores", C_SYS)
s.box(50, 455, 300, 100, "Backend API", "[Container: FastAPI, Python 3.12+]", "Regras de negócio, XP, ranking e seleção de questões", C_SYS)
s.box(410, 455, 190, 100, "Serviço de SSO", "[Software System]", "Dosso (Microsoft Entra ID)", C_EXT)
s.boundary(640, 215, 300, 400, "Pipeline de geração de questões")
s.box(660, 275, 260, 100, "Rotina semanal", "[Container: Python]", "Detecta documentos com revisão nova, aciona a geração e atualiza os bancos", C_SYS)
s.box(660, 435, 260, 130, "Pipelines de geração (P1, P2, P3)", "[Container: Python]", "Extraem o texto, geram, revisam e validam as questões e montam o banco", C_SYS)
s.box(1010, 275, 200, 100, "SoftExpert", "[Software System]", "Documentos e procedimentos corporativos", C_EXT)
s.boundary(300, 690, 910, 195, "Databricks", fill="#ECEAF0", stroke="#8C8496", anchor="start")
s.db(320, 735, 250, 140, "Banco da aplicação", "[Container: PostgreSQL (Lakebase)]", "Avaliações, resultados, gamificação e cópia das questões ativas")
s.db(610, 735, 270, 140, "Banco de questões", "[Container: tabelas Delta]", "Questões, alternativas e avisos; revisão vigente de cada documento")
s.box(910, 740, 280, 100, "AI Gateway", "[Container: modelos de IA (LLMs)]", "Acesso governado aos modelos Claude", C_EXT)
s.arrow([(130, 170), (130, 275)], "HTTPS", 130, 205)
s.arrow([(330, 170), (330, 275)], "HTTPS", 330, 205)
s.arrow([(190, 375), (190, 455)], "HTTPS", 190, 415)
s.arrow([(350, 505), (410, 505)], "HTTPS", 380, 482)
s.arrow([(110, 555), (110, 805), (320, 805)], "Lê e grava via protocolo PostgreSQL", 215, 805, lw=120)
s.arrow([(660, 310), (600, 310), (600, 668), (480, 668), (480, 735)], "copia as questões ativas via protocolo PostgreSQL", 512, 662, lw=175)
s.arrow([(660, 350), (625, 350), (625, 705), (700, 705), (700, 735)], "consulta a revisão via API SQL (HTTPS)", 668, 705, lw=125)
s.arrow([(790, 375), (790, 435)], "aciona a geração", 790, 405, lw=100)
s.box(1010, 465, 200, 110, "Modelos locais", "[Software System]", "Modelos abertos executados localmente (P3 e P1)", C_EXT)
s.arrow([(920, 325), (1010, 325)], "baixa o PDF via HTTPS", 965, 300, lw=90)
s.arrow([(920, 520), (1010, 520)], "gera (P3 e P1)", 965, 498, lw=80)
s.arrow([(900, 565), (900, 700), (1050, 700), (1050, 740)], "gera e revisa (P2), avalia e corrige (P1) via HTTPS", 975, 700, lw=170)
s.arrow([(780, 565), (780, 640), (830, 640), (830, 735)], "grava e aposenta questões via API SQL (HTTPS)", 820, 610, lw=130)
s.save("nivel2_cmodel_v2")

# ---------------- Nível 3: componentes do backend ----------------
s = Svg(1250, 920)
s.box(520, 8, 210, 46, "Frontend SPA", "", "", C_SYS, rx=4, title_size=14)
s.boundary(20, 80, 1210, 690, "Backend API (FastAPI)", fill="#FFFFE0", stroke="#B8B84C", anchor="start")
def layer(y, h, label):
    s.parts.append('<rect x="40" y="%s" width="1170" height="%s" rx="8" fill="#FFFFF0" stroke="#B8B84C" stroke-dasharray="4 3"/>' % (y, h))
    s.text(625, y + 18, label, 13, True, "#444")
COMP = "#2F7A89"
layer(115, 130, "Camada de rotas (main.py e dependências)")
s.box(60, 140, 720, 95, "Routers", "", "Rotas de autenticação, instrutores, avaliações, resultados, participantes, turmas, ranking e análises", COMP, rx=4, title_size=14)
s.box(820, 140, 350, 95, "Dependências de autenticação", "", "Autenticação e autorização por papel (instrutor e aluno)", COMP, rx=4, title_size=14)
layer(290, 130, "Camada de serviços (regras de negócio)")
names = [("turma_service", ""), ("gamification_service", "XP, níveis e conquistas"), ("analytics_service", "engajamento e lacunas"), ("avaliacao_service", "avaliações e questões"),
         ("result_service", "envio e nota"), ("participant_service", ""), ("instrutor_service", ""), ("auth_service", "papéis")]
for i, (n, d) in enumerate(names):
    s.box(55 + i * 145, 325, 135, 80, n, "", d, COMP, rx=4, title_size=12)
layer(465, 105, "Camada de repositórios (acesso a dados)")
for i, n in enumerate(["turma_repo", "result_repo", "avaliacao_repo", "participant_repo", "user_repo"]):
    s.box(75 + i * 225, 497, 190, 55, n, "", "", COMP, rx=4, title_size=13)
layer(615, 140, "Infraestrutura de dados")
s.box(120, 645, 420, 90, "models.py", "", "Participant, UserRole, Avaliacao, Question, QuestionOption, Result, ParticipantAnswer, Turma, TurmaAvaliacao, Badge", COMP, rx=4, title_size=14)
s.box(620, 645, 240, 90, "schemas.py", "", "DTOs Pydantic v2", COMP, rx=4, title_size=14)
s.box(940, 645, 240, 90, "database.py", "", "engine, sessão e seed", COMP, rx=4, title_size=14)
s.db(465, 800, 320, 100, "Banco de Dados", "[Databricks Lakebase, PostgreSQL]", "")
s.arrow([(625, 54), (625, 115)], "REST / JSON", 625, 66, lw=100)
s.arrow([(625, 245), (625, 290)], "delegam", 625, 268, lw=70)
s.arrow([(625, 420), (625, 465)], "acessam dados por meio de", 625, 443, lw=160)
s.arrow([(625, 570), (625, 615)], "queries SQLAlchemy", 625, 592, lw=140)
s.arrow([(625, 755), (625, 815)], "protocolo PostgreSQL", 625, 785, lw=140)
s.save("nivel3_cmodel_v2")
