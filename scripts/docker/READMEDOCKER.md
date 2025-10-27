# Démarrage strict des services Docker de migration

Ce guide explique comment démarrer **tous** les services Docker fournis par ce dépôt. Les étapes sont volontairement strictes : suivez-les dans l'ordre.

## 1. Prérequis
- Docker 20.10+ et Docker Compose v2.20+ installés.
- Accès shell à la racine du dépôt `migration-mongodb`.

## 2. Préparer l'unique fichier de configuration
1. Copiez le modèle d'environnement :
   ```bash
   cp .env.example .env
   ```
2. Ouvrez `.env` et mettez à jour **au minimum** :
   - `MONGO_INITDB_ROOT_PASSWORD`
   - `MONGO_APP_PASSWORD`
   - `MIGRATION_MONGODB_URI` (doit refléter les valeurs précédentes).
3. Optionnel : ajustez `MONGO_APP_ROLES` pour ajouter ou retirer des rôles MongoDB (par défaut `readWrite,dbOwner` donnent les droits d'écriture, mise à jour et suppression sur la base cible).

> ℹ️  Aucun autre fichier n'est requis : **`.env` est le seul fichier à personnaliser**.

## 3. Démarrer la base MongoDB (obligatoire)
Lancez MongoDB et la création automatique de l'utilisateur applicatif :
```bash
docker compose \
  --env-file .env \
  -f docker/compose.mongodb.yml \
  up -d
```
Attendez que le conteneur `mongodb` affiche l'état `running` (`docker compose ps`).

## 4. Vérifier l'utilisateur applicatif
Le script `docker/mongo-init/01-create-app-user.sh` crée (ou met à jour) l'utilisateur défini par `MONGO_APP_USER` avec les rôles `MONGO_APP_ROLES`. Par défaut cela inclut `readWrite` et `dbOwner`, ce qui donne les droits **write**, **update** et **delete** sur la base `MONGO_APP_DATABASE`.

Chargez les variables dans votre shell si ce n'est pas déjà fait :
```bash
set -a && source .env && set +a
```

Pour vérifier :
```bash
docker compose \
  --env-file .env \
  -f docker/compose.mongodb.yml \
  exec mongodb mongosh --quiet \
    "${MONGO_APP_DATABASE}" --eval 'db.getUser("'"${MONGO_APP_USER}"'")'
```

## 5. Utiliser le client de migration
Le service `migration-cli` s'exécute à la demande. Exemple pour lancer un import :
```bash
# (Optionnel) charger les variables dans votre shell
set -a && source .env && set +a

docker compose \
  --env-file .env \
  -f docker/compose.mongodb.yml \
  -f docker/compose.migration.yml \
  run --rm migration-cli \
  --uri "$MIGRATION_MONGODB_URI" \
  import_csv --file data/healthcare_dataset_purge.csv
```

Vous pouvez remplacer `import_csv ...` par `find`, `insert_one`, `update_one`, `delete_one`, etc. Toutes les commandes de `python scripts/migration_crud.py --help` sont disponibles. Les options `--db` et `--collection` sont désormais pré-remplies grâce aux variables `MIGRATION_DEFAULT_DB` et `MIGRATION_DEFAULT_COLLECTION` définies dans `.env`.

## 6. Arrêt et nettoyage
Pour arrêter MongoDB :
```bash
docker compose \
  --env-file .env \
  -f docker/compose.mongodb.yml \
  down
```
Ajoutez `--volumes` si vous souhaitez supprimer complètement les données MongoDB locales.

## 7. Résumé rapide
1. Copier `.env.example` → `.env` et adapter les mots de passe.
2. `docker compose --env-file .env -f docker/compose.mongodb.yml up -d`
3. `docker compose --env-file .env -f docker/compose.mongodb.yml -f docker/compose.migration.yml run --rm migration-cli ...`

En respectant ces étapes, vous disposez d'une base MongoDB avec un utilisateur applicatif disposant des droits d'écriture, de mise à jour et de suppression, ainsi que du client de migration prêt à l'emploi