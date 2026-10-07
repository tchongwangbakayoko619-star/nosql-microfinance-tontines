import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

DARK_BLUE = RGBColor(15, 32, 67)
LIGHT_BG = RGBColor(245, 247, 250)
WHITE = RGBColor(255, 255, 255)
TEAL_ACCENT = RGBColor(0, 150, 136)
TEXT_DARK = RGBColor(30, 41, 59)
TEXT_MUTED = RGBColor(100, 116, 139)
CARD_BG = RGBColor(255, 255, 255)
BORDER_COLOR = RGBColor(226, 232, 240)
PLACEHOLDER_BG = RGBColor(241, 245, 249)
PLACEHOLDER_BORDER = RGBColor(203, 213, 225)

def add_header(slide, title_text, category_text="PROJET 9 - MICROFINANCE ET TONTINES"):
    # Header container
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = TEAL_ACCENT
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = DARK_BLUE

def add_placeholder_box(slide, left, top, width, height, title, subtitle):
    # Outer box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = PLACEHOLDER_BG
    shape.line.color.rgb = PLACEHOLDER_BORDER
    shape.line.width = Pt(1.5)
    
    # Text inside box
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.4)
    
    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    p0.text = "📷 " + title
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = DARK_BLUE
    
    p1 = tf.add_paragraph()
    p1.alignment = PP_ALIGN.CENTER
    p1.text = subtitle
    p1.font.size = Pt(11)
    p1.font.color.rgb = TEXT_MUTED

# Slide 1: Page de Garde
slide = prs.slides.add_slide(blank_layout)
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = DARK_BLUE
bg.line.fill.background()

tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "ÉVALUATION FINALE — PROJETS NoSQL"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = TEAL_ACCENT

p2 = tf.add_paragraph()
p2.text = "Projet 9 : Microfinance et Tontines"
p2.font.size = Pt(32)
p2.font.bold = True
p2.font.color.rgb = WHITE
p2.space_before = Pt(10)

p3 = tf.add_paragraph()
p3.text = "Matière : Du SQL au NoSQL (bases de données, Big Data, MongoDB et Python)"
p3.font.size = Pt(14)
p3.font.color.rgb = RGBColor(203, 213, 225)
p3.space_before = Pt(10)

p4 = tf.add_paragraph()
p4.text = "Enseignant : FOTSO T. Valdez W."
p4.font.size = Pt(14)
p4.font.bold = True
p4.font.color.rgb = RGBColor(203, 213, 225)
p4.space_before = Pt(5)

# Members card
shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.8), Inches(11.333), Inches(2.8))
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(23, 42, 84)
shape.line.color.rgb = RGBColor(40, 65, 120)

tf2 = shape.text_frame
tf2.word_wrap = True
tf2.margin_left = tf2.margin_top = Inches(0.3)

pm = tf2.paragraphs[0]
pm.text = "Membres du Groupe :"
pm.font.size = Pt(14)
pm.font.bold = True
pm.font.color.rgb = TEAL_ACCENT

members = [
    ("Nom & Prénom 1", "Matricule 1", "Chef de Projet / Modélisation & CRUD"),
    ("Nom & Prénom 2", "Matricule 2", "Développeur Python / Agrégations"),
    ("Nom & Prénom 3", "Matricule 3", "Gestion des Données & Indexation"),
    ("Nom & Prénom 4", "Matricule 4", "Interface Graphique & Exports")
]

for name, mat, role in members:
    p_mem = tf2.add_paragraph()
    p_mem.text = f"• {name} ({mat}) — Rôle : {role}"
    p_mem.font.size = Pt(12)
    p_mem.font.color.rgb = WHITE
    p_mem.space_before = Pt(4)


# Helper for standard content slide
def create_standard_slide(title):
    s = prs.slides.add_slide(blank_layout)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT_BG
    bg.line.fill.background()
    add_header(s, title)
    return s

# Slide 2: Contexte
s2 = create_standard_slide("Contexte & Problématique Métier")
# Left Card: Problem
card1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
card1.fill.solid()
card1.fill.fore_color.rgb = CARD_BG
card1.line.color.rgb = BORDER_COLOR
tf = card1.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_top = tf.margin_right = Inches(0.3)
p = tf.paragraphs[0]
p.text = "📌 Le Contexte de la Microfinance"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = DARK_BLUE

bullets1 = [
    "Un établissement de microfinance accompagne ses membres à travers deux piliers majeurs : le crédit bancaire classique et les tontines traditionnelles.",
    "Les membres disposent d'un ou plusieurs comptes (épargne, courant), contractent des prêts amortissables sur plusieurs mois et participent à des tontines locales.",
    "Défi métier : Assurer la gestion simultanée des transactions financières, du suivi des remboursements d'échéances et des cagnottes de tontines sans incohérence."
]
for b in bullets1:
    p_b = tf.add_paragraph()
    p_b.text = "• " + b
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = TEXT_DARK
    p_b.space_before = Pt(8)

# Right Card: Solution
card2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
card2.fill.solid()
card2.fill.fore_color.rgb = CARD_BG
card2.line.color.rgb = BORDER_COLOR
tf2 = card2.text_frame
tf2.word_wrap = True
tf2.margin_left = tf2.margin_top = tf2.margin_right = Inches(0.3)
p = tf2.paragraphs[0]
p.text = "💡 Pourquoi NoSQL & MongoDB ?"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = DARK_BLUE

