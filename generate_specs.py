"""
Generate JuriTheque Technical Specifications PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.units import inch
import os

# ── Colors ────────────────────────────────────────────────────────────────────
NAVY      = colors.HexColor('#0f2044')
GOLD      = colors.HexColor('#c9a84c')
LIGHT_BG  = colors.HexColor('#f8fafc')
BORDER    = colors.HexColor('#e2e8f0')
TEXT_DARK = colors.HexColor('#1e293b')
TEXT_MED  = colors.HexColor('#475569')
CODE_BG   = colors.HexColor('#f1f5f9')
SUCCESS   = colors.HexColor('#15803d')

OUTPUT = r"C:\Users\HP\Desktop\Legal-website\lexbase\JuriTheque_Specifications_Techniques.pdf"

# ── Document setup ────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2.5*cm,
    bottomMargin=2*cm,
    title="JuriTheque — Specifications Techniques",
    author="JuriTheque Team",
    subject="Technical Stack Documentation",
)

W, H = A4
styles = getSampleStyleSheet()

# ── Custom styles ─────────────────────────────────────────────────────────────
def s(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title = s('CoverTitle',
    fontSize=32, textColor=colors.white, fontName='Helvetica-Bold',
    alignment=TA_CENTER, spaceAfter=8, leading=38)

cover_sub = s('CoverSub',
    fontSize=14, textColor=GOLD, fontName='Helvetica',
    alignment=TA_CENTER, spaceAfter=6, leading=18)

cover_date = s('CoverDate',
    fontSize=11, textColor=colors.HexColor('#94a3b8'),
    fontName='Helvetica', alignment=TA_CENTER)

h1 = s('H1',
    fontSize=18, textColor=NAVY, fontName='Helvetica-Bold',
    spaceBefore=18, spaceAfter=8, leading=22,
    borderPad=0)

h2 = s('H2',
    fontSize=13, textColor=NAVY, fontName='Helvetica-Bold',
    spaceBefore=14, spaceAfter=6, leading=17)

h3 = s('H3',
    fontSize=11, textColor=colors.HexColor('#1e40af'), fontName='Helvetica-Bold',
    spaceBefore=10, spaceAfter=4, leading=14)

body = s('Body',
    fontSize=10, textColor=TEXT_DARK, fontName='Helvetica',
    spaceBefore=3, spaceAfter=3, leading=15)

body_med = s('BodyMed',
    fontSize=10, textColor=TEXT_MED, fontName='Helvetica',
    spaceBefore=2, spaceAfter=2, leading=14)

bullet = s('Bullet',
    fontSize=10, textColor=TEXT_DARK, fontName='Helvetica',
    spaceBefore=2, spaceAfter=2, leading=14,
    leftIndent=16, bulletIndent=6)

code_style = s('Code',
    fontSize=9, textColor=colors.HexColor('#0f172a'), fontName='Courier',
    spaceBefore=2, spaceAfter=2, leading=13,
    leftIndent=12, backColor=CODE_BG)

badge_style = s('Badge',
    fontSize=9, textColor=colors.white, fontName='Helvetica-Bold',
    alignment=TA_CENTER)

toc_h1 = s('TOCH1',
    fontSize=11, textColor=NAVY, fontName='Helvetica-Bold',
    spaceBefore=6, spaceAfter=2, leading=14)

toc_h2 = s('TOCH2',
    fontSize=10, textColor=TEXT_MED, fontName='Helvetica',
    spaceBefore=2, spaceAfter=2, leading=13, leftIndent=14)

# ── Helper: section header with colored bar ────────────────────────────────────
def section_header(num, title, story):
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=6))
    story.append(Paragraph(f"{num}. {title}", h1))

def subsection(title, story):
    story.append(Paragraph(title, h2))

def sub2(title, story):
    story.append(Paragraph(title, h3))

def bul(text, story, symbol="•"):
    story.append(Paragraph(f"{symbol}  {text}", bullet))

def para(text, story):
    story.append(Paragraph(text, body))

def space(story, h=8):
    story.append(Spacer(1, h))

# ── Tech badge table ──────────────────────────────────────────────────────────
def tech_table(rows, story):
    """rows = list of (Technology, Version/Detail, Role)"""
    header = ['Technologie', 'Version', 'Rôle']
    data = [header] + rows
    col_w = [4.5*cm, 3*cm, 9*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('ALIGN',       (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 9),
        ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
        ('BACKGROUND',  (0,1), (-1,-1), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,0), (-1,0), [NAVY]),
    ]))
    story.append(t)
    space(story, 10)

def sources_table(rows, story):
    """Source stats table"""
    header = ['Source (--source)', 'Site Officiel', 'PDFs']
    data = [header] + rows
    col_w = [3.5*cm, 9.5*cm, 2.5*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('ALIGN',       (0,0), (0,-1), 'LEFT'),
        ('ALIGN',       (2,0), (2,-1), 'CENTER'),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 9),
        ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_BG]),
        ('BACKGROUND',  (0,-1), (-1,-1), colors.HexColor('#dbeafe')),
        ('FONTNAME',    (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (0,-1), (-1,-1), NAVY),
        ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    space(story, 10)

def kpi_table(rows, story):
    """Key metrics table"""
    header = ['Métrique', 'Valeur']
    data = [header] + rows
    col_w = [9*cm, 6.5*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 10),
        ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,1), (-1,-1), 10),
        ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
        ('FONTNAME',    (1,1), (1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR',   (1,1), (1,-1), SUCCESS),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
        ('ALIGN',       (1,0), (1,-1), 'CENTER'),
        ('TOPPADDING',  (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t)

def db_table(title, cols, rows, story):
    """Database schema table"""
    para(f"<b>Table «{title}»</b>", story)
    header = ['Colonne', 'Type', 'Description']
    data = [header] + rows
    col_w = [3.5*cm, 3.5*cm, 8.5*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0), 9),
        ('FONTNAME',    (0,1), (-1,-1), 'Courier'),
        ('FONTSIZE',    (0,1), (-1,-1), 8),
        ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#eff6ff')]),
        ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    space(story, 8)

# ── Page numbering ─────────────────────────────────────────────────────────────
def add_page_number(canvas, doc):
    if doc.page == 1:
        return  # no number on cover
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(TEXT_MED)
    # Footer line
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.5*cm, W - 2*cm, 1.5*cm)
    canvas.drawString(2*cm, 1.1*cm, "JuriTheque — Specifications Techniques")
    canvas.drawRightString(W - 2*cm, 1.1*cm, f"Page {doc.page}")
    canvas.restoreState()

# ══════════════════════════════════════════════════════════════════════════════
# BUILD STORY
# ══════════════════════════════════════════════════════════════════════════════
story = []

# ── COVER PAGE ────────────────────────────────────────────────────────────────
# Navy background rectangle (simulated with a table)
cover_data = [['']]
cover_bg = Table(cover_data, colWidths=[W - 4*cm], rowHeights=[H - 4*cm])
cover_bg.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), NAVY),
    ('GRID', (0,0), (-1,-1), 0, NAVY),
]))

# We'll use a colored table as visual separator instead
# Cover header bar
bar = Table([['']], colWidths=[W - 4*cm], rowHeights=[0.5*cm])
bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), GOLD)]))
story.append(bar)
space(story, 60)

# Logo / Title block
story.append(Paragraph("⚖", ParagraphStyle('Icon', fontSize=48, textColor=NAVY,
    alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')))
space(story, 10)
story.append(Paragraph("JuriThèque", ParagraphStyle('CT',
    fontSize=36, textColor=NAVY, fontName='Helvetica-Bold',
    alignment=TA_CENTER, spaceAfter=4, leading=40)))
story.append(Paragraph("Spécifications Techniques", ParagraphStyle('CS',
    fontSize=16, textColor=GOLD, fontName='Helvetica-Bold',
    alignment=TA_CENTER, spaceAfter=8)))
story.append(HRFlowable(width="60%", thickness=2, color=GOLD,
    hAlign='CENTER', spaceAfter=16, spaceBefore=8))
story.append(Paragraph("Plateforme de Base de Données Juridique Marocaine",
    ParagraphStyle('CSub', fontSize=13, textColor=TEXT_MED,
    fontName='Helvetica', alignment=TA_CENTER, spaceAfter=4)))
space(story, 40)

# Info block
info_data = [
    ['Projet', 'JuriTheque / LexBase'],
    ['Type', 'Application Web Full-Stack JAMstack'],
    ['Version', '1.0'],
    ['Date', 'Mai 2026'],
    ['Langues', 'Francais / Arabe (RTL)'],
    ['Hebergement', 'Hostinger (frontend) + Supabase (backend)'],
]
info_t = Table(info_data, colWidths=[4*cm, 11*cm])
info_t.setStyle(TableStyle([
    ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
    ('FONTSIZE',    (0,0), (-1,-1), 10),
    ('TEXTCOLOR',   (0,0), (0,-1), NAVY),
    ('TEXTCOLOR',   (1,0), (1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, colors.white]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 7),
    ('BOTTOMPADDING',(0,0), (-1,-1), 7),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
]))
story.append(info_t)
space(story, 30)
bar2 = Table([['']], colWidths=[W - 4*cm], rowHeights=[0.3*cm])
bar2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), GOLD)]))
story.append(bar2)

story.append(PageBreak())

# ── TABLE OF CONTENTS ─────────────────────────────────────────────────────────
story.append(Paragraph("Table des Matières", h1))
story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=12))
space(story, 4)

toc_entries = [
    ("1.", "Architecture Générale", "3"),
    ("2.", "Frontend — React / Vite / Tailwind", "3"),
    ("   2.1", "Technologies", "3"),
    ("   2.2", "Pages & Routing", "4"),
    ("   2.3", "Build & Déploiement", "4"),
    ("3.", "Backend — Supabase", "4"),
    ("   3.1", "Composants", "4"),
    ("   3.2", "Schéma Base de Données", "5"),
    ("   3.3", "Domaines & Migrations", "6"),
    ("4.", "Pipeline de Données (Python)", "6"),
    ("   4.1", "scraper.py — Collecte des PDFs", "6"),
    ("   4.2", "extract.py — Extraction & Insertion", "8"),
    ("5.", "Assistant IA", "8"),
    ("6.", "Sécurité & Authentification", "8"),
    ("7.", "Structure du Projet", "9"),
    ("8.", "Chiffres Clés", "9"),
]
for num, title, page in toc_entries:
    is_main = not num.strip().startswith('   ')
    style = toc_h1 if is_main else toc_h2
    dots = '.' * max(2, 60 - len(num) - len(title) - len(page))
    story.append(Paragraph(
        f"<b>{num}</b>  {title}  <font color='#94a3b8'>{dots}</font>  {page}",
        style))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Architecture
# ══════════════════════════════════════════════════════════════════════════════
section_header("1", "Architecture Générale", story)
para("Application <b>full-stack JAMstack</b> — frontend statique + backend serverless + pipeline de données Python autonome.", story)
space(story, 8)

arch_data = [
    ['Couche', 'Technologie', 'Hébergement', 'Rôle'],
    ['Frontend', 'React 18 + Vite', 'Hostinger', 'Interface utilisateur (SPA statique)'],
    ['Backend', 'Supabase (PostgreSQL)', 'Supabase Cloud EU', 'BDD + Auth + API REST + Storage'],
    ['Pipeline', 'Python 3.14', 'Local (exécution manuelle)', 'Scraping PDFs + extraction + insertion DB'],
    ['IA', 'Claude (Anthropic API)', 'Anthropic Cloud', 'Assistant juridique conversationnel'],
]
t = Table(arch_data, colWidths=[2.5*cm, 4*cm, 4.5*cm, 5.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Frontend
# ══════════════════════════════════════════════════════════════════════════════
section_header("2", "Frontend — React / Vite / Tailwind CSS", story)

subsection("2.1  Technologies", story)
tech_table([
    ['React', '18', 'Framework UI — Single Page Application (SPA)'],
    ['Vite', '5', 'Bundler ultra-rapide, build production optimise'],
    ['React Router DOM', 'v6', 'Navigation client-side, routes imbriquees'],
    ['Tailwind CSS', 'v3', 'Styling utility-first, responsive mobile-first'],
    ['Lucide React', 'latest', 'Bibliotheque d\'icones SVG (500+ icones)'],
], story)

subsection("2.2  Fonctionnalités Clés", story)
bul("<b>Internationalisation (i18n)</b> : Contexte LangContext — toggle FR/AR avec activation automatique du mode RTL (right-to-left)", story)
bul("<b>Authentification</b> : Contexte AuthContext — gestion JWT, login/logout, 3 niveaux de rôles", story)
bul("<b>Responsive</b> : Mobile-first, menu burger, grilles CSS adaptatives (sm/md/lg/xl)", story)
bul("<b>Thème</b> : Palette Navy + Gold, typographie Playfair Display (titres) + Arabic (textes AR)", story)
space(story, 8)

subsection("2.3  Pages & Routing", story)
pages_data = [
    ['Route', 'Page', 'Description'],
    ['/', 'HomePage', 'Hero animé, statistiques, grille domaines, CTA'],
    ['/base', 'BasePage', 'Recherche full-text, filtres domaine/type/langue'],
    ['/domaines', 'DomainesPage', 'Grille des 11 domaines avec cards colorees'],
    ['/domaine/:id', 'DomainePage', 'Detail d\'un domaine, liste des lois'],
    ['/assistant', 'AssistantPage', 'Chat IA Claude — questions juridiques'],
    ['/connexion', 'ConnexionPage', 'Login + Register avec Supabase Auth'],
    ['/profil', 'ProfilPage', 'Espace utilisateur, historique'],
    ['/admin', 'AdminPage', 'Back-office editeur/admin (CRUD lois)'],
    ['/videos', 'VideosPage', 'Ressources video juridiques'],
]
t = Table(pages_data, colWidths=[3.5*cm, 3.5*cm, 9.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
    ('FONTNAME',    (0,1), (1,-1), 'Courier'),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t)
space(story, 8)

subsection("2.4  Build & Déploiement", story)
bul("<b>Build</b> : <font face='Courier'>npm run build</font> → génère le dossier <font face='Courier'>dist/</font> (HTML + CSS + JS minifiés)", story)
bul("<b>Hébergement</b> : Hostinger — upload manuel du dossier <font face='Courier'>dist/</font> via File Manager", story)
bul("<b>Taille bundle</b> : ~571 KB JS (gzip: 156 KB) + 38 KB CSS", story)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Backend
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
section_header("3", "Backend — Supabase", story)

subsection("3.1  Composants Supabase", story)
tech_table([
    ['PostgreSQL', 'v15', 'Base de donnees relationnelle principale'],
    ['Supabase Auth', 'v2', 'JWT, email/password, sessions securisees'],
    ['PostgREST', 'auto', 'API REST auto-generee depuis le schema PostgreSQL'],
    ['Supabase JS SDK', 'v2', 'Client JavaScript pour le frontend React'],
    ['Supabase Storage', 'latest', 'Stockage fichiers (PDFs, assets)'],
    ['Row Level Security', 'natif PG', 'Controle d\'acces par ligne selon le role'],
], story)

subsection("3.2  Schéma de Base de Données", story)

db_table("laws", [], [
    ['id', 'UUID PK', 'Identifiant unique auto-genere'],
    ['number', 'TEXT', 'Numero de la loi (ex: "103-12", "2-15-426")'],
    ['title_fr', 'TEXT', 'Titre en francais (max 500 car.)'],
    ['title_ar', 'TEXT', 'Titre en arabe'],
    ['type', 'TEXT', 'Loi | Dahir | Decret | Arrete | Circulaire | Code'],
    ['status', 'TEXT', 'En vigueur | Abroge | Modifie'],
    ['date', 'DATE', 'Date de promulgation'],
    ['domain_id', 'TEXT FK', 'Reference vers domains.id'],
    ['language', 'TEXT', 'Francais | Arabe | Bilingue'],
    ['content_fr', 'TEXT', 'Texte integral extrait du PDF (francais)'],
    ['content_ar', 'TEXT', 'Texte integral extrait du PDF (arabe)'],
    ['tags', 'TEXT[]', 'Tableau de tags pour la recherche'],
    ['created_at', 'TIMESTAMPTZ', 'Date d\'insertion automatique'],
], story)

db_table("domains", [], [
    ['id', 'TEXT PK', 'Identifiant slug (ex: "civil", "penal")'],
    ['name_fr', 'TEXT', 'Nom en francais'],
    ['name_ar', 'TEXT', 'Nom en arabe'],
    ['icon', 'TEXT', 'Nom de l\'icone Lucide React'],
    ['law_count', 'INT', 'Compteur de lois (mis a jour par trigger)'],
    ['sub_domains', 'TEXT[]', 'Sous-categories du domaine'],
], story)

db_table("profiles", [], [
    ['id', 'UUID FK', 'Reference vers auth.users (Supabase Auth)'],
    ['name', 'TEXT', 'Nom d\'affichage de l\'utilisateur'],
    ['role', 'TEXT', 'user | editor | admin'],
], story)

subsection("3.3  Domaines Juridiques (11)", story)
domains_data = [
    ['civil', 'Droit Civil', 'Obligations, contrats, procedures civiles'],
    ['penal', 'Droit Penal', 'Code penal, procedure penale, infractions'],
    ['commercial', 'Droit Commercial', 'Code de commerce, societes, faillites'],
    ['administratif', 'Droit Administratif', 'Fonction publique, collectivites, mines'],
    ['travail', 'Droit du Travail', 'Code du travail, securite sociale'],
    ['fiscal', 'Droit Fiscal', 'CGI, TVA, douanes, fiscalite'],
    ['international', 'Droit International', 'Traites, conventions, accords bilateraux'],
    ['numerique', 'Droit Numerique', 'Telecom, cybersecurite, donnees personnelles'],
    ['constitutionnel', 'Droit Constitutionnel', 'Constitution, lois organiques'],
    ['bancaire', 'Droit Bancaire', 'Loi bancaire, circulaires BAM, microfinance'],
    ['finances_publiques', 'Finances Publiques', 'LOF, lois de finances, marches publics'],
]
t = Table([['ID', 'Domaine FR', 'Couverture']] + domains_data,
          colWidths=[3.5*cm, 4.5*cm, 8.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('FONTNAME',    (0,1), (0,-1), 'Courier'),
    ('FONTNAME',    (1,1), (-1,-1), 'Helvetica'),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 4),
    ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t)
space(story, 6)

subsection("3.4  Migrations SQL", story)
mig_data = [
    ['Fichier', 'Contenu'],
    ['001_initial_schema.sql', 'Création tables laws, domains, profiles + index'],
    ['002_profiles.sql', 'Trigger auto-création profil à l\'inscription'],
    ['003_domains_seed.sql', 'Insertion des 9 domaines initiaux'],
    ['004_storage.sql', 'Configuration Supabase Storage + RLS buckets'],
    ['005_new_domains.sql', 'Ajout domaines bancaire + finances_publiques'],
]
t = Table(mig_data, colWidths=[6*cm, 10.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('FONTNAME',    (0,1), (0,-1), 'Courier'),
    ('FONTNAME',    (1,1), (-1,-1), 'Helvetica'),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#eff6ff')]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Pipeline Python
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
section_header("4", "Pipeline de Données (Python)", story)
para("Pipeline local autonome en ligne de commande : téléchargement des PDFs depuis les sources officielles, extraction du texte, et insertion dans Supabase.", story)
space(story, 8)

subsection("4.1  scraper.py — Collecte des PDFs", story)
tech_table([
    ['Python', '3.14', 'Langage du pipeline'],
    ['requests', 'latest', 'Telechargement HTTP des PDFs (avec retry/timeout)'],
    ['httpx', 'latest', 'Requetes HTTP async vers l\'API Supabase'],
    ['beautifulsoup4 + lxml', 'latest', 'Parsing HTML pour scraping dynamique'],
    ['rich', 'latest', 'Interface CLI coloree avec progress bars'],
    ['python-dotenv', 'latest', 'Chargement des variables d\'environnement .env'],
], story)

para("<b>Mode CLI :</b>", story)
bul("<font face='Courier'>--source &lt;nom&gt;</font> : choisir la source à télécharger", story)
bul("<font face='Courier'>--limit N</font> : limiter le nombre de PDFs", story)
bul("<font face='Courier'>--dry-run</font> : prévisualiser sans télécharger", story)
bul("<font face='Courier'>--year YYYY</font> : filtrer par année", story)
space(story, 8)

para("<b>11 sources configurées — 696 PDFs :</b>", story)
space(story, 4)
sources_table([
    ['sgg', 'sgg.gov.ma — Textes consolidés officiels', '63'],
    ['sgg-lois', 'sgg.gov.ma — Lois organiques, lois-cadres, décrets', '73'],
    ['mmsp', 'mmsp.gov.ma — Fonction publique, statuts', '47'],
    ['anrt', 'anrt.ma — Télécommunications & numérique', '32'],
    ['bkam', 'bkam.ma — Réglementation bancaire (Bank Al-Maghrib)', '67'],
    ['finances', 'lof.finances.gov.ma + mef + dgi + cdr', '67'],
    ['cdr', 'chambredesrepresentants.ma — Projets de loi', '27'],
    ['mem', 'mem.gov.ma — Énergie, mines, hydrocarbures, EnR', '89'],
    ['environnement', 'environnement.gov.ma — Déchets, air, littoral, EIE', '53'],
    ['wipo', 'WIPO Lex + UNODC + Maroclear — PI, codes', '18'],
    ['ism', 'ism.ma — Institut Sup. Magistrature (13 domaines, arabe)', '160'],
    ['TOTAL', '', '696'],
], story)

subsection("4.2  extract.py — Extraction & Insertion", story)
tech_table([
    ['PyMuPDF (fitz)', 'latest', 'Extraction texte depuis PDFs natifs (vectoriels)'],
    ['pytesseract', 'latest', 'OCR pour PDFs scannes (images)'],
    ['pdf2image', 'latest', 'Conversion PDF -> images pour OCR'],
    ['re (regex)', 'stdlib', 'Nettoyage texte, extraction numero de loi, date'],
    ['httpx', 'latest', 'Insertion Supabase via REST API (PostgREST)'],
], story)

para("<b>Étapes du pipeline extract.py :</b>", story)
steps = [
    ("1", "Scan du dossier pdfs/", "Détecte tous les fichiers .pdf téléchargés"),
    ("2", "Lecture PDF", "PyMuPDF extrait le texte page par page"),
    ("3", "OCR si vide", "Si texte < 100 chars → pytesseract sur image"),
    ("4", "Nettoyage", "Regex normalise espaces, sauts de ligne, caractères spéciaux"),
    ("5", "Detection", "detect_domain() + detect_type() par règles lexicales"),
    ("6", "Déduplication", "Vérifie si le numéro de loi existe déjà en DB"),
    ("7", "Insertion", "POST vers Supabase REST API avec upsert"),
]
steps_data = [['Etape', 'Action', 'Detail']] + steps
t = Table(steps_data, colWidths=[1.5*cm, 4*cm, 11*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('FONTNAME',    (0,1), (-1,-1), 'Helvetica'),
    ('FONTNAME',    (0,1), (0,-1), 'Helvetica-Bold'),
    ('TEXTCOLOR',   (0,1), (0,-1), GOLD),
    ('ALIGN',       (0,0), (0,-1), 'CENTER'),
    ('TEXTCOLOR',   (1,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Assistant IA
# ══════════════════════════════════════════════════════════════════════════════
story.append(PageBreak())
section_header("5", "Assistant IA", story)
tech_table([
    ['Claude (Anthropic)', 'API', 'Modele de langage pour reponses juridiques'],
    ['React Chat UI', 'custom', 'Interface conversationnelle page /assistant'],
    ['Streaming', 'SSE', 'Reponses en temps reel (Server-Sent Events)'],
], story)
bul("<b>Rôle</b> : Répondre aux questions juridiques sur le droit marocain en FR et AR", story)
bul("<b>Contexte</b> : Peut consulter les textes de loi extraits de la base de données", story)
bul("<b>Accès</b> : Page <font face='Courier'>/assistant</font> — disponible pour les utilisateurs connectés", story)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Sécurité
# ══════════════════════════════════════════════════════════════════════════════
section_header("6", "Sécurité & Authentification", story)

subsection("6.1  Système d'authentification", story)
bul("<b>JWT (JSON Web Token)</b> via Supabase Auth — expiration automatique + refresh token", story)
bul("<b>3 niveaux de rôles</b> :", story)

roles_data = [
    ['Rôle', 'Permissions'],
    ['user', 'Lecture de la base de données, recherche, consultation'],
    ['editor', 'CRUD sur les lois (créer, modifier, supprimer des textes)'],
    ['admin', 'Accès complet : gestion utilisateurs + toutes permissions editor'],
]
t = Table(roles_data, colWidths=[3*cm, 13.5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',    (0,1), (0,-1), 'Courier'),
    ('FONTNAME',    (1,1), (1,-1), 'Helvetica'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 6),
    ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
]))
story.append(t)
space(story, 8)

subsection("6.2  Row Level Security (RLS)", story)
bul("Activé sur toutes les tables PostgreSQL (laws, domains, profiles)", story)
bul("Les utilisateurs non connectés peuvent uniquement lire les lois publiques", story)
bul("Les editors/admins ont accès aux opérations d'écriture via policies RLS", story)
space(story, 6)

subsection("6.3  Variables d'Environnement", story)
env_data = [
    ['Variable', 'Usage', 'Exposée ?'],
    ['VITE_SUPABASE_URL', 'URL du projet Supabase', 'Frontend (build)'],
    ['VITE_SUPABASE_ANON_KEY', 'Clé publique Supabase (lecture)', 'Frontend (build)'],
    ['SUPABASE_SERVICE_KEY', 'Clé service (écriture admin)', 'Pipeline Python UNIQUEMENT'],
    ['VITE_CLAUDE_API_KEY', 'Clé API Anthropic pour l\'IA', 'Frontend (build)'],
]
t = Table(env_data, colWidths=[5*cm, 6.5*cm, 5*cm])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',    (0,1), (0,-1), 'Courier'),
    ('FONTNAME',    (1,1), (-1,-1), 'Helvetica'),
    ('FONTSIZE',    (0,0), (-1,-1), 9),
    ('TEXTCOLOR',   (0,1), (-1,-1), TEXT_DARK),
    ('BACKGROUND',  (2,4), (2,4), colors.HexColor('#fef2f2')),
    ('TEXTCOLOR',   (2,4), (2,4), colors.HexColor('#dc2626')),
    ('FONTNAME',    (2,4), (2,4), 'Helvetica-Bold'),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
    ('GRID',        (0,0), (-1,-1), 0.5, BORDER),
    ('TOPPADDING',  (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
]))
story.append(t)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Structure Projet
# ══════════════════════════════════════════════════════════════════════════════
section_header("7", "Structure du Projet", story)
para("Organisation du dépôt :", story)
space(story, 4)

struct = [
    "lexbase/",
    "├── src/",
    "│   ├── components/       # Navbar, DomainCard, LawCard, SearchBar...",
    "│   ├── contexts/         # AuthContext.jsx, LangContext.jsx",
    "│   ├── pages/            # HomePage, BasePage, DomainesPage...",
    "│   ├── data/             # mockData.js (données fallback)",
    "│   └── main.jsx          # Point d'entrée React",
    "├── pipeline/",
    "│   ├── scraper.py        # Collecte PDFs (11 sources, 696 PDFs)",
    "│   ├── extract.py        # Extraction texte + insertion Supabase",
    "│   └── pdfs/             # PDFs téléchargés (dossier local)",
    "├── supabase/",
    "│   └── migrations/       # 001 à 005 — scripts SQL",
    "├── dist/                 # Build production (upload → Hostinger)",
    "├── .env                  # Variables d'environnement (non versionné)",
    "├── vite.config.js        # Configuration Vite + proxy",
    "├── tailwind.config.js    # Configuration Tailwind CSS",
    "└── package.json          # Dépendances npm",
]
for line in struct:
    story.append(Paragraph(line, code_style))
space(story, 6)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Chiffres Clés
# ══════════════════════════════════════════════════════════════════════════════
section_header("8", "Chiffres Clés", story)
space(story, 4)
kpi_table([
    ['Sources officelles cataloguees', '11 sites gouvernementaux + internationaux'],
    ['PDFs references dans le scraper', '696 PDFs'],
    ['Domaines juridiques couverts', '11'],
    ['Pages frontend (React Router)', '10+'],
    ['Migrations base de donnees', '5 fichiers SQL'],
    ['Langues supportees', '2 (Francais + Arabe avec RTL)'],
    ['Hebergement frontend', 'Hostinger (hébergement partagé)'],
    ['Hebergement backend', 'Supabase Cloud (région EU)'],
    ['Modele IA', 'Claude (Anthropic API)'],
    ['Taille bundle JS (gzip)', '~156 KB'],
], story)

space(story, 20)
story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
story.append(Paragraph(
    "Document généré automatiquement — JuriThèque © 2026",
    ParagraphStyle('Footer', fontSize=9, textColor=TEXT_MED,
                   alignment=TA_CENTER, fontName='Helvetica')))

# ══════════════════════════════════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════════════════════════════════
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"PDF generated: {OUTPUT}")
