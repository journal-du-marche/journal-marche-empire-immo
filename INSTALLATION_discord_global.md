# Installation — Rapport Discord automatique Immobilier Global

## 1. Créer le repo GitHub (ou utiliser le repo existant)
1. Va sur github.com → New repository → nom au choix (ex: `discord-immobilier-global`) → **Private**.
2. Mets-y ces fichiers :
   - `script_discord_global.py`
   - `requirements.txt` (contenant : `requests`, `pandas`, `gspread`)
   - `discord_global.yml` → à placer dans `.github/workflows/discord_global.yml` (crée ce dossier).

## 2. Créer les webhooks Discord
Sur ton serveur "Immobilier Global", pour chacun des 3 salons (`primes`, `frais-de-gestion`, `promotions`) :
1. Icône ⚙️ du salon → **Intégrations** → **Webhooks**.
2. **Nouveau webhook** → donne-lui un nom → **Copier l'URL du webhook**.
3. Garde les 3 URLs de côté, une par salon.

## 3. Créer le compte de service Google (accès à la Google Sheet)
1. Va sur [console.cloud.google.com](https://console.cloud.google.com) → crée un projet (ou utilise un existant).
2. Active les API **Google Sheets API** et **Google Drive API**.
3. Menu "IAM et administration" → "Comptes de service" → Créer un compte de service.
4. Une fois créé, onglet "Clés" → Ajouter une clé → JSON → télécharge le fichier.
5. Ouvre ta feuille Google "Immobilier Global" → Partager → colle l'email du compte de service (ressemble à `xxx@xxx.iam.gserviceaccount.com`) → droit **Lecteur** suffit.

## 4. Ajouter les secrets sur GitHub
Dans ton repo : Settings → Secrets and variables → Actions → New repository secret. Ajoute :

| Nom du secret | Valeur |
|---|---|
| `WEBHOOK_PRIMES_GLOBAL` | ton URL webhook du salon primes |
| `WEBHOOK_FRAIS_GLOBAL` | ton URL webhook du salon frais-de-gestion |
| `WEBHOOK_PROMO_GLOBAL` | ton URL webhook du salon promotions |
| `CLE_API` | ta clé API du jeu |
| `GOOGLE_CREDENTIALS` | tout le contenu du fichier JSON téléchargé à l'étape 3 (colle-le tel quel) |

## 5. Tester
Onglet "Actions" de ton repo → sélectionne "Rapport Discord Immobilier Global" → **Run workflow** → coche "Ignorer le garde-fou horaire (test immédiat)" → lance-le pour vérifier que tout fonctionne, sans attendre 3h du matin.

## 6. C'est automatique
Une fois les secrets en place, le workflow se déclenche tout seul chaque jour à 3h du matin heure de Paris, sans PC allumé, sans intervention de ta part.