bullets2 = [
    "Flexibilité des structures : Imbrication naturelle des sous-documents (échéanciers de prêts, tours de tontines, cotisations) au sein d'un document unique.",
    "Scalabilité & Haute Disponibilité : Gestion volumétrique importante (des milliers de transactions) et agrégations analytiques complexes en temps réel.",
    "Atomicité des virements : Utilisation des transactions multi-documents ACID MongoDB pour éviter toute perte de fonds lors des virements inter-comptes."
]
for b in bullets2:
    p_b = tf2.add_paragraph()
    p_b.text = "• " + b
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = TEXT_DARK
    p_b.space_before = Pt(8)


# Slide 3: Objectifs
s3 = create_standard_slide("Objectifs du Projet & Fonctionnalités Clés")
box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
box.fill.solid()
box.fill.fore_color.rgb = CARD_BG
box.line.color.rgb = BORDER_COLOR
tf = box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_top = Inches(0.4)

objs = [
    ("Modélisation & Choix d'architecture", "Traduire les entités métiers (membres, comptes, transactions, prêts, tontines) en collections MongoDB adaptées, en justifiant chaque choix d'imbrication ou de référence."),
    ("Génération de Données Réalistes", "Générer un jeu de données volumineux et cohérent (160+ membres, 250+ comptes, 3200+ transactions, 100+ prêts avec échéancier, 12 tontines)."),
    ("Opérations CRUD & Transactions ACID", "Implémenter les règles métiers avec validation stricte, transactions multi-documents pour les virements et archivage automatique des prêts soldés."),
    ("Agrégations Analytiques Advanced", "Concevoir 5 pipelines d'agrégation ($match, $lookup, $unwind, $group) pour produire des statistiques décisionnelles en temps réel."),
    ("Optimisation & Conformité des Livrables", "Indexer les clés stratégiques, mesurer le gain de performance via explain, et fournir tous les exports JSON/CSV conformes.")
]

for title, desc in objs:
    p_t = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p_t.text = f"✔ {title}"
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = DARK_BLUE
    p_t.space_before = Pt(6)
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = TEXT_DARK
    p_d.space_before = Pt(2)


# Slide 4: Modélisation - Schéma Global
s4 = create_standard_slide("Modélisation NoSQL : Schéma des Collections & Liens")
# Left table/summary
c_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
c_box.fill.solid()
c_box.fill.fore_color.rgb = CARD_BG
c_box.line.color.rgb = BORDER_COLOR
tf = c_box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_top = Inches(0.3)

p = tf.paragraphs[0]
p.text = "🗂 Architecture des 5 Collections Principal"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = DARK_BLUE

cols = [
    ("membres", "Clé prim. : numero (MBR-xxxx). Contient l'identité, contact, profession, ville."),
    ("comptes", "Clé prim. : numero (CPT-xxxxx). Référence membre_numero -> membres.numero."),
    ("transactions", "Clé prim. : transaction_id. Référence compte_numero -> comptes.numero."),
    ("prets", "Clé prim. : code_pret. Référence membre_numero. Imbrique l'échéancier (liste de sous-documents)."),
    ("tontines", "Clé prim. : code_tontine. Contient membres (liste), ordre_benefice, et tours (sous-documents).")
]
for c_name, c_desc in cols:
    p_c = tf.add_paragraph()
    p_c.text = f"• {c_name} : {c_desc}"
    p_c.font.size = Pt(11)
    p_c.font.color.rgb = TEXT_DARK
    p_c.space_before = Pt(6)

# Right choice justification
c_box2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
c_box2.fill.solid()
c_box2.fill.fore_color.rgb = CARD_BG
c_box2.line.color.rgb = BORDER_COLOR
tf2 = c_box2.text_frame
tf2.word_wrap = True
tf2.margin_left = tf2.margin_top = Inches(0.3)

p2 = tf2.paragraphs[0]
p2.text = "🎯 Principes de Conception : Imbrication vs Référence"
p2.font.size = Pt(15)
p2.font.bold = True
p2.font.color.rgb = DARK_BLUE

justifs = [
    ("Référence (1-à-Plusieurs Élevé)", "Les transactions sont séparées des comptes car une collection de transactions grossit indéfiniment. Imbriquer des milliers de transactions dépasserait la limite de 16 Mo par document MongoDB."),
    ("Imbrication (1-à-Peu Borné)", "L'échéancier d’un prêt (3 à 24 mensualités) et les cotisations de tontines sont imbriqués sous forme de tableaux de sous-documents car leur taille est strictement limitée et ils sont toujours consultés avec le document parent."),
    ("Codes Métiers Lisibles", "Utilisation de identifiants lisibles (MBR-0001, CPT-00001) indexés uniques pour faciliter les requêtes de démonstration et les jointures $lookup.")
]
for j_t, j_d in justifs:
    p_j = tf2.add_paragraph()
    p_j.text = f"✔ {j_t}"
    p_j.font.size = Pt(12)
    p_j.font.bold = True
    p_j.font.color.rgb = TEAL_ACCENT
    p_j.space_before = Pt(6)
    
    p_jd = tf2.add_paragraph()
    p_jd.text = j_d
    p_jd.font.size = Pt(10.5)
    p_jd.font.color.rgb = TEXT_DARK
    p_jd.space_before = Pt(2)


