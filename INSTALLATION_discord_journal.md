# Publier le Journal du Marché sur Discord — installation

## 1. Ajouter le secret GitHub
Dans ton repo GitHub → Settings → Secrets and variables → Actions → New repository secret :
- Nom : `WEBHOOK_JOURNAL`
- Valeur : l'URL du webhook que tu m'as donnée (celle du salon "édition")

⚠️ Ne remets plus cette URL en clair nulle part ailleurs (chat public, forum) — seul le secret GitHub doit la contenir.

## 2. Ajouter les 2 fichiers au repo
- `script_discord_journal.py` — le script qui lit le HTML et poste sur Discord
- `.github/workflows/discord_journal.yml` — le workflow pour le lancer

## 3. Une fois tes fichiers d'édition transférés sur GitHub
Quand une édition (ex: `Edition/edition-81.html`) est dans ton repo :
1. Va dans l'onglet **Actions** du repo.
2. Choisis le workflow **"Publier édition du Journal sur Discord"**.
3. Clique **Run workflow**.
4. Dans le champ, écris le chemin du fichier, ex : `Edition/edition-81.html`.
5. Lance.

Ça va poster :
- Un message d'en-tête avec le titre de l'édition.
- Une série de messages contenant les sections du journal (5 sections par message, en blocs colorés), dans l'ordre du journal.

## Comment ça marche
Le script lit les balises `<h3 class="section">` du fichier HTML (Introduction, Achat du jour, Alerte marché, etc.), convertit chaque section en texte simple (tableaux → lignes avec " · ", gras conservé), et les envoie en blocs Discord colorés, comme dans la maquette qu'on a vue ensemble.

## Prochaine étape possible
Une fois que ça tourne bien en manuel, on peut automatiser le déclenchement pour qu'il se lance tout seul dès qu'un nouveau fichier d'édition est ajouté au repo (au lieu de cliquer "Run workflow" à chaque fois).
