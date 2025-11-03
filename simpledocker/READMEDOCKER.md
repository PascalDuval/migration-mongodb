# Docker — Migration MongoDB et Routines (sans mongo-init)

Ce dossier fournit une dockerisation simple:
- `mongodb`: MongoDB 6 avec healthcheck (auth root via variables d'environnement)
- `migration`: import CSV one-shot (optionnel)
- `routines`: exécution à la demande de scripts d'analyse
- `dataflow`: conteneur utilitaire (peut exécuter `scripts/setup_users.py`)

Important: la création des utilisateurs applicatifs ne se fait plus via des scripts shell `mongo-init`, mais via un script Python manuel idempotent: `scripts/setup_users.py`.

## Prérequis
- Docker Desktop (ou équivalent)
- Docker Compose v2+

## Fichiers clés
- `simpledocker/docker-compose.yml` — Orchestration des services
- `simpledocker/.env` — Variables d'environnement (ne pas committer)
- `simpledocker/Dockerfile` — Image Python pour migration/routines
- `scripts/setup_users.py` — Création/MAJ des utilisateurs (dbOwner + read-only)

## `.env` (exemple)
```
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=CHANGER-MOI
MONGO_APP_USERNAME=appuser
MONGO_APP_PASSWORD=CHANGER-MOI-APP
MONGO_READONLY_USERNAME=readonly
MONGO_READONLY_PASSWORD=CHANGER-MOI-RO
MONGO_DB=FirstTry
MONGO_COLLECTION=mediccrud
```

## Démarrages typiques
Depuis `simpledocker/`:

1) Lancer MongoDB:
```
docker compose up -d mongodb
```
Attendre le healthcheck (CMD `mongosh ... ping`).

2) Créer/mettre à jour les utilisateurs (manuel, idempotent):
```
docker compose up -d dataflow
docker compose exec dataflow python /app/scripts/setup_users.py
```
- Crée/MAJ:
  - dbOwner (`MONGO_APP_USERNAME`) sur `MONGO_DB`
  - read-only (`MONGO_READONLY_USERNAME`) sur `MONGO_DB`

3) Migration one-shot (optionnel):
```
docker compose up --build migration
```
Importe `data/healthcare_dataset_purge.csv` dans `${MONGO_DB}.${MONGO_COLLECTION}` puis s'arrête.

4) Routines à la demande:
```
docker compose up -d routines
docker compose exec routines python MedicationByCancerAndResults.py
```

## Connexions utiles
- Depuis l'hôte: `mongodb://localhost:27017`
- Depuis un service du compose: `mongodb://mongodb:27017`

## Sécurité
- Ne commitez pas `.env`.
- Évitez l'admin root dans les scripts applicatifs.
- Pour changer un mot de passe: mettez à jour `.env`, relancez `scripts/setup_users.py`.

Pour une vue d'ensemble du projet et des scripts Python, voir le `README.md` à la racine.