# Slide 5: Modélisation - Structure des Documents Membres, Comptes, Transactions
s5 = create_standard_slide("Structure des Documents : Membres, Comptes & Transactions")
# 3 Cards
card_w = Inches(3.64)
card_h = Inches(5.3)

# Card 1: Membres
b1 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), card_w, card_h)
b1.fill.solid(); b1.fill.fore_color.rgb = CARD_BG; b1.line.color.rgb = BORDER_COLOR
tf1 = b1.text_frame; tf1.word_wrap = True; tf1.margin_left = tf1.margin_top = Inches(0.2)
tf1.paragraphs[0].text = "📄 Collection: membres"
tf1.paragraphs[0].font.size = Pt(13); tf1.paragraphs[0].font.bold = True; tf1.paragraphs[0].font.color.rgb = DARK_BLUE

m_code = """{
  "_id": ObjectId("..."),
  "numero": "MBR-0001",
  "nom": "Kengne Jean",
  "telephone": "+237698259335",
  "profession": "Médecin",
  "ville": "Yaoundé",
  "date_adhesion": ISODate("2021-04-12"),
  "piece_identite": "CNI-13356886"
}"""
p = tf1.add_paragraph()
p.text = m_code; p.font.size = Pt(9); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(6)

# Card 2: Comptes
b2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.84), Inches(1.5), card_w, card_h)
b2.fill.solid(); b2.fill.fore_color.rgb = CARD_BG; b2.line.color.rgb = BORDER_COLOR
tf2 = b2.text_frame; tf2.word_wrap = True; tf2.margin_left = tf2.margin_top = Inches(0.2)
tf2.paragraphs[0].text = "📄 Collection: comptes"
tf2.paragraphs[0].font.size = Pt(13); tf2.paragraphs[0].font.bold = True; tf2.paragraphs[0].font.color.rgb = DARK_BLUE

c_code = """{
  "_id": ObjectId("..."),
  "numero": "CPT-00001",
  "membre_numero": "MBR-0001",
  "type": "épargne",
  "solde": 254000.50,
  "date_ouverture": ISODate("2021-04-15")
}"""
p = tf2.add_paragraph()
p.text = c_code; p.font.size = Pt(9); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(6)

# Card 3: Transactions
b3 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.88), Inches(1.5), card_w, card_h)
b3.fill.solid(); b3.fill.fore_color.rgb = CARD_BG; b3.line.color.rgb = BORDER_COLOR
tf3 = b3.text_frame; tf3.word_wrap = True; tf3.margin_left = tf3.margin_top = Inches(0.2)
tf3.paragraphs[0].text = "📄 Collection: transactions"
tf3.paragraphs[0].font.size = Pt(13); tf3.paragraphs[0].font.bold = True; tf3.paragraphs[0].font.color.rgb = DARK_BLUE

t_code = """{
  "_id": ObjectId("..."),
  "transaction_id": "TXN-0000042",
  "compte_numero": "CPT-00001",
  "type": "dépôt",
  "montant": 50000.0,
  "date": ISODate("2025-01-10"),
  "canal": "agence"
}"""
p = tf3.add_paragraph()
p.text = t_code; p.font.size = Pt(9); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(6)


# Slide 6: Modélisation - Structure Prêts et Tontines
s6 = create_standard_slide("Structure des Documents : Prêts & Tontines (Sous-documents)")
w6 = Inches(5.6)
h6 = Inches(5.3)

# Prêts
bp = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), w6, h6)
bp.fill.solid(); bp.fill.fore_color.rgb = CARD_BG; bp.line.color.rgb = BORDER_COLOR
tfp = bp.text_frame; tfp.word_wrap = True; tfp.margin_left = tfp.margin_top = Inches(0.2)
tfp.paragraphs[0].text = "📄 Collection: prets (Échéancier Imbriqué)"
tfp.paragraphs[0].font.size = Pt(13); tfp.paragraphs[0].font.bold = True; tfp.paragraphs[0].font.color.rgb = DARK_BLUE

pret_code = """{
  "code_pret": "PRT-0014",
  "membre_numero": "MBR-0006",
  "montant": 1980544.16,
  "taux": 5.1,
  "duree_mois": 18,
  "date_octroi": ISODate("2024-04-17"),
  "statut": "en cours",
  "echeancier": [
    {
      "numero_echeance": 1,
      "date_echeance": ISODate("2024-05-17"),
      "montant_du": 110030.23,
      "paye": true,
      "date_paiement": ISODate("2024-05-15")
    }, ...
  ]
}"""
p = tfp.add_paragraph(); p.text = pret_code; p.font.size = Pt(8.5); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(4)

# Tontines
bt = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), w6, h6)
bt.fill.solid(); bt.fill.fore_color.rgb = CARD_BG; bt.line.color.rgb = BORDER_COLOR
tft = bt.text_frame; tft.word_wrap = True; tft.margin_left = tft.margin_top = Inches(0.2)
tft.paragraphs[0].text = "📄 Collection: tontines (Tours Imbriqués)"
tft.paragraphs[0].font.size = Pt(13); tft.paragraphs[0].font.bold = True; tft.paragraphs[0].font.color.rgb = DARK_BLUE

