"""
Poste une édition du Journal du Marché (fichier HTML) dans un salon Discord,
découpée en plusieurs embeds (un par section ## / h3.section).

Ne dépend d'aucune librairie externe (pas de bs4) — parsing par regex, car
le gabarit HTML du Journal est stable et bien structuré.

Usage :
    EDITION_FILE=Edition/edition-81.html WEBHOOK_JOURNAL=... python script_discord_journal.py
"""

import os
import re
import time
import requests

WEBHOOK_JOURNAL = os.environ["WEBHOOK_JOURNAL"]
EDITION_FILE = os.environ["EDITION_FILE"]

# Discord limite un embed à 4096 caractères de description et 25 embeds par message.
MAX_DESC = 4000

# Couleurs par emoji de section (façon maquette) — sinon couleur or par défaut.
COULEUR_DEFAUT = 0xC9A35A
COULEURS = {
    "💎": 0x7BA05B,  # Achat du jour -> vert
    "🔔": 0xD4537E,  # Alerte marché -> rose
    "🚫": 0xE24B4A,  # À éviter -> rouge
    "🏆": 0xEF9F27,  # Champions -> ambre
}


def strip_tags(html: str) -> str:
    """Convertit un fragment HTML simple en texte lisible pour Discord."""
    # Titres de sous-section -> **gras**
    html = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n**\1**\n', html, flags=re.S)
    # Gras
    html = re.sub(r'<b>(.*?)</b>', r'**\1**', html, flags=re.S)
    # Span positif/négatif -> juste le texte (Discord n'a pas de couleur inline)
    html = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html, flags=re.S)
    # Lignes de tableau -> une ligne texte avec " · " entre les cellules
    def table_to_text(m):
        table_html = m.group(0)
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, flags=re.S)
        lignes = []
        for row in rows:
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, flags=re.S)
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if cells:
                lignes.append(" · ".join(cells))
        return "\n".join(lignes)
    html = re.sub(r'<table[^>]*>.*?</table>', table_to_text, html, flags=re.S)
    # Paragraphes -> juste un saut de ligne
    html = re.sub(r'</p>', '\n', html)
    html = re.sub(r'<div[^>]*>', '', html)
    html = re.sub(r'</div>', '\n', html)
    # Retire toutes les balises restantes
    html = re.sub(r'<[^>]+>', '', html)
    # Nettoyage des espaces multiples / lignes vides
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n+', '\n\n', html)
    return html.strip()


def extraire_sections(html: str):
    """Découpe le HTML en (titre_section, contenu_html) à partir des h3.section."""
    pattern = r'<h3 class="section">(.*?)</h3>(.*?)(?=<h3 class="section">|<div class="sources">)'
    return re.findall(pattern, html, flags=re.S)


def extraire_titre_edition(html: str) -> str:
    m = re.search(r'<div class="dateline">(.*?)</div>', html, flags=re.S)
    return strip_tags(m.group(1)) if m else "Le Journal du Marché"


def construire_embeds(html: str):
    titre_edition = extraire_titre_edition(html)
    sections = extraire_sections(html)
    embeds = []

    for titre_brut, contenu_html in sections:
        titre = strip_tags(titre_brut)
        emoji = titre.split(" ")[0] if titre else ""
        texte = strip_tags(contenu_html)
        if not texte:
            continue
        texte = texte[:MAX_DESC]
        embeds.append({
            "title": titre,
            "description": texte,
            "color": COULEURS.get(emoji, COULEUR_DEFAUT),
        })

    return titre_edition, embeds


def envoyer(titre_edition, embeds):
    print(f"Webhook utilisé (début) : {WEBHOOK_JOURNAL[:50]}...")

    # Message d'en-tête
    r = requests.post(WEBHOOK_JOURNAL, json={"content": f"📰 **{titre_edition}**"})
    print(f"Envoi en-tête -> statut {r.status_code} : {r.text[:300]}")
    if r.status_code >= 300:
        raise SystemExit(f"❌ Échec de l'envoi du message d'en-tête : {r.status_code} {r.text}")
    time.sleep(1)

    if not embeds:
        print("⚠️ Aucune section détectée dans le fichier HTML — vérifie le parsing.")
        return

    # Discord limite la taille TOTALE d'un message à 6000 caractères, tous embeds
    # combinés (pas juste 4096 par description) -> on envoie 1 embed par message
    # pour ne jamais dépasser cette limite, même sur les plus grosses sections.
    for i, embed in enumerate(embeds):
        r = requests.post(WEBHOOK_JOURNAL, json={"embeds": [embed]})
        print(f"Envoi section {i} ({embed['title']}) -> statut {r.status_code} : {r.text[:300]}")
        if r.status_code >= 300:
            raise SystemExit(f"❌ Erreur envoi section {i}: {r.status_code} {r.text}")
        time.sleep(1)  # évite le rate-limit Discord


if __name__ == "__main__":
    with open(EDITION_FILE, encoding="utf-8") as f:
        html = f.read()

    titre_edition, embeds = construire_embeds(html)
    print(f"Édition : {titre_edition} — {len(embeds)} sections trouvées")
    envoyer(titre_edition, embeds)
    print("Tout est envoyé avec succès !")
