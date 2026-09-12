# Créer le serveur Discord du Journal du Marché — guide pas à pas

## 1. Créer le serveur
1. Ouvre Discord (app ou navigateur, discord.com/app).
2. En bas à gauche, clique sur le **+** dans la liste des serveurs.
3. Choisis **"Créer un serveur"**.
4. Choisis **"Créer le mien"**, puis **"Pour moi et mes amis"** (peu importe, ça ne change rien pour notre usage).
5. Donne-lui le nom **"Journal du Marché"**, ajoute une image si tu veux, puis clique **Créer**.

## 2. Créer les salons texte
Par défaut Discord crée un salon "général" — tu peux le garder ou le supprimer, peu importe.

Pour chaque nouveau salon :
1. Clique sur le **+** à côté de "SALONS TEXTUELS" dans la colonne de gauche.
2. Choisis **Salon textuel**, donne le nom, clique **Créer le salon**.

Salons utilisés jusqu'ici :
- `📰-editions` — les éditions nocturnes du Journal du Marché, postées automatiquement
- `-constitution` — les repères officiels du jeu (lien vers la Constitution interactive hébergée sur GitHub Pages)

## 3. Créer un webhook pour un salon
Répète ces étapes pour chaque salon qui doit recevoir des messages automatiques :
1. Clique sur l'engrenage ⚙️ à côté du nom du salon (ou clic droit sur le salon → **Modifier le salon**).
2. Dans le menu de gauche, clique **Intégrations**.
3. Clique **Créer un Webhook** (ou **Webhooks** puis **Nouveau Webhook**).
4. Donne-lui un nom (ex: "Journal du Marché"), garde le salon associé tel quel.
5. Clique **Copier l'URL du Webhook** — colle-la quelque part en sécurité (bloc-notes).
6. Clique **Enregistrer**.

Pour le Journal, l'URL de webhook du salon `📰-editions` correspond à la variable `WEBHOOK_JOURNAL` (stockée comme secret GitHub, jamais partagée publiquement).

⚠️ Une URL de webhook donne accès pour poster dans le salon associé — évite de la partager publiquement (la mettre dans les secrets GitHub, comme prévu, est sécuritaire).