tontine_code = """{
  "code_tontine": "TNT-001",
  "nom": "Tontine Solidarité Douala",
  "montant_cotisation": 25000.0,
  "periodicite": "mensuelle",
  "membres": ["MBR-0001", "MBR-0002", "MBR-0003"],
  "ordre_benefice": ["MBR-0002", "MBR-0001", "MBR-0003"],
  "tours": [
    {
      "numero_tour": 1,
      "date": ISODate("2025-01-05"),
      "beneficiaire": "MBR-0002",
      "cotisations_recues": [
        {"membre_numero": "MBR-0001", "montant": 25000.0, "date": ISODate("2025-01-04")},
        {"membre_numero": "MBR-0002", "montant": 25000.0, "date": ISODate("2025-01-05")}
      ]
    }
  ]
}"""
p = tft.add_paragraph(); p.text = tontine_code; p.font.size = Pt(8.5); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(4)


# Slide 7: Jeu de Données
s7 = create_standard_slide("Génération du Jeu de Données Réaliste (generer_donnees.py)")
# Left text info
box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box.fill.solid(); box.fill.fore_color.rgb = CARD_BG; box.line.color.rgb = BORDER_COLOR
tf = box.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_top = Inches(0.3)

p = tf.paragraphs[0]; p.text = "📊 Volumétrie Générée & Reproductibilité"
p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = DARK_BLUE

data_info = [
    ("Reproductibilité Stricte", "Utilisation de `random.seed(42)` garantissant un jeu de données identique à chaque exécution du script."),
    ("membres", "160 documents insérés (Exigence minimum : >= 150) avec noms, professions et villes réelles du Cameroun."),
    ("comptes", "250 documents insérés (Exigence minimum : >= 200) distribués entre comptes épargne et courant."),
    ("transactions", "3 200 documents insérés (Exigence minimum : >= 3 000) couvrant dépôts, retraits, virements et remboursements."),
    ("prets", "100 prêts insérés (Exigence minimum : >= 80) générant plus de 1 200 sous-documents d'échéances."),
    ("tontines", "12 tontines insérées (Exigence minimum : >= 10) avec listes de membres et historiques des tours.")
]
for d_t, d_d in data_info:
    p_t = tf.add_paragraph()
    p_t.text = f"• {d_t} : {d_d}"
    p_t.font.size = Pt(11)
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_before = Pt(6)

# Right Placeholder
add_placeholder_box(s7, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture MongoDB Compass", 
                    "Affichage des 5 collections et du nombre total de documents insérés")


# Slide 8: CRUD - INSERT
s8 = create_standard_slide("Opérations CRUD : Insertion & Validation (INSERT)")
box8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box8.fill.solid(); box8.fill.fore_color.rgb = CARD_BG; box8.line.color.rgb = BORDER_COLOR
tf8 = box8.text_frame; tf8.word_wrap = True; tf8.margin_left = tf8.margin_top = Inches(0.3)
tf8.paragraphs[0].text = "📝 Logique de Création & Validation Stricte"
tf8.paragraphs[0].font.size = Pt(15); tf8.paragraphs[0].font.bold = True; tf8.paragraphs[0].font.color.rgb = DARK_BLUE

c_info = [
    ("Génération Automatique de Codes", "Fonction `generer_code_auto` dans `utils.py` pour générer automatiquement les séquences MBR-xxxx, CPT-xxxxx, PRT-xxxx et TNT-xxx si le champ est omis."),
    ("Module de Validation (validators.py)", "Contrôle avant insertion : format de téléphone (+237), vérification de l'existence du membre propriétaire, positivité du solde et des montants."),
    ("Gestion des Doublons", "Interception systématique des erreurs `DuplicateKeyError` pour garantir l'unicité des clés métiers.")
]
for ci_t, ci_d in c_info:
    p = tf8.add_paragraph()
    p.text = f"• {ci_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf8.add_paragraph()
    p2.text = ci_d; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)

add_placeholder_box(s8, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture de Code & Résultat INSERT", 
                    "Code Python de create_membre / create_compte et résultat de l'exécution dans le terminal")


# Slide 9: CRUD - FIND
s9 = create_standard_slide("Opérations CRUD : Interrogation & Lecteurs (FIND)")
box9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box9.fill.solid(); box9.fill.fore_color.rgb = CARD_BG; box9.line.color.rgb = BORDER_COLOR
tf9 = box9.text_frame; tf9.word_wrap = True; tf9.margin_left = tf9.margin_top = Inches(0.3)
tf9.paragraphs[0].text = "🔍 Opérations de Lecture Implémentées"
tf9.paragraphs[0].font.size = Pt(15); tf9.paragraphs[0].font.bold = True; tf9.paragraphs[0].font.color.rgb = DARK_BLUE

