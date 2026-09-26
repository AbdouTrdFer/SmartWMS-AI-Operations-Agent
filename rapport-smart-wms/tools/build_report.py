from __future__ import annotations

import html
import shutil
import textwrap
from pathlib import Path

import fitz
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
BUILD = ROOT / "build"
FIGURES = ROOT / "figures"
CHAPTERS = ROOT / "chapters"
CONFIG = ROOT / "config"
BIB = ROOT / "bibliography"
ANNEXES = ROOT / "annexes"

NAVY = "#173F66"
TEAL = "#2A837C"
RED = "#D7261E"
VIOLET = "#7D60C8"
ORANGE = "#EE8626"
GREEN = "#5D9A50"
LIGHT_BG = "#F6F8FB"
TEXT = "#152638"


def ensure_dirs() -> None:
    for path in [
        BUILD,
        CHAPTERS,
        CONFIG,
        BIB,
        ANNEXES / "plantuml",
        ANNEXES / "schemas",
        FIGURES / "chapitre3",
        FIGURES / "chapitre4",
        FIGURES / "chapitre5",
        FIGURES / "chapitre6",
        FIGURES / "chapitre7",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def copy_plantuml() -> None:
    src = REPO / "diagramms"
    if not src.exists():
        return
    for puml in src.glob("*.puml"):
        shutil.copy2(puml, ANNEXES / "plantuml" / puml.name)


def svg_text(
    x: float,
    y: float,
    lines: list[str] | str,
    *,
    size: int = 16,
    fill: str = TEXT,
    weight: str = "400",
    anchor: str = "start",
    line_height: int | None = None,
) -> str:
    if isinstance(lines, str):
        lines = [lines]
    line_height = line_height or int(size * 1.35)
    chunks = [
        f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" fill="{fill}" font-weight="{weight}" '
        f'text-anchor="{anchor}">'
    ]
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else line_height
        chunks.append(f'<tspan x="{x}" dy="{dy}">{html.escape(line)}</tspan>')
    chunks.append("</text>")
    return "".join(chunks)


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str = "white",
    stroke: str = NAVY,
    sw: float = 2,
    rx: float = 10,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = NAVY) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="4" marker-end="url(#arrow)"/>'
    )


def svg_defs() -> str:
    return """
    <defs>
      <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6"
              orient="auto" markerUnits="strokeWidth">
        <path d="M2,2 L10,6 L2,10 z" fill="#173F66"/>
      </marker>
      <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">
        <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.16"/>
      </filter>
    </defs>
    """


def write_svg_asset(relative: str, svg: str) -> Path:
    svg_path = FIGURES / relative
    write_text(svg_path, svg)
    doc = fitz.open(stream=svg.encode("utf-8"), filetype="svg")
    pdf_path = svg_path.with_suffix(".pdf")
    pdf_path.write_bytes(doc.convert_to_pdf())
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
    png_path = svg_path.with_suffix(".png")
    pix.save(png_path)
    return svg_path


