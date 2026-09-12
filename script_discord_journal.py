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
import json
import time
import requests

WEBHOOK_JOURNAL = os.environ["WEBHOOK_JOURNAL"]
EDITION_FILE = os.environ["EDITION_FILE"]
ETAT_FILE = "discord_message_ids.json"  # mémoire des IDs de messages postés la veille

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


# Sections à ne PAS poster sur Discord (trop génériques, redondantes, ou déjà
# couvertes par le Journal de la Construction publié séparément à la suite).
SECTIONS_EXCLUES = {
    "🌍 Terrains",
    "🏗️ Construction",
    "🧮 Repère devis du jour",
    "📰 À lire aussi dans le Journal",
    "📌 Pour les nouveaux joueurs",
    "🤝 Rejoindre la communauté",
    "⚡ Coin des petits chiffres",
    "👀 Liste de surveillance — promotions longue durée",
}


def construire_embeds(html: str):
    titre_edition = extraire_titre_edition(html)
    sections = extraire_sections(html)
    embeds = []

    for titre_brut, contenu_html in sections:
        titre = strip_tags(titre_brut)
        if titre in SECTIONS_EXCLUES:
            continue
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


def charger_etat():
    if os.path.exists(ETAT_FILE):
        with open(ETAT_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"entete_id": None, "section_ids": []}


def sauver_etat(etat):
    with open(ETAT_FILE, "w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False, indent=2)


def poster(payload):
    """Poste un nouveau message et retourne son ID (?wait=true renvoie le message créé)."""
    r = requests.post(f"{WEBHOOK_JOURNAL}?wait=true", json=payload)
    if r.status_code >= 300:
        raise SystemExit(f"❌ Erreur à la création : {r.status_code} {r.text}")
    return r.json()["id"]


def editer(message_id, payload):
    """Édite un message existant du webhook. Retourne False si le message n'existe plus."""
    r = requests.patch(f"{WEBHOOK_JOURNAL}/messages/{message_id}", json=payload)
    if r.status_code == 404:
        return False
    if r.status_code >= 300:
        raise SystemExit(f"❌ Erreur à l'édition de {message_id} : {r.status_code} {r.text}")
    return True


def supprimer(message_id):
    requests.delete(f"{WEBHOOK_JOURNAL}/messages/{message_id}")


def envoyer(titre_edition, embeds):
    print(f"Webhook utilisé (début) : {WEBHOOK_JOURNAL[:50]}...")
    etat = charger_etat()

    # 1. Message d'en-tête : édité en place si on a déjà un ID, sinon créé.
    payload_entete = {"content": f"📰 **{titre_edition}**"}
    entete_id = etat.get("entete_id")
    if not (entete_id and editer(entete_id, payload_entete)):
        entete_id = poster(payload_entete)
        print(f"En-tête créé : {entete_id}")
    else:
        print(f"En-tête édité : {entete_id}")
    time.sleep(1)

    if not embeds:
        print("⚠️ Aucune section détectée dans le fichier HTML — vérifie le parsing.")
        sauver_etat({"entete_id": entete_id, "section_ids": etat.get("section_ids", [])})
        return

    anciens_ids = etat.get("section_ids", [])
    nouveaux_ids = []

    # 2. Chaque section : édite le message correspondant de la veille (même position),
    # sinon en crée un nouveau. Discord limite un message à 6000 caractères tous
    # embeds combinés -> un embed par message pour ne jamais dépasser la limite.
    for i, embed in enumerate(embeds):
        payload = {"embeds": [embed]}
        ancien_id = anciens_ids[i] if i < len(anciens_ids) else None
        if ancien_id and editer(ancien_id, payload):
            print(f"Section {i} ({embed['title']}) éditée : {ancien_id}")
            nouveaux_ids.append(ancien_id)
        else:
            nouveau_id = poster(payload)
            print(f"Section {i} ({embed['title']}) créée : {nouveau_id}")
            nouveaux_ids.append(nouveau_id)
        time.sleep(1)  # évite le rate-limit Discord

    # 3. S'il y a moins de sections ce soir que la veille, on supprime le surplus.
    for id_en_trop in anciens_ids[len(embeds):]:
        supprimer(id_en_trop)
        print(f"Ancien message en trop supprimé : {id_en_trop}")
        time.sleep(1)

    sauver_etat({"entete_id": entete_id, "section_ids": nouveaux_ids})
    print(f"État sauvegardé dans {ETAT_FILE}")


if __name__ == "__main__":
    with open(EDITION_FILE, encoding="utf-8") as f:
        html = f.read()

    titre_edition, embeds = construire_embeds(html)
    print(f"Édition : {titre_edition} — {len(embeds)} sections trouvées")
    envoyer(titre_edition, embeds)
    print("Tout est envoyé avec succès !")