find_ops = [
    ("Comptes et solde d'un membre", "Recherche des comptes rattachés à un membre_numero donné et calcul du solde cumulé."),
    ("Relevé de transactions filtré", "Extraction des transactions d'un compte sur une période temporelle donnée avec tri chronologique inverse."),
    ("Échéances impayées à ce jour", "Recherche via $unwind / find dans les sous-documents d'échéances non payées dont la date est échue."),
    ("Tontines & Prochain bénéficiaire", "Consultation des tontines d'un membre et calcul dynamique du prochain membre dans l'ordre de bénéfice.")
]
for fo_t, fo_d in find_ops:
    p = tf9.add_paragraph()
    p.text = f"• {fo_t} : {fo_d}"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(8)

add_placeholder_box(s9, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture des Résultats FIND", 
                    "Affichage du relevé de compte et de la liste des échéances impayées dans le terminal")


# Slide 10: CRUD - UPDATE & Transactions ACID
s10 = create_standard_slide("Opérations CRUD : Mises à jour & Transactions ACID (UPDATE)")
box10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box10.fill.solid(); box10.fill.fore_color.rgb = CARD_BG; box10.line.color.rgb = BORDER_COLOR
tf10 = box10.text_frame; tf10.word_wrap = True; tf10.margin_left = tf10.margin_top = Inches(0.3)
tf10.paragraphs[0].text = "🔄 Mises à jour Atomiques & Virements ACID"
tf10.paragraphs[0].font.size = Pt(15); tf10.paragraphs[0].font.bold = True; tf10.paragraphs[0].font.color.rgb = DARK_BLUE

up_ops = [
    ("Dépôts & Retraits Sécurisés", "Mise à jour du solde du compte avec vérification atomique de solde suffisant pour éviter les découverts interdits."),
    ("Virement Inter-comptes ACID", "Utilisation de `with client.start_session() as s: with s.start_transaction():` pour exécuter le débit du compte source et le crédit du compte cible de manière atomique."),
    ("Paiement d’Échéance & Cotisation", "Utilisation de l’opérateur positionnel MongoDB `$set` sur `echeancier.$.paye` et `$push` pour ajouter la cotisation dans le tour de tontine.")
]
for u_t, u_d in up_ops:
    p = tf10.add_paragraph()
    p.text = f"• {u_t} : {u_d}"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(8)

add_placeholder_box(s10, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture de Code Virement ACID", 
                    "Code Python de la transaction ACID multi-documents et logs de confirmation")


# Slide 11: CRUD - DELETE & Archiving
s11 = create_standard_slide("Opérations CRUD : Clôture & Archivage (DELETE / ARCHIVE)")
box11 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box11.fill.solid(); box11.fill.fore_color.rgb = CARD_BG; box11.line.color.rgb = BORDER_COLOR
tf11 = box11.text_frame; tf11.word_wrap = True; tf11.margin_left = tf11.margin_top = Inches(0.3)
tf11.paragraphs[0].text = "📦 Stratégie de Clôture & Archivage"
tf11.paragraphs[0].font.size = Pt(15); tf11.paragraphs[0].font.bold = True; tf11.paragraphs[0].font.color.rgb = DARK_BLUE

del_ops = [
    ("Clôture de Compte à Solde Nul", "Seuls les comptes ayant un solde exact de 0.0 FCFA peuvent être supprimés de la collection `comptes` pour des raisons de conformité."),
    ("Principe d'Archivage (Chapitre 2)", "Dans le secteur financier, les données ne sont pas détruites mais archivées."),
    ("Fonction `archiver_prets_soldes`", "1. Sélection des prêts avec statut 'soldé'.\n2. Ajout du champ `date_archivage = datetime.now()`.\n3. Insertion dans `prets_archives`.\n4. Suppression sécurisée de la collection principale `prets` via `delete_many`.")
]
for d_t, d_d in del_ops:
    p = tf11.add_paragraph()
    p.text = f"• {d_t} : {d_d}"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(8)

# Replace right placeholder with actual screenshot if available
slide11_img = "/home/bakayoko2-0/.gemini/antigravity-ide/brain/8170085c-9d6a-4d25-8878-123f33aba5ad/scratch/archiver_code.png"
import os
if os.path.exists(slide11_img):
    s11.shapes.add_picture(slide11_img, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
else:
    add_placeholder_box(s11, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                        "Capture Code & Résultat Archivage", 
                        "Fonction archiver_prets_soldes et message terminal confirmant le transfert vers prets_archives")


# Slide 12: Synthèse CRUD
s12 = create_standard_slide("Synthèse des Fonctionnalités CRUD Implémentées")
box12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
box12.fill.solid(); box12.fill.fore_color.rgb = CARD_BG; box12.line.color.rgb = BORDER_COLOR
tf12 = box12.text_frame; tf12.word_wrap = True; tf12.margin_left = tf12.margin_top = Inches(0.4)

summary_crud = [
    ("CREATE", "create_membre(), create_compte(), create_transaction(), create_pret(), create_tontine()"),
    ("READ", "obtenir_comptes_membre(), obtenir_releve_transactions(), obtenir_echeances_impayees(), obtenir_tontines_membre()"),
    ("UPDATE", "deposer_argent(), retirer_argent(), virement_inter_comptes() [Transaction ACID], payer_echeance_pret(), cotiser_tontine()"),
    ("DELETE / ARCHIVE", "cloturer_compte_solde_nul(), archiver_prets_soldes() -> prets_archives")
]

for cat, f_list in summary_crud:
    p = tf12.add_paragraph() if tf12.paragraphs[0].text else tf12.paragraphs[0]
    p.text = f"▪ Opérations {cat}"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = DARK_BLUE; p.space_before = Pt(8)
    
    p2 = tf12.add_paragraph()
    p2.text = f"Fonctions Python : {f_list}"
    p2.font.size = Pt(11); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)