def build_diagrams() -> None:
    write_svg_asset("chapitre3/demarche_scan_plan_act.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360">
      {svg_defs()}
      <rect width="1200" height="360" fill="white"/>
      {svg_text(600, 42, "Démarche d’identification des besoins appliquée au stage", size=24, weight="700", fill=NAVY, anchor="middle")}
      {rect(75, 85, 290, 190, fill="#F4F8FC", stroke=NAVY, rx=18)}
      {rect(455, 85, 290, 190, fill="#F4FBFA", stroke=TEAL, rx=18)}
      {rect(835, 85, 290, 190, fill="#FFF7EF", stroke=ORANGE, rx=18)}
      {svg_text(110, 125, "SCAN", size=22, weight="700", fill=NAVY)}
      {svg_text(110, 162, ["Observer et comprendre", "• Benchmark leaders", "• Architecture existante", "• Problèmes / contraintes", "• Données disponibles"], size=17, fill=TEXT)}
      {svg_text(490, 125, "PLAN", size=22, weight="700", fill=TEAL)}
      {svg_text(490, 162, ["Transformer le constat", "• Problème → cause → impact", "• Use case", "• Core / Smart / Optional", "• Critère d’activation"], size=17, fill=TEXT)}
      {svg_text(870, 125, "ACT", size=22, weight="700", fill=ORANGE)}
      {svg_text(870, 162, ["Formaliser et valider", "• Diagrammes UML", "• Scénarios métiers", "• Validation encadrante", "• Itérations architecture"], size=17, fill=TEXT)}
      {arrow(385, 180, 435, 180)}
      {arrow(765, 180, 815, 180)}
      {svg_text(600, 322, "Principe : ne pas choisir une technologie avant d’avoir clarifié le besoin, l’impact et les données disponibles.", size=15, fill="#5F6B78", anchor="middle")}
    </svg>
    """)

    write_svg_asset("chapitre3/classification_activation.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 780">
      {svg_defs()}
      <rect width="1000" height="780" fill="white"/>
      {svg_text(500, 48, "Logique de classification et d’activation des use cases", size=27, weight="700", fill=NAVY, anchor="middle")}

      {rect(55, 90, 275, 132, fill="#F4F8FC", stroke=NAVY, rx=20)}
      <rect x="55" y="90" width="275" height="46" rx="20" fill="{NAVY}"/>
      {svg_text(192, 119, "CORE", size=18, weight="700", fill="white", anchor="middle")}
      {svg_text(78, 163, ["Capacité nécessaire au", "fonctionnement du WMS", "Ex. réception, stock, tâches"], size=14, fill="#66717E", line_height=18)}

      {rect(362, 90, 275, 132, fill="#FBF8FF", stroke=VIOLET, rx=20)}
      <rect x="362" y="90" width="275" height="46" rx="20" fill="{VIOLET}"/>
      {svg_text(499, 119, "SMART", size=18, weight="700", fill="white", anchor="middle")}
      {svg_text(385, 163, ["Décision améliorée par", "données, optimisation ou ML", "Ex. prévision, slotting"], size=14, fill="#66717E", line_height=18)}

      {rect(669, 90, 275, 132, fill="#FFF8F0", stroke=ORANGE, rx=20)}
      <rect x="669" y="90" width="275" height="46" rx="20" fill="{ORANGE}"/>
      {svg_text(806, 119, "OPTIONAL", size=18, weight="700", fill="white", anchor="middle")}
      {svg_text(692, 163, ["Capacité dépendante", "d’une infrastructure", "Ex. RFID, AMR/AGV, BMS/EMS"], size=14, fill="#66717E", line_height=18)}

      {rect(205, 285, 590, 70, fill="#FFFFFF", stroke=NAVY, rx=18)}
      {svg_text(500, 328, "Besoin métier identifié", size=21, weight="700", fill=TEXT, anchor="middle")}
      {arrow(500, 355, 500, 392)}

      {rect(205, 395, 590, 70, fill="#F7FCFB", stroke=TEAL, rx=18)}
      {svg_text(500, 438, "Données suffisantes ?", size=21, weight="700", fill=TEXT, anchor="middle")}
      {svg_text(815, 420, ["non : règle métier", "ou processus classique"], size=13, fill="#66717E")}
      {arrow(500, 465, 500, 502)}

      {rect(205, 505, 590, 70, fill="#FFF9F1", stroke=ORANGE, rx=18)}
      {svg_text(500, 548, "Infrastructure requise ?", size=21, weight="700", fill=TEXT, anchor="middle")}
      {svg_text(815, 530, ["oui : vérifier équipement,", "capteur ou système externe"], size=13, fill="#66717E")}
      {arrow(500, 575, 500, 612)}

      {rect(205, 615, 590, 70, fill="#FBF8FF", stroke=VIOLET, rx=18)}
      {svg_text(500, 658, "Activer le use case adapté", size=21, weight="700", fill=TEXT, anchor="middle")}
      {svg_text(500, 735, "Objectif : éviter de présenter une option technologique comme une fonction obligatoire du WMS.", size=15, fill="#5F6B78", anchor="middle")}
    </svg>
    """)

    architecture_boxes = [
        ("ERP / SAP", ["Commandes, stocks,", "clients, fournisseurs"]),
        ("MES", ["Ordres production,", "matières, confirmations"]),
        ("TMS / YMS", ["Transport, camions,", "transporteurs, quais"]),
        ("FOURNISSEURS", ["ASN, informations", "de livraison"]),
        ("CLIENTS", ["Commandes clients,", "confirmations"]),
        ("AUTRES SYSTÈMES", ["Finance, RH, BI,", "CRM, reporting"]),
    ]
    ext = []
    for i, (title, body) in enumerate(architecture_boxes):
        x = 290 + i * 190
        ext.append(rect(x, 100, 165, 80, fill="#FFFFFF", stroke=NAVY, rx=8))
        ext.append(svg_text(x + 82.5, 126, title, size=14, weight="700", fill=NAVY, anchor="middle"))
        ext.append(svg_text(x + 82.5, 150, body, size=12, fill=TEXT, anchor="middle", line_height=14))

    core_cols = [
        ("RÉCEPTION\nMARCHANDISES", ["Rendez-vous & quais", "Réception", "Contrôle qualité", "Quantités", "Cross-docking", "Retours fournisseurs"]),
        ("STOCKAGE\n& INVENTAIRE", ["Emplacements", "Stocks", "Réapprovisionnement", "Stock de réserve", "Inventaire tournant", "Lots / dates"]),
        ("GESTION\nDES COMMANDES", ["Ordonnancement", "Planification", "Wave / Batch", "Allocation", "Priorités"]),
        ("EXÉCUTION\nENTREPÔT", ["Picking", "Packing", "Staging", "Consolidation", "Chargement", "Expédition"]),
        ("YARD & QUAIS", ["Gestion cour", "Planification quais", "Affectation quais", "Portes", "Transporteurs", "Entrées / sorties"]),
    ]
    core = []
    for i, (title, items) in enumerate(core_cols):
        x = 290 + i * 185
        core.append(rect(x, 270, 165, 325, fill="#FFFFFF", stroke=RED, rx=8))
        core.append(f'<rect x="{x}" y="270" width="165" height="48" fill="{RED}" rx="8"/>')
        core.append(svg_text(x + 82.5, 291, title.split("\n"), size=13, weight="700", fill="white", anchor="middle", line_height=15))
        core.append(svg_text(x + 18, 345, [f"• {item}" for item in items], size=11, fill=TEXT, line_height=33))

    support = [
        ("GESTION MAIN-D’ŒUVRE", ["Planification", "Compétences", "Équilibrage charge", "Productivité"]),
        ("GESTION ÉQUIPEMENTS", ["Chariots / convoyeurs", "AS/RS / shuttle", "AMR / AGV / robots", "Maintenance"]),
        ("ÉNERGIE & ENVIRONNEMENT", ["Consommation zones", "Température / humidité", "Seuils & consignes", "Pics consommation"]),
        ("INTERFACES WCS / WES", ["Instructions", "États / erreurs", "Itinéraires", "Trafic"]),
        ("GESTION DES ACTIFS", ["Suivi actifs", "Étalonnage", "Utilisation", "Cycle de vie"]),
    ]
    support_svg = []
    for i, (title, items) in enumerate(support):
        x = 295 + i * 238
        support_svg.append(rect(x, 690, 215, 135, fill="#FBFFFB", stroke=GREEN, rx=8))
        support_svg.append(svg_text(x + 107, 717, title, size=12, weight="700", fill=GREEN, anchor="middle"))
        support_svg.append(svg_text(x + 18, 745, [f"• {item}" for item in items], size=11, fill=TEXT, line_height=20))

    ai = [
        ("PRÉVISION DEMANDE\n& CHARGE", ["Inbound", "Outbound", "Ressources"]),
        ("OPTIMISATION\nSLOTTING", ["ABC / vélocité", "Occupation espace", "Règles dynamiques"]),
        ("OPTIMISATION\nORDRES / TÂCHES", ["Waves", "Parcours", "Séquençage", "Priorisation"]),
        ("OPTIMISATION\nMAIN-D’ŒUVRE", ["Effectifs", "Affectation", "Équilibrage"]),
        ("DÉTECTION ANOMALIES\n& RISQUES", ["Anomalies", "Écarts processus", "Risques", "Tableaux de bord"]),
    ]
    ai_svg = []
    for i, (title, items) in enumerate(ai):
        x = 295 + i * 238
        ai_svg.append(rect(x, 890, 215, 135, fill="#FCFAFF", stroke=VIOLET, rx=8))
        ai_svg.append(svg_text(x + 107, 916, title.split("\n"), size=12, weight="700", fill=VIOLET, anchor="middle", line_height=14))
        ai_svg.append(svg_text(x + 18, 955, [f"• {item}" for item in items], size=11, fill=TEXT, line_height=18))

    field_devices = ["Terminaux RF", "Scanners codes-barres / QR", "Lecteurs RFID", "Capteurs", "Caméras / vision", "Balances / pesage", "Systèmes vocaux", "Smartphone / Tablet", "Pick-to-Light / Put-to-Light", "Vehicle terminal"]
    devices_svg = []
    for i, item in enumerate(field_devices):
        col = i % 5
        row = i // 5
        x = 365 + col * 210
        y = 1120 + row * 58
        devices_svg.append(rect(x, y, 170, 44, fill="#DDF7E7", stroke=TEAL, rx=12))
        devices_svg.append(svg_text(x + 85, y + 28, item, size=13, fill="#00605C", anchor="middle"))

    write_svg_asset("chapitre4/architecture_fonctionnelle.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1260">
      {svg_defs()}
      <rect width="1600" height="1260" fill="#F7F9FC"/>
      {svg_text(800, 48, "ARCHITECTURE FONCTIONNELLE CIBLE DU SMART WMS", size=30, weight="800", fill=NAVY, anchor="middle")}
      {rect(25, 85, 220, 150, fill="white", stroke=NAVY, rx=8)}
      {svg_text(52, 127, ["SYSTÈMES", "EXTERNES"], size=21, weight="700", fill=NAVY)}
      {svg_text(52, 180, ["Systèmes métiers et", "d’entreprise"], size=14, fill=TEXT)}
      {rect(275, 85, 1295, 150, fill="white", stroke=NAVY, rx=8)}
      {''.join(ext)}
      {arrow(370, 236, 370, 260)}
      {arrow(560, 236, 560, 260)}
      {arrow(750, 236, 750, 260)}
      {arrow(940, 236, 940, 260)}
      {arrow(1130, 236, 1130, 260)}
      {arrow(1320, 236, 1320, 260)}
      {svg_text(800, 255, "Commandes / plan directeur / confirmations • Statuts / événements / traçabilité / indicateurs", size=14, fill=NAVY, anchor="middle")}
      {rect(25, 270, 220, 430, fill="white", stroke=RED, rx=8)}
      {svg_text(52, 410, ["CŒUR OPÉRATIONNEL", "DU WMS"], size=18, weight="700", fill=RED)}
      {svg_text(52, 485, ["Gérer et exécuter", "les processus entrepôt"], size=14, fill=NAVY)}
      {''.join(core)}
      {rect(1225, 270, 345, 245, fill="white", stroke=RED, rx=8)}
      {svg_text(1397, 305, "DONNÉES DE RÉFÉRENCE", size=15, weight="700", fill=RED, anchor="middle")}
      {svg_text(1260, 340, ["• Produits / articles", "• Clients", "• Fournisseurs", "• Emplacements / zones", "• Unités logistiques", "• Règles / politiques", "• Utilisateurs / rôles"], size=12, fill=TEXT, line_height=22)}
      {rect(1225, 535, 345, 165, fill="#FAF7FF", stroke=VIOLET, rx=8)}
      {svg_text(1397, 570, "STOCKAGE DES DONNÉES", size=15, weight="700", fill=NAVY, anchor="middle")}
      {rect(1260, 610, 115, 72, fill="white", stroke="#777", rx=26)}
      {rect(1410, 610, 115, 72, fill="white", stroke="#777", rx=26)}
      {svg_text(1318, 656, ["Base", "OLTP"], size=12, fill=TEXT, anchor="middle")}
      {svg_text(1468, 656, ["Base", "OLAP/DWH"], size=12, fill=TEXT, anchor="middle")}
      {rect(285, 620, 922, 62, fill="white", stroke=RED, rx=4)}
      {svg_text(746, 655, "GESTION DES TÂCHES & DES TRAVAUX", size=17, weight="700", fill=RED, anchor="middle")}
      {svg_text(746, 680, "création • affectation • exécution • suivi des statuts • exceptions", size=12, fill=TEXT, anchor="middle")}
      {rect(25, 690, 220, 145, fill="white", stroke=GREEN, rx=8)}
      {svg_text(52, 742, ["RESSOURCES &", "INFRASTRUCTURES"], size=18, weight="700", fill=GREEN)}
      {svg_text(52, 792, ["Personnes, équipements", "et actifs"], size=14, fill=NAVY)}
      {''.join(support_svg)}
      {rect(25, 890, 220, 145, fill="white", stroke=VIOLET, rx=8)}
      {svg_text(52, 935, ["INTELLIGENCE &", "AIDE À LA DÉCISION"], size=18, weight="700", fill=VIOLET)}
      {svg_text(52, 990, ["Analyser, prédire,", "optimiser, décider"], size=14, fill=NAVY)}
      {''.join(ai_svg)}
      {rect(25, 1095, 220, 145, fill="white", stroke=NAVY, rx=8)}
      {svg_text(52, 1140, ["TERMINAUX &", "APPAREILS TERRAIN"], size=18, weight="700", fill=TEAL)}
      {rect(300, 1085, 1240, 155, fill="#FFFFFF", stroke="#5A636D", rx=36)}
      {''.join(devices_svg)}
    </svg>
    """)

    write_svg_asset("chapitre4/activation_progressive.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520">
      {svg_defs()}
      <rect width="1200" height="520" fill="white"/>
      {svg_text(600, 46, "Activation progressive des capacités Smart WMS", size=26, weight="800", fill=NAVY, anchor="middle")}
      {rect(100, 105, 280, 210, fill="#F4F8FC", stroke=NAVY, rx=18)}
      <rect x="100" y="105" width="280" height="58" fill="{NAVY}" rx="18"/>
      {svg_text(240, 129, ["Niveau 1", "Socle WMS"], size=17, weight="700", fill="white", anchor="middle", line_height=20)}
      {svg_text(240, 220, ["réception, stock,", "commandes, tâches,", "données de référence"], size=16, fill=TEXT, anchor="middle")}
      {arrow(402, 210, 465, 210)}
      {rect(480, 105, 280, 210, fill="#FAF7FF", stroke=VIOLET, rx=18)}
      <rect x="480" y="105" width="280" height="58" fill="{VIOLET}" rx="18"/>
      {svg_text(620, 129, ["Niveau 2", "Smart data-driven"], size=17, weight="700", fill="white", anchor="middle", line_height=20)}
      {svg_text(620, 220, ["prévision, slotting,", "priorisation,", "détection d’anomalies"], size=16, fill=TEXT, anchor="middle")}
      {arrow(782, 210, 845, 210)}
      {rect(860, 105, 280, 210, fill="#FFF7EF", stroke=ORANGE, rx=18)}
      <rect x="860" y="105" width="280" height="58" fill="{ORANGE}" rx="18"/>
      {svg_text(1000, 129, ["Niveau 3", "Automatisation optionnelle"], size=17, weight="700", fill="white", anchor="middle", line_height=20)}
      {svg_text(1000, 220, ["RFID, vision, AMR/AGV,", "WCS/WES, BMS/EMS"], size=16, fill=TEXT, anchor="middle")}
      {rect(235, 375, 730, 70, fill="#F7FCFB", stroke=TEAL, rx=14)}
      {svg_text(600, 416, "Le passage d’un niveau à l’autre dépend des données, des contraintes produit, des équipements et de la maturité opérationnelle.", size=16, fill=TEXT, anchor="middle")}
    </svg>
    """)

    write_svg_asset("chapitre5/vue_modelisation_uml.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 650">
      {svg_defs()}
      <rect width="1300" height="650" fill="white"/>
      {svg_text(650, 48, "Vue de modélisation UML retenue pour le Smart WMS", size=27, weight="800", fill=NAVY, anchor="middle")}
      {rect(500, 105, 300, 90, fill="#F4F8FC", stroke=NAVY, rx=18)}
      {svg_text(650, 142, "Architecture fonctionnelle", size=20, weight="700", fill=NAVY, anchor="middle")}
      {svg_text(650, 168, "blocs, responsabilités, interfaces", size=14, fill=TEXT, anchor="middle")}
      {rect(90, 270, 250, 118, fill="#F4F8FC", stroke=NAVY, rx=16)}
      {svg_text(215, 308, "Cas d’utilisation", size=18, weight="700", fill=NAVY, anchor="middle")}
      {svg_text(215, 340, ["acteurs, périmètre,", "Core / Smart / Optional"], size=14, fill=TEXT, anchor="middle")}
      {rect(385, 270, 250, 118, fill="#FFF7EF", stroke=ORANGE, rx=16)}
      {svg_text(510, 308, "Activités", size=18, weight="700", fill=ORANGE, anchor="middle")}
      {svg_text(510, 340, ["workflow métier,", "exceptions, décisions"], size=14, fill=TEXT, anchor="middle")}
      {rect(680, 270, 250, 118, fill="#F7FCFB", stroke=TEAL, rx=16)}
      {svg_text(805, 308, "Séquences", size=18, weight="700", fill=TEAL, anchor="middle")}
      {svg_text(805, 340, ["échanges entre acteurs,", "WMS et systèmes"], size=14, fill=TEXT, anchor="middle")}
      {rect(975, 270, 250, 118, fill="#FAF7FF", stroke=VIOLET, rx=16)}
      {svg_text(1100, 308, "Domaine & composants", size=18, weight="700", fill=VIOLET, anchor="middle")}
      {svg_text(1100, 340, ["objets métier,", "services applicatifs"], size=14, fill=TEXT, anchor="middle")}
      {arrow(650, 195, 215, 270)}
      {arrow(650, 195, 510, 270)}
      {arrow(650, 195, 805, 270)}
      {arrow(650, 195, 1100, 270)}
      {rect(260, 485, 780, 82, fill="#F6F8FB", stroke="#AAB4C0", rx=18)}
      {svg_text(650, 517, "Traçabilité", size=19, weight="700", fill=TEXT, anchor="middle")}
      {svg_text(650, 546, "Problème métier → use case → activité → interaction → composant applicatif", size=16, fill=TEXT, anchor="middle")}
    </svg>
    """)

    write_svg_asset("chapitre6/architecture_applicative_logique.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 770">
      {svg_defs()}
      <rect width="1300" height="770" fill="white"/>
      {svg_text(650, 45, "Architecture applicative logique proposée", size=27, weight="800", fill=NAVY, anchor="middle")}
      {rect(90, 95, 1120, 78, fill="#F4F8FC", stroke=NAVY, rx=16)}
      {svg_text(650, 127, "Canaux utilisateurs", size=19, weight="700", fill=NAVY, anchor="middle")}
      {svg_text(650, 153, "dashboard superviseur • terminaux RF/tablette • API partenaires", size=15, fill=TEXT, anchor="middle")}
      {arrow(650, 173, 650, 213)}
      {rect(90, 215, 1120, 88, fill="#FFFFFF", stroke=TEAL, rx=16)}
      {svg_text(650, 250, "API & orchestration", size=19, weight="700", fill=TEAL, anchor="middle")}
      {svg_text(650, 277, "validation requêtes • authentification • orchestration tâches/outils • journalisation", size=15, fill=TEXT, anchor="middle")}
      {arrow(650, 303, 650, 345)}
      {rect(90, 345, 340, 145, fill="#FFF7F7", stroke=RED, rx=16)}
      {svg_text(260, 380, "Services métier WMS", size=18, weight="700", fill=RED, anchor="middle")}
      {svg_text(260, 412, ["réception", "stock & inventaire", "commandes", "tâches", "expédition"], size=14, fill=TEXT, anchor="middle", line_height=19)}
      {rect(480, 345, 340, 145, fill="#FAF7FF", stroke=VIOLET, rx=16)}
      {svg_text(650, 380, "Services Smart", size=18, weight="700", fill=VIOLET, anchor="middle")}
      {svg_text(650, 412, ["prévision", "optimisation", "anomalies", "recommandations", "agent explicatif"], size=14, fill=TEXT, anchor="middle", line_height=19)}
      {rect(870, 345, 340, 145, fill="#F7FCFB", stroke=TEAL, rx=16)}
      {svg_text(1040, 380, "Intégrations", size=18, weight="700", fill=TEAL, anchor="middle")}
      {svg_text(1040, 412, ["ERP / SAP", "MES", "TMS / YMS", "WCS / WES", "BMS / EMS"], size=14, fill=TEXT, anchor="middle", line_height=19)}
      {arrow(260, 490, 260, 535)}
      {arrow(650, 490, 650, 535)}
      {arrow(1040, 490, 1040, 535)}
      {rect(90, 535, 1120, 88, fill="#F6F8FB", stroke="#AAB4C0", rx=16)}
      {svg_text(650, 568, "Couche données", size=19, weight="700", fill=TEXT, anchor="middle")}
      {svg_text(650, 595, "base OLTP • référentiel documentaire/RAG • entrepôt analytique OLAP-DWH • logs & événements", size=15, fill=TEXT, anchor="middle")}
      {rect(190, 665, 920, 60, fill="#FFF9F1", stroke=ORANGE, rx=14)}
      {svg_text(650, 702, "Principe de sécurité : outils lecture seule, décisions déterministes, validation humaine avant action sensible.", size=16, fill=TEXT, anchor="middle")}
    </svg>
    """)

    write_svg_asset("chapitre7/chaine_validation.svg", f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1250 420">
      {svg_defs()}
      <rect width="1250" height="420" fill="white"/>
      {svg_text(625, 45, "Chaîne de validation proposée", size=26, weight="800", fill=NAVY, anchor="middle")}
      {rect(70, 130, 210, 110, fill="#F4F8FC", stroke=NAVY, rx=15)}
      {svg_text(175, 170, "Scénario métier", size=18, weight="700", fill=NAVY, anchor="middle")}
      {svg_text(175, 200, ["réception", "stock", "expédition"], size=14, fill=TEXT, anchor="middle")}
      {arrow(292, 185, 355, 185)}
      {rect(370, 130, 210, 110, fill="#F7FCFB", stroke=TEAL, rx=15)}
      {svg_text(475, 170, "Use cases", size=18, weight="700", fill=TEAL, anchor="middle")}
      {svg_text(475, 200, ["Core / Smart", "Optional"], size=14, fill=TEXT, anchor="middle")}
      {arrow(592, 185, 655, 185)}
      {rect(670, 130, 210, 110, fill="#FAF7FF", stroke=VIOLET, rx=15)}
      {svg_text(775, 170, "UML", size=18, weight="700", fill=VIOLET, anchor="middle")}
      {svg_text(775, 200, ["activité", "séquence", "composants"], size=14, fill=TEXT, anchor="middle")}
      {arrow(892, 185, 955, 185)}
      {rect(970, 130, 210, 110, fill="#FFF7EF", stroke=ORANGE, rx=15)}
      {svg_text(1075, 170, "Prototype / revue", size=18, weight="700", fill=ORANGE, anchor="middle")}
      {svg_text(1075, 200, ["règles testables", "retours encadrante"], size=14, fill=TEXT, anchor="middle")}
      {rect(190, 310, 870, 54, fill="#F6F8FB", stroke="#AAB4C0", rx=12)}
      {svg_text(625, 344, "La validation cherche la cohérence métier avant le choix technique définitif.", size=16, fill=TEXT, anchor="middle")}
    </svg>
    """)


LATEX_FILES = {
    CONFIG / "packages.tex": r"""
        \usepackage[utf8]{inputenc}
        \usepackage[T1]{fontenc}
        \usepackage[french]{babel}
        \usepackage{lmodern}
        \usepackage[a4paper,margin=2.35cm,headheight=18pt]{geometry}
        \usepackage{graphicx}
        \usepackage{xcolor}
        \usepackage{tabularx}
        \usepackage{longtable}
        \usepackage{booktabs}
        \usepackage{array}
        \usepackage{enumitem}
        \usepackage{fancyhdr}
        \usepackage{hyperref}
        \usepackage{caption}
        \usepackage{float}
        \usepackage{pdflscape}
        \usepackage[most]{tcolorbox}
        \usepackage{tikz}
    """,
    CONFIG / "style.tex": r"""
        \definecolor{SmartNavy}{HTML}{173F66}
        \definecolor{SmartTeal}{HTML}{2A837C}
        \definecolor{SmartRed}{HTML}{D7261E}
        \definecolor{SmartViolet}{HTML}{7D60C8}
        \definecolor{SmartOrange}{HTML}{EE8626}
        \definecolor{SmartGreen}{HTML}{5D9A50}
        \definecolor{SmartLight}{HTML}{F6F8FB}

        \hypersetup{colorlinks=true, linkcolor=SmartNavy, urlcolor=SmartTeal, citecolor=SmartNavy}
        \setlength{\parindent}{0pt}
        \setlength{\parskip}{0.62em}
        \renewcommand{\arraystretch}{1.18}
        \captionsetup{font=small,labelfont=bf,textfont=it}

        \pagestyle{fancy}
        \fancyhf{}
        \lhead{\small Rapport de stage}
        \rhead{\small Smart WMS}
        \cfoot{\thepage}
        \renewcommand{\headrulewidth}{0.4pt}

        \newtcolorbox{problematique}{
          colback=SmartLight,
          colframe=SmartNavy,
          boxrule=0.8pt,
          arc=2mm,
          title=Problématique directrice,
          fonttitle=\bfseries
        }
    """,
    CONFIG / "commands.tex": r"""
        \newcommand{\studentName}{FERHAN Abdelali}
        \newcommand{\schoolName}{ENIAD -- École Nationale de l'Intelligence Artificielle \& du Digital, Berkane}
        \newcommand{\internshipCompany}{Smart Automation Technologies, Tanger}
        \newcommand{\internshipPeriod}{Août -- octobre 2026}
        \newcommand{\reportTitle}{Conception d'une Architecture Intelligente pour la Transformation d'un Warehouse Management System Traditionnel en Smart WMS}
        \newcommand{\reportSubtitle}{Modélisation métier, fonctionnelle et applicative}
    """,
}


def latex_chapters() -> dict[Path, str]:
    return {
        CHAPTERS / "00_remerciements.tex": r"""
        \chapter*{Remerciements}
        Je tiens à remercier l'équipe de Smart Automation Technologies pour son accueil, son accompagnement et les échanges qui ont permis de cadrer progressivement le sujet du stage. Je remercie particulièrement mon encadrante en entreprise, Chaimae Kaina, pour ses remarques sur la cohérence métier, la lisibilité des modèles et la nécessité de distinguer clairement le socle WMS des capacités avancées.

        Je remercie également l'ENIAD pour le cadre pédagogique de cette expérience, ainsi que toutes les personnes ayant contribué, directement ou indirectement, à l'avancement de ce travail.
        """,
        CHAPTERS / "01_introduction.tex": r"""
        \chapter*{Introduction générale}
        La gestion d'un entrepôt ne se limite plus à enregistrer des entrées et des sorties de marchandises. Un entrepôt moderne doit connaître l'état du stock, organiser les emplacements, préparer les commandes, coordonner les opérateurs et les équipements, prendre en compte les contraintes propres aux produits et échanger avec plusieurs systèmes de l'entreprise. Dans ce contexte, le Warehouse Management System (WMS) joue un rôle central : il structure les opérations depuis la réception jusqu'à l'expédition et assure la traçabilité des mouvements.

        Un WMS traditionnel couvre déjà les fonctions essentielles : réception, contrôle, mise en stock, gestion des emplacements, inventaire, réapprovisionnement, allocation, picking, packing et expédition. La transformation vers un Smart WMS ne consiste donc pas à remplacer ce socle par une intelligence artificielle généralisée. Elle consiste plutôt à renforcer le système par des capacités activables lorsque le besoin, les données et l'infrastructure le justifient : prévision de charge, optimisation de slotting, détection d'anomalies, supervision énergétique, vision industrielle, RFID ou orchestration avec WCS/WES.

        Le stage réalisé au sein de Smart Automation Technologies s'inscrit dans cette logique. L'objectif principal est de concevoir une architecture de référence capable de guider la transformation d'un WMS traditionnel vers un Smart WMS. Le travail porte sur la conception métier, fonctionnelle et applicative logique ; il ne vise pas le développement complet d'un produit WMS industriel.

        \begin{problematique}
        Comment concevoir une architecture Smart WMS suffisamment complète pour couvrir les fonctions essentielles d'un entrepôt, tout en restant générique, modulaire et adaptable aux contraintes produits, aux données disponibles et au niveau d'automatisation de chaque entreprise ?
        \end{problematique}

        La démarche adoptée suit une logique SCAN -- PLAN -- ACT. La phase SCAN a permis de comprendre les solutions WMS leaders et les limites d'un WMS classique. La phase PLAN a structuré les besoins, les use cases et l'architecture fonctionnelle cible. La phase ACT prépare la validation du modèle, la modélisation UML et une architecture applicative logique pouvant servir de base à une future implémentation.
        """,
        CHAPTERS / "02_chapitre1_organisme.tex": r"""
        \chapter{Présentation de l'organisme d'accueil et cadrage du stage}
        \section{Présentation générale de Smart Automation Technologies}
        Smart Automation Technologies (SAT) est une startup technologique située à Tanger. Elle intervient dans les domaines de la transformation digitale, de l'architecture des systèmes d'information, de la data science et de l'intelligence artificielle. Son positionnement est celui d'un partenaire technologique capable d'accompagner les organisations depuis la compréhension du besoin jusqu'à la conception de solutions adaptées.

        Ce contexte est cohérent avec le sujet du stage, car la transformation d'un WMS vers un Smart WMS exige d'abord une compréhension métier solide. Il ne suffit pas d'ajouter des technologies à un processus existant ; il faut identifier les problèmes opérationnels, les données disponibles, les dépendances avec les systèmes externes et les conditions réelles d'activation des capacités avancées.

        \section{Contexte et périmètre du stage}
        Le stage couvre la période d'août à octobre 2026 et porte sur la conception d'une architecture intelligente pour transformer un WMS traditionnel en Smart WMS. Le périmètre est volontairement centré sur la modélisation métier, fonctionnelle et applicative logique. Les choix définitifs de technologie, de base de données, d'infrastructure cloud ou d'équipement physique restent hors périmètre à ce stade.

        \section{Objectifs}
        Les objectifs opérationnels du stage sont les suivants :
        \begin{itemize}[leftmargin=1.2cm]
          \item réaliser un benchmark fonctionnel des solutions WMS leaders ;
          \item identifier les fonctions communes et les limites d'un WMS traditionnel ;
          \item formaliser les use cases Core, Smart et Optional ;
          \item proposer une architecture fonctionnelle cible modulaire ;
          \item préparer une modélisation UML cohérente ;
          \item traduire la cible fonctionnelle vers une architecture applicative logique.
        \end{itemize}

        \section{Livrables}
        Les livrables attendus sont un benchmark WMS, une cartographie des use cases, une architecture fonctionnelle cible, des modèles UML et une proposition d'architecture applicative. Le projet logiciel local SmartWMS AI Operations Agent est traité comme une maquette d'aide à la décision : il démontre certains principes d'outillage, de règles déterministes et d'agent conversationnel, sans prétendre constituer un WMS complet.
        """,
        CHAPTERS / "03_chapitre2_benchmark.tex": r"""
        \chapter{État de l'art et benchmark des solutions WMS}
        \section{WMS classique et Smart WMS}
        Un WMS classique structure les flux inbound, internes et outbound. Il assure la réception, la mise en stock, l'inventaire, le réapprovisionnement, l'allocation, la préparation, le packing et l'expédition. Un Smart WMS conserve ces responsabilités mais ajoute une capacité d'analyse et d'adaptation : il peut prévoir une charge, détecter une anomalie, optimiser une affectation ou recommander une action.

        La différence principale n'est donc pas la présence d'un algorithme. Elle réside dans la capacité du système à transformer des données fiables en décisions opérationnelles exécutables.

        \section{Solutions étudiées}
        Le benchmark a porté sur Manhattan Active Warehouse Management, SAP Extended Warehouse Management et Oracle Warehouse Management Cloud. L'objectif n'était pas de produire un classement commercial, mais d'extraire des principes de conception applicables à une architecture générique.

        \begin{table}[H]
        \centering
        \caption{Synthèse des apports retenus du benchmark}
        \begin{tabularx}{\linewidth}{>{\bfseries}p{3.2cm}X X}
        \toprule
        Solution & Idée directrice & Apport pour le projet \\
        \midrule
        Manhattan Active WMS & Unification de l'exécution & Relier stocks, tâches, opérateurs, équipements et décisions dans une boucle courte décision -- action. \\
        SAP EWM & Richesse du modèle métier & Donner une place centrale aux objets métier : produit, lot, HU, emplacement, ressource, règle et tâche. \\
        Oracle WMS Cloud & Orchestration commande -- wave -- allocation -- tâches & Montrer comment transformer une demande client en travail coordonné et mesurable. \\
        \bottomrule
        \end{tabularx}
        \end{table}

        \section{Enseignements pour l'architecture cible}
        Trois enseignements structurent la suite du rapport. Premièrement, le socle WMS doit rester stable et complet. Deuxièmement, la donnée de référence est un prérequis de l'intelligence : une optimisation n'a pas de sens si les produits, emplacements, lots et règles sont mal représentés. Troisièmement, les capacités Smart doivent être reliées à la gestion des tâches pour produire une action concrète, et non seulement un indicateur dans un tableau de bord.
        """,
        CHAPTERS / "04_chapitre3_besoins_use_cases.tex": r"""
        \chapter{Analyse des besoins et identification des use cases}
        \section{Approche SCAN -- PLAN -- ACT}
        La démarche d'identification des besoins a consisté à passer d'une observation générale du domaine WMS vers des use cases traçables. La figure~\ref{fig:scan-plan-act} synthétise cette progression.

        \begin{figure}[H]
        \centering
        \includegraphics[width=0.92\linewidth]{figures/chapitre3/demarche_scan_plan_act.pdf}
        \caption{Application de la démarche SCAN -- PLAN -- ACT à l'identification et à la validation des besoins.}
        \label{fig:scan-plan-act}
        \end{figure}

        \section{Logique de classification}
        La classification Core / Smart / Optional évite de confondre une fonction indispensable avec une capacité avancée ou dépendante d'une infrastructure. Le Core correspond aux capacités nécessaires au fonctionnement du WMS. Le Smart améliore la décision grâce aux données, à l'optimisation ou au machine learning. L'Optional dépend d'un équipement ou d'un système particulier : caméra 3D, RFID, AMR/AGV, WCS/WES ou BMS/EMS.

        \begin{figure}[H]
        \centering
        \includegraphics[width=\linewidth]{figures/chapitre3/classification_activation.pdf}
        \caption{Logique Core / Smart / Optional et principe d'activation selon les données et l'infrastructure.}
        \label{fig:classification}
        \end{figure}

        \section{Cartographie des use cases}
        Les tableaux suivants conservent la numérotation validée pendant le stage.

        \begin{longtable}{p{2.2cm}p{9.2cm}p{3cm}}
        \caption{Use cases Réception}\\
        \toprule
        ID & Use case & Type \\
        \midrule
        UC-R01 & Planifier rendez-vous et quai & Core \\
        UC-R02 & Réceptionner les marchandises & Core \\
        UC-R03 & Identifier le produit & Core \\
        UC-R04 & Contrôler la quantité & Core \\
        UC-R05 & Contrôler la qualité & Core \\
        UC-R06 & Gérer une anomalie de réception & Core \\
        UC-R07 & Proposer emplacement de stockage & Core \\
        UC-R08 & Prévoir la charge de réception & Smart \\
        UC-R09 & Compter les cartons par caméra 3D & Optional \\
        UC-R10 & Lire l'étiquette par OCR & Optional \\
        UC-R11 & Détecter les défauts par vision & Optional \\
        UC-R12 & Suivre le conteneur connecté & Optional \\
        \bottomrule
        \end{longtable}

        \begin{longtable}{p{2.2cm}p{9.2cm}p{3cm}}
        \caption{Use cases Stockage et Inventaire}\\
        \toprule
        ID & Use case & Type \\
        \midrule
        UC-S01 & Mettre en stock / putaway & Core \\
        UC-S02 & Gérer les stocks & Core \\
        UC-S03 & Gérer les emplacements & Core \\
        UC-S04 & Réaliser l'inventaire tournant & Core \\
        UC-S05 & Réapprovisionner la zone picking & Core \\
        UC-S06 & Détecter la congestion d'une zone & Smart \\
        UC-S07 & Surveiller les produits sensibles & Core conditionnel \\
        UC-S08 & Gérer lots / DLC / FEFO & Core conditionnel \\
        UC-S09 & Choisir l'emplacement optimal / slotting & Smart \\
        UC-S10 & Cibler les emplacements à recompter & Smart \\
        UC-S11 & Prédire une rupture avant blocage & Smart \\
        UC-S12 & Chercher un emplacement alternatif & Smart \\
        UC-S13 & Suivre les palettes par RFID & Optional \\
        UC-S14 & Déplacer le stock par AMR / AGV & Optional \\
        \bottomrule
        \end{longtable}

        \begin{longtable}{p{2.2cm}p{9.2cm}p{3cm}}
        \caption{Use cases Commandes et Expédition}\\
        \toprule
        ID & Use case & Type \\
        \midrule
        UC-E01 & Recevoir la commande client & Core \\
        UC-E02 & Planifier la commande & Core \\
        UC-E03 & Créer la wave / batch & Core \\
        UC-E04 & Allouer le stock & Core \\
        UC-E05 & Créer tâches de picking & Core \\
        UC-E06 & Effectuer le picking & Core \\
        UC-E07 & Effectuer le packing & Core \\
        UC-E08 & Charger le camion & Core \\
        UC-E09 & Expédier la commande & Core \\
        UC-E10 & Guider le picking RF / Pick-to-Light & Optional \\
        UC-E11 & Optimiser le parcours picking & Smart \\
        UC-E12 & Contrôler le picking scan / poids / vision & Optional \\
        UC-E13 & Recommander l'emballage & Smart \\
        UC-E14 & Contrôler le chargement scan / caméra & Optional \\
        UC-E15 & Détecter commandes à risque de retard & Smart \\
        \bottomrule
        \end{longtable}

        \begin{table}[H]
        \centering
        \caption{Synthèse des catégories et critères d'activation par domaine}
        \begin{tabularx}{\linewidth}{p{3cm}X X X}
        \toprule
        Domaine & Core & Smart & Optional / infrastructure \\
        \midrule
        Réception & UC-R01--UC-R07 & UC-R08 & UC-R09--UC-R12 \\
        Stockage & UC-S01--UC-S05, UC-S07--UC-S08 & UC-S06, UC-S09--UC-S12 & UC-S13--UC-S14 \\
        Commandes & UC-E01--UC-E09 & UC-E11, UC-E13, UC-E15 & UC-E10, UC-E12, UC-E14 \\
        Yard & UC-Y01--UC-Y04 & UC-Y06--UC-Y07 & UC-Y05 \\
        Ressources & UC-RES01--03, UC-RES05--06, UC-RES08 & UC-RES04 & UC-RES07, UC-RES09--10 \\
        \bottomrule
        \end{tabularx}
        \end{table}
        """,
        CHAPTERS / "05_chapitre4_architecture_fonctionnelle.tex": r"""
        \chapter{Architecture fonctionnelle cible du Smart WMS}
        \section{Principes de conception}
        L'architecture cible est construite comme un système modulaire. Elle doit pouvoir s'appliquer à un entrepôt simple utilisant des terminaux RF, mais aussi à un site automatisé intégrant RFID, convoyeurs, AMR/AGV, WCS/WES ou BMS/EMS. Le modèle distingue donc les blocs fonctionnels stables, les services Smart activables par la donnée et les options dépendantes de l'infrastructure.

        \section{Vue d'ensemble}
        La figure~\ref{fig:architecture-fonctionnelle} redessine la vue fonctionnelle cible à partir de l'architecture validée dans le support de benchmark. Contrairement à une représentation trop compacte, elle sépare explicitement les systèmes externes, le cœur opérationnel, la gestion des tâches, les données de référence, le stockage des données, les ressources et infrastructures, l'intelligence décisionnelle et les appareils terrain.

        \begin{landscape}
        \begin{figure}[p]
        \centering
        \includegraphics[width=0.98\linewidth]{figures/chapitre4/architecture_fonctionnelle.pdf}
        \caption{Architecture fonctionnelle cible du Smart WMS proposée.}
        \label{fig:architecture-fonctionnelle}
        \end{figure}
        \end{landscape}

        \section{Rôle des couches}
        Les systèmes externes alimentent le WMS en commandes, statuts, confirmations, informations transport, production et référentiels. Le cœur opérationnel exécute les processus d'entrepôt : réception, stockage, inventaire, commandes, préparation, expédition et yard. La gestion des tâches transforme les décisions en actions exécutables et assure le suivi des statuts et exceptions.

        Les données de référence ne sont pas traitées comme des use cases artificiels. Elles constituent une couche de support essentielle : produits, clients, fournisseurs, zones, règles, unités logistiques, utilisateurs et rôles. Le stockage est séparé en deux usages : l'OLTP pour l'exécution transactionnelle et l'OLAP/DWH pour l'historique, les KPI, l'analyse et les modèles prédictifs.

        \section{Activation progressive}
        L'architecture doit rester utile même lorsque toutes les technologies ne sont pas disponibles. La figure~\ref{fig:activation-progressive} formalise cette progressivité.

        \begin{figure}[H]
        \centering
        \includegraphics[width=0.92\linewidth]{figures/chapitre4/activation_progressive.pdf}
        \caption{Principe d'activation progressive des capacités Smart WMS.}
        \label{fig:activation-progressive}
        \end{figure}

        \begin{table}[H]
        \centering
        \caption{Responsabilités des blocs fonctionnels de l'architecture cible}
        \begin{tabularx}{\linewidth}{p{3.4cm}X X}
        \toprule
        Bloc & Responsabilité principale & Contribution au Smart WMS \\
        \midrule
        Cœur opérationnel & Exécuter réception, stock, commandes, yard et expédition & Stabiliser le socle métier indispensable \\
        Gestion des tâches & Créer, affecter, suivre et traiter les exceptions & Transformer décisions et alertes en actions \\
        Données de référence & Structurer produits, zones, règles, rôles et unités logistiques & Donner le contexte aux règles et optimisations \\
        Ressources & Gérer main-d'œuvre, équipements, actifs et interfaces & Adapter le système au niveau réel d'automatisation \\
        Intelligence & Prévoir, optimiser, détecter et recommander & Améliorer la qualité des décisions opérationnelles \\
        Terrain & Capturer les données et guider l'exécution & Relier le numérique au flux physique \\
        \bottomrule
        \end{tabularx}
        \end{table}
        """,
        CHAPTERS / "06_chapitre5_modelisation_uml.tex": r"""
        \chapter{Modélisation UML}
        \section{Philosophie de modélisation}
        La modélisation UML sert à rendre la cible fonctionnelle vérifiable. Les diagrammes ne doivent pas seulement illustrer le rapport ; ils doivent permettre de contrôler que chaque besoin métier possède un acteur, un processus, des interactions et, lorsque nécessaire, un composant applicatif.

        \begin{figure}[H]
        \centering
        \includegraphics[width=0.92\linewidth]{figures/chapitre5/vue_modelisation_uml.pdf}
        \caption{Vue de modélisation UML retenue pour le Smart WMS.}
        \label{fig:vue-uml}
        \end{figure}

        \section{Diagrammes de cas d'utilisation}
        Les diagrammes de cas d'utilisation sont organisés par domaine : vue globale, réception, stockage et inventaire, préparation et expédition, services transversaux, yard et ressources. La correction principale consiste à séparer visuellement les use cases Core, Smart et Optional. Les blocs Données de référence et Stockage des données ne sont pas représentés comme des cas d'utilisation déclenchés par un acteur ; ils relèvent du modèle de domaine et du diagramme de composants.

        \section{Diagrammes d'activité}
        Les diagrammes d'activité décrivent les flux de bout en bout : réception intelligente, stockage et inventaire, expédition, supervision énergétique et environnementale. Leur intérêt est de montrer les alternatives : règle métier standard lorsqu'aucune infrastructure avancée n'est disponible, puis activation OCR, caméra 3D, RFID, WCS/WES ou BMS/EMS lorsque le contexte le permet.

        \section{Modèle de domaine et composants}
        Le modèle de domaine doit couvrir les objets nécessaires à la cohérence métier : Warehouse, Zone, Location, Product, ProductRequirement, StockUnit, HandlingUnit, Lot, CustomerOrder, OrderLine, Task, Worker, Equipment, Device, Sensor, SensorReading, Alert et Recommendation. Le diagramme de composants traduira ensuite ces objets en services : services métier WMS, services Smart, intégrations externes, couche données et couche terrain.

        Les sources PlantUML utilisées pour cette modélisation sont conservées en annexe afin de faciliter les itérations futures.
        """,
        CHAPTERS / "07_chapitre6_architecture_applicative.tex": r"""
        \chapter{Architecture applicative logique proposée}
        \section{Objectif}
        L'architecture applicative logique traduit la cible fonctionnelle en composants logiciels sans imposer une stack définitive. Elle sert à préparer une future implémentation tout en respectant le périmètre du stage : conception, modélisation et validation.

        \begin{figure}[H]
        \centering
        \includegraphics[width=0.94\linewidth]{figures/chapitre6/architecture_applicative_logique.pdf}
        \caption{Architecture applicative logique proposée pour le Smart WMS.}
        \label{fig:architecture-applicative}
        \end{figure}

        \section{Positionnement du prototype SmartWMS AI Operations Agent}
        Le dépôt local SmartWMS AI Operations Agent illustre une partie de cette architecture : une interface Next.js, une API FastAPI, un runner d'agent, des outils WMS en lecture seule, un moteur de décisions déterministes et un retriever de documents synthétiques. Cette maquette ne constitue pas un WMS complet. Elle démontre surtout comment une couche d'aide à la décision peut consommer des faits structurés sans inventer la logique métier.

        \section{Principes de sûreté}
        Les règles de décision doivent rester testables hors du modèle de langage. Dans la maquette, les calculs de disponibilité, position de stock, demande ouverte, risque de rupture, priorité de réapprovisionnement et quantité de réapprovisionnement sont centralisés dans un service métier déterministe. Le modèle de langage explique les résultats ; il ne crée pas de mouvements de stock et ne prend pas de décision d'achat autonome.
        """,
        CHAPTERS / "08_chapitre7_validation_limites.tex": r"""
        \chapter{Validation, limites et perspectives}
        \section{Méthode de validation}
        La validation proposée repose sur des scénarios métier plutôt que sur un déploiement industriel. Chaque scénario doit être relié à un problème, à un ensemble de use cases, à un diagramme UML et à un composant applicatif.

        \begin{figure}[H]
        \centering
        \includegraphics[width=0.88\linewidth]{figures/chapitre7/chaine_validation.pdf}
        \caption{Chaîne de validation proposée pour l'architecture Smart WMS.}
        \label{fig:validation}
        \end{figure}

        \section{Limites}
        Le benchmark reste limité aux informations disponibles et ne remplace pas une étude détaillée de licences, coûts, performances ou contraintes réglementaires. La modélisation UML n'a pas encore été validée sur un entrepôt réel. Les capacités IA restent conceptuelles ou démontrées par une maquette contrôlée, avec données synthétiques.

        \section{Perspectives}
        Les perspectives naturelles sont la simulation de scénarios réels, la collecte de jeux de données entrepôt, la création d'un dashboard de supervision, l'intégration d'un IoT gateway, l'évaluation de modèles de prévision, puis la connexion progressive avec ERP, WCS/WES ou BMS/EMS. Une attention particulière devra être portée à la qualité des données, à la sécurité, à la supervision humaine et à la traçabilité des recommandations.
        """,
        CHAPTERS / "09_conclusion.tex": r"""
        \chapter*{Conclusion générale}
        Ce stage a permis de structurer une vision cohérente de la transformation d'un WMS traditionnel vers un Smart WMS. Le travail ne s'est pas limité à identifier des technologies avancées ; il a consisté à replacer chaque capacité dans un besoin métier, une condition d'activation et une architecture fonctionnelle claire.

        Le benchmark a montré trois principes complémentaires : l'unification de l'exécution, la richesse du modèle métier et l'orchestration des tâches. L'analyse des besoins a ensuite permis de formaliser les use cases Core, Smart et Optional. L'architecture fonctionnelle cible positionne les systèmes externes, le cœur opérationnel, les tâches, les données, les ressources, l'intelligence et les terminaux terrain dans une structure modulaire.

        La suite du travail consiste à consolider la modélisation UML, valider les scénarios avec des acteurs métier et transformer progressivement l'architecture logique en prototype plus complet. L'apport principal du stage réside dans cette clarification : un Smart WMS robuste n'est pas un WMS auquel on ajoute de l'IA partout, mais un système capable d'utiliser les bonnes données, au bon endroit, pour améliorer les décisions et l'exécution réelle.
        """,
    }


def write_latex_project() -> None:
    for path, content in LATEX_FILES.items():
        write_text(path, content)
    for path, content in latex_chapters().items():
        write_text(path, content)

    write_text(ROOT / "main.tex", r"""
    \documentclass[12pt,a4paper]{report}
    \input{config/packages}
    \input{config/style}
    \input{config/commands}
    \graphicspath{{./}}

    \begin{document}

    \begin{titlepage}
    \centering
    \vspace*{1.5cm}
    {\Large \schoolName \par}
    \vspace{0.4cm}
    {\large Filière : Génie informatique \par}
    \vspace{1.8cm}
    {\Huge\bfseries RAPPORT DE STAGE \par}
    \vspace{1.2cm}
    {\LARGE\bfseries \reportTitle \par}
    \vspace{0.4cm}
    {\Large \reportSubtitle \par}
    \vfill
    \begin{tabular}{rl}
    Étudiant : & \studentName \\
    Organisme d'accueil : & \internshipCompany \\
    Encadrante : & Chaimae Kaina \\
    Période : & \internshipPeriod \\
    \end{tabular}
    \vfill
    {\large Année universitaire 2026}
    \end{titlepage}

    \pagenumbering{roman}
    \input{chapters/00_remerciements}
    \tableofcontents
    \listoffigures
    \listoftables

    \clearpage
    \pagenumbering{arabic}
    \input{chapters/01_introduction}
    \input{chapters/02_chapitre1_organisme}
    \input{chapters/03_chapitre2_benchmark}
    \input{chapters/04_chapitre3_besoins_use_cases}
    \input{chapters/05_chapitre4_architecture_fonctionnelle}
    \input{chapters/06_chapitre5_modelisation_uml}
    \input{chapters/07_chapitre6_architecture_applicative}
    \input{chapters/08_chapitre7_validation_limites}
    \input{chapters/09_conclusion}

    \appendix
    \chapter{Sources PlantUML}
    Les fichiers PlantUML du projet sont conservés dans \texttt{annexes/plantuml}. Ils servent de base aux diagrammes de cas d'utilisation et d'activité et doivent être rendus avec PlantUML lors d'une itération outillée.

    \bibliographystyle{plain}
    \bibliography{bibliography/references}
    \end{document}
    """)

    write_text(BIB / "references.bib", r"""
    @misc{sat2026,
      title = {Document de présentation interne de Smart Automation Technologies},
      year = {2026},
      note = {Document fourni dans le cadre du stage}
    }

    @misc{benchmark2026,
      title = {Support de benchmark Smart Warehouse Management Systems},
      year = {2026},
      note = {Support de travail réalisé pendant le stage}
    }

    @misc{repo2026,
      title = {SmartWMS AI Operations Agent -- dépôt de maquette applicative},
      year = {2026},
      note = {Prototype local FastAPI, Next.js, règles métier déterministes et agent en lecture seule}
    }
    """)

    write_text(ROOT / "README.md", """
    # Rapport Smart WMS

    Ce dossier contient une version restructurée du rapport de stage sous forme de projet LaTeX.

    ## Contenu

    - `main.tex` : point d'entrée LaTeX.
    - `config/` : packages, style et commandes.
    - `chapters/` : chapitres séparés.
    - `figures/` : schémas redessinés en SVG, PDF et PNG.
    - `annexes/plantuml/` : sources PlantUML copiées depuis le dossier `diagramms/`.
    - `build/` : PDF de prévisualisation et HTML de contrôle.

    ## Compilation LaTeX

    Un moteur TeX n'est pas installé sur cette machine au moment de la génération. Après installation
    de TeX Live ou MiKTeX, compiler avec :

    ```powershell
    pdflatex main.tex
    bibtex main
    pdflatex main.tex
    pdflatex main.tex
    ```

    Le PDF présent dans `build/` est une prévisualisation générée localement pour contrôler la mise en page.
    """)

    write_text(ROOT / "CORRECTIONS.md", """
    # Corrections réalisées

    - Reconstruction du rapport en projet LaTeX modulaire.
    - Correction de la figure de classification Core / Smart / Optional : suppression des textes superposés.
    - Redessin complet de l'architecture fonctionnelle à partir de la version validée dans le PPT.
    - Séparation claire entre données de référence, stockage OLTP / OLAP-DWH et use cases métier.
    - Ajout des chapitres de suite : modélisation UML, architecture applicative logique, validation et perspectives.
    - Positionnement du prototype SmartWMS AI Operations Agent comme maquette d'aide à la décision, sans exagérer son périmètre.
    - Copie des sources PlantUML dans les annexes pour les itérations futures.

    # Points à valider manuellement

    - Noms et logos officiels à ajouter sur la couverture si l'école ou l'entreprise fournissent une charte.
    - Références bibliographiques externes à compléter avec les sources officielles réellement consultées.
    - Validation finale des diagrammes UML rendus depuis PlantUML lorsque PlantUML/Graphviz seront disponibles.
    - Validation par l'encadrante de la granularité des chapitres 5 à 7.
    """)


class SmartDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            if flowable.style.name == "ChapterTitle":
                self.notify("TOCEntry", (0, text, self.page))
            elif flowable.style.name == "SectionTitle":
                self.notify("TOCEntry", (1, text, self.page))


def para(text: str, styles, style: str = "Body") -> Paragraph:
    return Paragraph(text.replace("\n", " "), styles[style])


def bullet(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(para(item, styles, "Body"), bulletColor=colors.HexColor(NAVY)) for item in items],
        bulletType="bullet",
        leftIndent=18,
    )


def img_flow(path: Path, max_w: float, max_h: float) -> Image:
    with PILImage.open(path) as im:
        w, h = im.size
    ratio = min(max_w / w, max_h / h)
    return Image(str(path), width=w * ratio, height=h * ratio)


def table_flow(headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> Table:
    header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.4,
        leading=10.5,
        textColor=colors.white,
        alignment=TA_LEFT,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor(TEXT),
        alignment=TA_LEFT,
    )
    data = [
        [Paragraph(html.escape(cell), header_style) for cell in headers],
        *[
            [Paragraph(html.escape(cell), cell_style) for cell in row]
            for row in rows
        ],
    ]
    tbl = Table(data, colWidths=widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.4),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor(TEXT)),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D2DC")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7FA")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tbl


def draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = canvas._pagesize
    canvas.setStrokeColor(colors.HexColor(NAVY))
    canvas.setLineWidth(0.7)
    canvas.line(doc.leftMargin, h - 1.45 * cm, w - doc.rightMargin, h - 1.45 * cm)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor(NAVY))
    canvas.drawRightString(w - doc.rightMargin, h - 1.15 * cm, "RAPPORT DE STAGE | SMART WMS")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5F6B78"))
    canvas.drawRightString(w - doc.rightMargin, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=31,
            textColor=colors.HexColor(NAVY),
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=19,
            textColor=colors.HexColor(TEXT),
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "ChapterTitle": ParagraphStyle(
            "ChapterTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=27,
            textColor=colors.HexColor(NAVY),
            spaceBefore=4,
            spaceAfter=14,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor(TEAL),
            spaceBefore=10,
            spaceAfter=7,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.1,
            leading=14.4,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor(TEXT),
            spaceAfter=7,
        ),
        "Caption": ParagraphStyle(
            "Caption",
            parent=base["Italic"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5F6B78"),
            spaceAfter=8,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=11.2,
            textColor=colors.HexColor(TEXT),
        ),
    }
    return styles


def chapter(story, styles, title: str) -> None:
    story.append(PageBreak())
    story.append(Paragraph(title, styles["ChapterTitle"]))


def section(story, styles, title: str) -> None:
    story.append(Paragraph(title, styles["SectionTitle"]))


def build_pdf_preview() -> Path:
    styles = make_styles()
    pdf_path = BUILD / "Rapport_Stage_FERHAN_Abdelali_Smart_WMS_Revu.pdf"
    doc = SmartDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2.2 * cm,
        bottomMargin=1.8 * cm,
    )
    portrait_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="portrait")
    land = landscape(A4)
    landscape_frame = Frame(1.2 * cm, 1.3 * cm, land[0] - 2.4 * cm, land[1] - 2.5 * cm, id="landscape")
    doc.addPageTemplates(
        [
            PageTemplate(id="Portrait", frames=[portrait_frame], onPage=draw_header_footer, pagesize=A4),
            PageTemplate(id="Landscape", frames=[landscape_frame], onPage=draw_header_footer, pagesize=land),
        ]
    )

    story = []
    story.append(Spacer(1, 2.2 * cm))
    story.append(Paragraph("RAPPORT DE STAGE", styles["Title"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Conception d'une Architecture Intelligente pour la Transformation d'un Warehouse Management System Traditionnel en Smart WMS", styles["Title"]))
    story.append(Paragraph("Modélisation métier, fonctionnelle et applicative", styles["Subtitle"]))
    story.append(Spacer(1, 1.5 * cm))
    info = [
        ["Étudiant", "FERHAN Abdelali"],
        ["Établissement", "ENIAD — École Nationale de l’Intelligence Artificielle & du Digital, Berkane"],
        ["Filière", "Génie informatique"],
        ["Organisme d’accueil", "Smart Automation Technologies — Tanger, Maroc"],
        ["Encadrante", "Chaimae Kaina"],
        ["Période", "Août à octobre 2026"],
    ]
    story.append(table_flow(["Élément", "Information"], info, [4.0 * cm, 11.8 * cm]))
    story.append(PageBreak())

    story.append(Paragraph("Table des matières", styles["ChapterTitle"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC0", fontSize=10.5, leading=14, leftIndent=0, firstLineIndent=0, spaceBefore=5),
        ParagraphStyle(name="TOC1", fontSize=9.4, leading=12, leftIndent=18, firstLineIndent=0),
    ]
    story.append(toc)

    chapter(story, styles, "Introduction générale")
    for p in [
        "La gestion d’un entrepôt ne se limite plus à enregistrer des entrées et des sorties de marchandises. Un entrepôt moderne doit connaître l’état du stock, organiser les emplacements, préparer les commandes, coordonner les opérateurs et les équipements, prendre en compte les contraintes propres aux produits et échanger avec plusieurs systèmes de l’entreprise.",
        "Un WMS traditionnel couvre les fonctions essentielles : réception, contrôle, mise en stock, gestion des emplacements, inventaire, réapprovisionnement, allocation, picking, packing et expédition. La transformation vers un Smart WMS consiste à conserver ce socle tout en ajoutant, lorsque cela apporte une valeur réelle, des capacités de supervision, d’optimisation, de prédiction et de recommandation.",
        "Le périmètre du stage reste centré sur la conception métier, fonctionnelle et applicative logique. Le rapport ne présente donc pas le développement complet d’un WMS industriel ; il construit une base modulaire et vérifiable pour une future phase d’implémentation.",
    ]:
        story.append(para(p, styles))
    story.append(KeepTogether([Paragraph("Problématique directrice", styles["SectionTitle"]), para("Comment concevoir une architecture Smart WMS suffisamment complète pour couvrir les fonctions essentielles d’un entrepôt, tout en restant générique, modulaire et adaptable aux contraintes produits, aux données disponibles et au niveau d’automatisation de chaque entreprise ?", styles)]))

    chapter(story, styles, "1. Présentation de l’organisme d’accueil et cadrage du stage")
    section(story, styles, "1.1 Présentation générale")
    story.append(para("Smart Automation Technologies est une startup technologique située à Tanger. Elle intervient dans la transformation digitale, l’architecture des systèmes d’information, la data science et l’intelligence artificielle. Son positionnement est celui d’un partenaire capable d’accompagner la compréhension du besoin, la conception de solutions et la préparation de leur évolution.", styles))
    section(story, styles, "1.2 Cadrage du stage")
    story.append(para("Le sujet confié porte sur la conception d’une architecture intelligente pour faire évoluer un WMS traditionnel vers un Smart WMS. La difficulté principale était de définir ce que devait signifier le terme « Smart » sans tomber dans une addition de technologies non reliées à un problème métier.", styles))
    story.append(bullet([
        "réaliser un benchmark fonctionnel de solutions WMS leaders ;",
        "identifier les fonctions communes et les limites d’un WMS traditionnel ;",
        "formaliser des use cases Core, Smart et Optional ;",
        "proposer une architecture fonctionnelle cible ;",
        "préparer la modélisation UML et une architecture applicative logique.",
    ], styles))
    section(story, styles, "1.3 Livrables")
    story.append(para("Les livrables sont un benchmark, une cartographie des use cases, une architecture fonctionnelle, des modèles UML et une proposition d’architecture applicative. La maquette SmartWMS AI Operations Agent est présentée comme un démonstrateur d’aide à la décision, non comme un WMS complet.", styles))

    chapter(story, styles, "2. État de l’art et benchmark des solutions WMS")
    section(story, styles, "2.1 Enseignements généraux")
    story.append(para("Le benchmark a porté sur Manhattan Active Warehouse Management, SAP Extended Warehouse Management et Oracle Warehouse Management Cloud. L’objectif n’était pas de produire un classement commercial, mais d’extraire des principes de conception utiles pour une architecture générique.", styles))
    story.append(table_flow(
        ["Solution", "Idée directrice", "Apport retenu"],
        [
            ["Manhattan Active WMS", "Unification de l’exécution", "Relier décisions, tâches, opérateurs, équipements et exécution réelle."],
            ["SAP EWM", "Richesse du modèle métier", "Structurer finement produits, lots, unités logistiques, emplacements, ressources et règles."],
            ["Oracle WMS Cloud", "Orchestration commande → wave → allocation → tâches", "Transformer une demande client en travail coordonné et mesurable."],
        ],
        [4.0 * cm, 5.0 * cm, 7.0 * cm],
    ))
    section(story, styles, "2.2 Principes retenus")
    story.append(para("Trois principes guident la suite du rapport : stabiliser le socle WMS, traiter les données de référence comme une couche fondamentale et relier les capacités Smart à la gestion des tâches pour produire une action opérationnelle.", styles))

    chapter(story, styles, "3. Analyse des besoins et identification des use cases")
    section(story, styles, "3.1 Démarche SCAN — PLAN — ACT")
    story.append(img_flow(FIGURES / "chapitre3/demarche_scan_plan_act.png", doc.width, 7.0 * cm))
    story.append(Paragraph("Figure 3.1 — Application de la démarche SCAN — PLAN — ACT à l’identification et à la validation des besoins.", styles["Caption"]))
    story.append(para("La phase SCAN observe le fonctionnement d’un WMS et les bonnes pratiques du benchmark. La phase PLAN transforme les constats en use cases classés. La phase ACT formalise les scénarios, les diagrammes UML et les règles de validation.", styles))
    section(story, styles, "3.2 Classification Core / Smart / Optional")
    story.append(img_flow(FIGURES / "chapitre3/classification_activation.png", doc.width, 12.0 * cm))
    story.append(Paragraph("Figure 3.2 — Logique Core / Smart / Optional et principe d’activation selon les données et l’infrastructure.", styles["Caption"]))
    story.append(para("Cette figure corrige le problème de superposition de l’ancienne version : les notes de décision sont séparées du flux principal et les trois catégories sont lisibles indépendamment.", styles))
    section(story, styles, "3.3 Cartographie des use cases")
    story.append(table_flow(
        ["Domaine", "Core", "Smart", "Optional / infrastructure"],
        [
            ["Réception", "UC-R01–UC-R07", "UC-R08", "UC-R09–UC-R12"],
            ["Stockage & inventaire", "UC-S01–UC-S05, UC-S07–UC-S08", "UC-S06, UC-S09–UC-S12", "UC-S13–UC-S14"],
            ["Commandes / expédition", "UC-E01–UC-E09", "UC-E11, UC-E13, UC-E15", "UC-E10, UC-E12, UC-E14"],
            ["Yard & quais", "UC-Y01–UC-Y04", "UC-Y06–UC-Y07", "UC-Y05"],
            ["Ressources", "UC-RES01–03, UC-RES05–06, UC-RES08", "UC-RES04", "UC-RES07, UC-RES09–10"],
        ],
        [3.3 * cm, 4.3 * cm, 4.3 * cm, 4.4 * cm],
    ))

    chapter(story, styles, "4. Architecture fonctionnelle cible du Smart WMS")
    section(story, styles, "4.1 Principes de conception")
    story.append(para("L’architecture cible est construite comme un système modulaire. Elle doit fonctionner dans un entrepôt simple équipé de terminaux RF, mais aussi dans un environnement automatisé intégrant RFID, vision, AMR/AGV, WCS/WES ou BMS/EMS.", styles))
    story.append(NextPageTemplate("Landscape"))
    story.append(PageBreak())
    story.append(Paragraph("4.2 Vue d’ensemble de l’architecture proposée", styles["SectionTitle"]))
    story.append(img_flow(FIGURES / "chapitre4/architecture_fonctionnelle.png", land[0] - 2.6 * cm, land[1] - 5.2 * cm))
    story.append(Paragraph("Figure 4.1 — Architecture fonctionnelle cible du Smart WMS proposée.", styles["Caption"]))
    story.append(NextPageTemplate("Portrait"))
    story.append(PageBreak())
    section(story, styles, "4.3 Couches fonctionnelles")
    story.append(para("Les systèmes externes apportent commandes, statuts, confirmations et informations transport. Le cœur opérationnel exécute les processus d’entrepôt. La gestion des tâches transforme les décisions en actions. Les données de référence et les bases OLTP/OLAP soutiennent la traçabilité, les KPI et les services d’intelligence.", styles))
    story.append(img_flow(FIGURES / "chapitre4/activation_progressive.png", doc.width, 7.2 * cm))
    story.append(Paragraph("Figure 4.2 — Principe d’activation progressive des capacités Smart WMS.", styles["Caption"]))
    story.append(table_flow(
        ["Bloc", "Responsabilité", "Contribution"],
        [
            ["Cœur opérationnel", "Réception, stock, commandes, yard et expédition", "Stabiliser le socle métier indispensable"],
            ["Gestion des tâches", "Créer, affecter, exécuter et suivre les exceptions", "Transformer décisions et alertes en actions"],
            ["Données de référence", "Produits, zones, règles, rôles et unités logistiques", "Donner le contexte aux règles et optimisations"],
            ["Intelligence", "Prévoir, optimiser, détecter et recommander", "Améliorer la qualité des décisions opérationnelles"],
            ["Terrain", "Capturer les données et guider l’exécution", "Relier système numérique et flux physique"],
        ],
        [3.7 * cm, 6.1 * cm, 6.2 * cm],
    ))

    chapter(story, styles, "5. Modélisation UML")
    story.append(img_flow(FIGURES / "chapitre5/vue_modelisation_uml.png", doc.width, 8.2 * cm))
    story.append(Paragraph("Figure 5.1 — Vue de modélisation UML retenue pour le Smart WMS.", styles["Caption"]))
    story.append(para("Les diagrammes de cas d’utilisation décrivent les acteurs et le périmètre. Les diagrammes d’activité montrent les workflows et les exceptions. Les diagrammes de séquence détaillent les échanges entre acteurs, Smart WMS et systèmes externes. Le modèle de domaine clarifie les objets métier ; le diagramme de composants prépare le passage applicatif.", styles))
    story.append(para("Les sources PlantUML sont conservées en annexe. Elles devront être rendues avec PlantUML et Graphviz lors d’une itération dédiée afin d’obtenir des figures UML finales homogènes.", styles))

    chapter(story, styles, "6. Architecture applicative logique proposée")
    story.append(img_flow(FIGURES / "chapitre6/architecture_applicative_logique.png", doc.width, 8.8 * cm))
    story.append(Paragraph("Figure 6.1 — Architecture applicative logique proposée pour le Smart WMS.", styles["Caption"]))
    story.append(para("Le prototype SmartWMS AI Operations Agent illustre une partie de cette architecture : interface Next.js, API FastAPI, runner d’agent, outils WMS en lecture seule, moteur de décisions déterministes, documents synthétiques et fournisseur LLM interchangeable. Cette maquette démontre la logique d’aide à la décision sans exécuter d’opérations WMS sensibles.", styles))
    story.append(bullet([
        "les outils sont en lecture seule ;",
        "les règles de stock et de réapprovisionnement sont déterministes et testées ;",
        "le modèle de langage explique les faits mais ne modifie pas le stock ;",
        "les données utilisées dans la maquette sont synthétiques.",
    ], styles))

    chapter(story, styles, "7. Validation, limites et perspectives")
    story.append(img_flow(FIGURES / "chapitre7/chaine_validation.png", doc.width, 6.7 * cm))
    story.append(Paragraph("Figure 7.1 — Chaîne de validation proposée pour l’architecture Smart WMS.", styles["Caption"]))
    story.append(para("La validation doit relier chaque scénario métier aux use cases, aux diagrammes UML et aux composants applicatifs. Elle reste limitée par l’absence de déploiement sur un entrepôt réel et par l’utilisation de données synthétiques dans la maquette.", styles))
    story.append(para("Les perspectives concernent la simulation de scénarios réels, la collecte de jeux de données entrepôt, l’intégration d’un IoT gateway, l’évaluation de modèles de prévision, puis la connexion progressive avec ERP, WCS/WES et BMS/EMS.", styles))

    chapter(story, styles, "Conclusion générale")
    story.append(para("Le travail réalisé permet de clarifier la transformation d’un WMS traditionnel vers un Smart WMS. L’apport principal du stage est d’avoir structuré les capacités autour de besoins métier, de conditions d’activation et d’une architecture modulaire. Un Smart WMS robuste n’est pas un système où l’IA est partout ; c’est un système qui utilise les bonnes données au bon endroit pour améliorer la décision et l’exécution réelle.", styles))

    doc.multiBuild(story)
    return pdf_path


def build_html_preview() -> None:
    write_text(BUILD / "report_preview.html", f"""
    <!doctype html>
    <html lang="fr">
    <head>
      <meta charset="utf-8">
      <title>Rapport Smart WMS</title>
      <style>
        body {{ font-family: "Segoe UI", Arial, sans-serif; color: {TEXT}; line-height: 1.55; margin: 36px auto; max-width: 920px; }}
        h1, h2 {{ color: {NAVY}; }}
        h3 {{ color: {TEAL}; }}
        img {{ max-width: 100%; display: block; margin: 14px auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 0.92rem; }}
        th {{ background: {NAVY}; color: white; }}
        th, td {{ border: 1px solid #c8d2dc; padding: 8px; vertical-align: top; }}
        figcaption {{ text-align: center; color: #5f6b78; font-style: italic; }}
      </style>
    </head>
    <body>
      <h1>Rapport de stage — Smart WMS</h1>
      <p><strong>FERHAN Abdelali</strong> — Smart Automation Technologies — Août à octobre 2026</p>
      <h2>Figures principales redessinées</h2>
      <figure><img src="../figures/chapitre3/classification_activation.svg"><figcaption>Figure 3.2 — Classification corrigée.</figcaption></figure>
      <figure><img src="../figures/chapitre4/architecture_fonctionnelle.svg"><figcaption>Figure 4.1 — Architecture fonctionnelle cible.</figcaption></figure>
      <figure><img src="../figures/chapitre6/architecture_applicative_logique.svg"><figcaption>Figure 6.1 — Architecture applicative logique.</figcaption></figure>
    </body>
    </html>
    """)


def main() -> None:
    ensure_dirs()
    copy_plantuml()
    build_diagrams()
    write_latex_project()
    build_html_preview()
    pdf_path = build_pdf_preview()
    print(f"Generated {pdf_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