# Slide 13: Agrégation 1
s13 = create_standard_slide("Agrégation 1 : Encours Total des Prêts par Ville & Profession")
box13 = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box13.fill.solid(); box13.fill.fore_color.rgb = CARD_BG; box13.line.color.rgb = BORDER_COLOR
tf13 = box13.text_frame; tf13.word_wrap = True; tf13.margin_left = tf13.margin_top = Inches(0.3)
tf13.paragraphs[0].text = "📊 Pipeline & Analyse Métier ($lookup & $unwind)"
tf13.paragraphs[0].font.size = Pt(14); tf13.paragraphs[0].font.bold = True; tf13.paragraphs[0].font.color.rgb = DARK_BLUE

pipe1_desc = [
    ("Pipeline MongoDB", "1. `$match` : Filtrage des prêts en cours ou en retard.\n2. `$lookup` : Jointure entre `prets.membre_numero` et `membres.numero`.\n3. `$unwind` : Aplatissement de l'array `info_membre`.\n4. `$group` : Regroupement par ville et profession avec `$sum` des montants."),
    ("Interprétation des Résultats", "Permet à la direction des risques d'identifier la concentration du crédit. Exemple : Les commerçants de Douala et les agriculteurs de Bafoussam représentent le plus fort encours du portefeuille.")
]
for p_t, p_d in pipe1_desc:
    p = tf13.add_paragraph(); p.text = f"• {p_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf13.add_paragraph(); p2.text = p_d
    p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)

add_placeholder_box(s13, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture du Résultat Agrégation 1", 
                    "Extrait JSON / Tableau des encours classés par ville et profession")


# Slide 14: Agrégation 2
s14 = create_standard_slide("Agrégation 2 : Taux de Remboursement à l'Échéance")
box14 = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box14.fill.solid(); box14.fill.fore_color.rgb = CARD_BG; box14.line.color.rgb = BORDER_COLOR
tf14 = box14.text_frame; tf14.word_wrap = True; tf14.margin_left = tf14.margin_top = Inches(0.3)
tf14.paragraphs[0].text = "📊 Pipeline sur Sous-documents ($unwind & $cond)"
tf14.paragraphs[0].font.size = Pt(14); tf14.paragraphs[0].font.bold = True; tf14.paragraphs[0].font.color.rgb = DARK_BLUE

pipe2_desc = [
    ("Pipeline MongoDB", "1. `$unwind` : Dénormalisation du tableau `echeancier`.\n2. `$match` : Conservation des échéances dues (`date_echeance <= maintenant`).\n3. `$group` : Calcul du nombre total d'échéances dues et payées via `$cond`.\n4. `$project` : Calcul du ratio exprimé en pourcentage."),
    ("Interprétation des Résultats", "Évalue la qualité du recouvrement global. Un taux supérieur à 85% atteste d'une bonne santé du portefeuille de crédits.")
]
for p_t, p_d in pipe2_desc:
    p = tf14.add_paragraph(); p.text = f"• {p_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf14.add_paragraph(); p2.text = p_d
    p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)

add_placeholder_box(s14, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture du Résultat Agrégation 2", 
                    "Taux de remboursement global et montants totaux recouvrés vs dus")


# Slide 15: Agrégation 3
s15 = create_standard_slide("Agrégation 3 : Volume des Dépôts & Retraits par Mois et Canal")
box15 = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
box15.fill.solid(); box15.fill.fore_color.rgb = CARD_BG; box15.line.color.rgb = BORDER_COLOR
tf15 = box15.text_frame; tf15.word_wrap = True; tf15.margin_left = tf15.margin_top = Inches(0.3)
tf15.paragraphs[0].text = "📊 Analyse des Flux Financement ($dateToString & $group)"
tf15.paragraphs[0].font.size = Pt(14); tf15.paragraphs[0].font.bold = True; tf15.paragraphs[0].font.color.rgb = DARK_BLUE

pipe3_desc = [
    ("Pipeline MongoDB", "1. `$match` : Filtrage sur les types 'dépôt' et 'retrait'.\n2. `$group` : Regroupement par année-mois (`$dateToString`), type de flux et canal (`agence` vs `mobile_money`).\n3. `$sort` : Tri chronologique par mois."),
    ("Interprétation des Résultats", "Révèle l'adoption du canal Mobile Money par rapport aux guichets physiques et aide à anticiper les besoins en liquidités des agences.")
]
for p_t, p_d in pipe3_desc:
    p = tf15.add_paragraph(); p.text = f"• {p_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf15.add_paragraph(); p2.text = p_d
    p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)

add_placeholder_box(s15, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture du Résultat Agrégation 3", 
                    "Volume des flux par mois et répartition agence vs mobile money")


# Slide 16: Agrégations 4 & 5
s16 = create_standard_slide("Agrégations 4 & 5 : Retards de Crédit & Suivi des Tontines")
b16_left = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
b16_left.fill.solid(); b16_left.fill.fore_color.rgb = CARD_BG; b16_left.line.color.rgb = BORDER_COLOR
tf16_l = b16_left.text_frame; tf16_l.word_wrap = True; tf16_l.margin_left = tf16_l.margin_top = Inches(0.3)
tf16_l.paragraphs[0].text = "⚠️ Agrégation 4: Membres en Retard (> 30 jours)"
tf16_l.paragraphs[0].font.size = Pt(13); tf16_l.paragraphs[0].font.bold = True; tf16_l.paragraphs[0].font.color.rgb = DARK_BLUE

a4_desc = [
    ("Description", "Filtre les échéances non payées dépassées de plus de 30 jours, joint les informations du membre via `$lookup` et calcule le montant impayé restant."),
    ("Utilisation Métier", "Génération des relances contentieuses et identification des membres à restreindre pour de nouveaux prêts.")
]
for t, d in a4_desc:
    p = tf16_l.add_paragraph(); p.text = f"• {t} : {d}"
    p.font.size = Pt(10.5); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(6)

b16_right = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
b16_right.fill.solid(); b16_right.fill.fore_color.rgb = CARD_BG; b16_right.line.color.rgb = BORDER_COLOR
tf16_r = b16_right.text_frame; tf16_r.word_wrap = True; tf16_r.margin_left = tf16_r.margin_top = Inches(0.3)
tf16_r.paragraphs[0].text = "🤝 Agrégation 5: Taux de Cotisation des Tontines"
tf16_r.paragraphs[0].font.size = Pt(13); tf16_r.paragraphs[0].font.bold = True; tf16_r.paragraphs[0].font.color.rgb = DARK_BLUE

a5_desc = [
    ("Description", "Extrait le dernier tour de chaque tontine, compare le nombre de cotisations perçues au nombre de membres inscrits."),
    ("Utilisation Métier", "Mesure l'assiduité des participants de tontine et identifie les défaillances de paiement avant l'attribution de la cagnotte.")
]
for t, d in a5_desc:
    p = tf16_r.add_paragraph(); p.text = f"• {t} : {d}"
    p.font.size = Pt(10.5); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(6)


# Slide 17: Indexation & Optimization
s17 = create_standard_slide("Optimisation & Performance : Indexation (indexes.py)")
b17 = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
b17.fill.solid(); b17.fill.fore_color.rgb = CARD_BG; b17.line.color.rgb = BORDER_COLOR
tf17 = b17.text_frame; tf17.word_wrap = True; tf17.margin_left = tf17.margin_top = Inches(0.3)
tf17.paragraphs[0].text = "⚡ Stragétie d'Indexation & Gain `explain`"
tf17.paragraphs[0].font.size = Pt(15); tf17.paragraphs[0].font.bold = True; tf17.paragraphs[0].font.color.rgb = DARK_BLUE

idx_list = [
    ("Index Uniques Obligatoires", "`membres.numero`, `comptes.numero`, `prets.code_pret`, `tontines.code_tontine` (unicité et accès direct)."),
    ("Index Composé Justifié", "`transactions (compte_numero: 1, date: -1)` pour accélérer l'affichage des relevés de compte sans tri en mémoire."),
    ("Index de Jointure ($lookup)", "`comptes.membre_numero`, `prets.membre_numero` et `tontines.membres`."),
    ("Preuve d'Efficacité (`explain()`)", "Passage d'un balayage de collection complet (`COLLSCAN`) à une recherche par index ciblée (`IXSCAN`), réduisant le temps d'exécution de plusieurs millisecondes à < 1ms.")
]
for i_t, i_d in idx_list:
    p = tf17.add_paragraph(); p.text = f"• {i_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf17.add_paragraph(); p2.text = i_d
    p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)

add_placeholder_box(s17, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3), 
                    "Capture de `explain()` MongoDB", 
                    "Affichage du winningPlan montrant IXSCAN et l'utilisation de l'index composé sur les transactions")


# Slide 18: Difficultés & Solutions
s18 = create_standard_slide("Difficultés Rencontrées & Solutions Apportées")
box18 = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
box18.fill.solid(); box18.fill.fore_color.rgb = CARD_BG; box18.line.color.rgb = BORDER_COLOR
tf18 = box18.text_frame; tf18.word_wrap = True; tf18.margin_left = tf18.margin_top = Inches(0.4)

diffs = [
    ("Gestion des Transactions Multi-documents en Local", 
     "Problème : Les transactions ACID MongoDB requièrent impérativement un ensemble de réplicas (Replica Set).\nSolution : Configuration d'un Replica Set local (`mongod --replSet rs0`) et gestion d'un secours propre en cas de serveur standalone."),
    
    ("Calcul du Taux de Remboursement sur Sous-documents", 
     "Problème : Manipulation d'échéanciers de durées variables imbriqués dans les prêts.\nSolution : Utilisation combinée de `$unwind` pour décomposer les échéances et de `$cond` dans l'étape `$group`."),
    
    ("Double Entrée Terminal & Interface Graphique Tkinter", 
     "Problème : Proposer une application flexible à la fois pour la démonstration en ligne de commande et pour les utilisateurs finaux.\nSolution : Architecture modulaire dans `main.py` permettant un basculement fluide entre le mode console et l'IHM Tkinter.")
]

for title, desc in diffs:
    p_t = tf18.add_paragraph() if tf18.paragraphs[0].text else tf18.paragraphs[0]
    p_t.text = f"🚨 {title}"
    p_t.font.size = Pt(13); p_t.font.bold = True; p_t.font.color.rgb = DARK_BLUE; p_t.space_before = Pt(8)
    
    p_d = tf18.add_paragraph()
    p_d.text = desc; p_d.font.size = Pt(11); p_d.font.color.rgb = TEXT_DARK; p_d.space_before = Pt(2)


# Slide 19: Répartition du Travail
s19 = create_standard_slide("Répartition du Travail au Sein du Groupe")
box19 = s19.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
box19.fill.solid(); box19.fill.fore_color.rgb = CARD_BG; box19.line.color.rgb = BORDER_COLOR
tf19 = box19.text_frame; tf19.word_wrap = True; tf19.margin_left = tf19.margin_top = Inches(0.4)

tasks = [
    ("Membre 1 (Chef de Projet)", "Modélisation NoSQL des 5 collections, architecture du fichier config.py, écriture des fonctions CRUD de base (membres, comptes)."),
    ("Membre 2 (Développeur Backend)", "Implémentation des transactions ACID de virement inter-comptes, développement du module de validation (validators.py) et archivage des prêts soldés."),
    ("Membre 3 (Spécialiste Data & Index)", "Écriture des 5 pipelines d'agrégation analytiques (agregations.py), conception et benchmark des index (indexes.py) via explain()."),
    ("Membre 4 (IHM & Livrables)", "Développement de l'interface graphique Tkinter (main.py), scripts d'export JSON/CSV (exports.py), rédaction du rapport et enregistrement vidéo.")
]

for m_name, m_tasks in tasks:
    p_t = tf19.add_paragraph() if tf19.paragraphs[0].text else tf19.paragraphs[0]
    p_t.text = f"👤 {m_name}"
    p_t.font.size = Pt(13); p_t.font.bold = True; p_t.font.color.rgb = DARK_BLUE; p_t.space_before = Pt(8)
    
    p_d = tf19.add_paragraph()
    p_d.text = m_tasks; p_d.font.size = Pt(11); p_d.font.color.rgb = TEXT_DARK; p_d.space_before = Pt(2)


# Slide 20: Conclusion & Perspectives
s20 = create_standard_slide("Conclusion, Limites & Améliorations Possibles")
b20_l = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
b20_l.fill.solid(); b20_l.fill.fore_color.rgb = CARD_BG; b20_l.line.color.rgb = BORDER_COLOR
tf20_l = b20_l.text_frame; tf20_l.word_wrap = True; tf20_l.margin_left = tf20_l.margin_top = Inches(0.3)
tf20_l.paragraphs[0].text = "🎯 Bilan du Projet"
tf20_l.paragraphs[0].font.size = Pt(15); tf20_l.paragraphs[0].font.bold = True; tf20_l.paragraphs[0].font.color.rgb = DARK_BLUE

bilan = [
    "Application Python/MongoDB complète et pleinement fonctionnelle respectant 100% des exigences du sujet 9.",
    "Modélisation équilibrée combinant imbrication de sous-documents et références clés métiers.",
    "Garantie de l'atomicité bancaire grâce aux transactions multi-documents MongoDB."
]
for b in bilan:
    p = tf20_l.add_paragraph(); p.text = f"✔ {b}"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_DARK; p.space_before = Pt(8)

b20_r = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
b20_r.fill.solid(); b20_r.fill.fore_color.rgb = CARD_BG; b20_r.line.color.rgb = BORDER_COLOR
tf20_r = b20_r.text_frame; tf20_r.word_wrap = True; tf20_r.margin_left = tf20_r.margin_top = Inches(0.3)
tf20_r.paragraphs[0].text = "🚀 Améliorations & Pistes Bonus"
tf20_r.paragraphs[0].font.size = Pt(15); tf20_r.paragraphs[0].font.bold = True; tf20_r.paragraphs[0].font.color.rgb = DARK_BLUE

bonus = [
    ("Score de Fiabilité des Membres", "Calcul automatique d'un score de crédit (credit scoring) basé sur l'historique des remboursements à temps."),
    ("Échéancier à Mensualités Constantes", "Génération automatique d'échéanciers basés sur la formule d'amortissement bancaire classique."),
    ("API REST Web", "Exposition des fonctions CRUD et agrégations via un framework Web moderne (FastAPI/Flask) et un dashboard React.")
]
for b_t, b_d in bonus:
    p = tf20_r.add_paragraph(); p.text = f"• {b_t} :"
    p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = TEAL_ACCENT; p.space_before = Pt(6)
    p2 = tf20_r.add_paragraph(); p2.text = b_d
    p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_DARK; p2.space_before = Pt(2)


prs.save("rapport_Groupe09.pptx")
print("PowerPoint generated successfully: rapport_Groupe09.pptx")
