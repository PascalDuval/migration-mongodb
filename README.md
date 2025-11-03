# Migration d'une base médicale vers MongoDB

Ce dépôt contient un ensemble de scripts Python pour nettoyer, préparer, migrer et analyser un jeu de données médicales dans MongoDB. Il constitue un support pédagogique complet pour comprendre toutes les étapes d'une migration de données depuis un fichier CSV vers une collection MongoDB.

> Dépôt public : https://github.com/PascalDuval/migration-mongodb

---

<a id="sommaire"></a>
## Sommaire

1. [Objectifs du projet](#objectifs-du-projet)
2. [Contenu du dépôt](#contenu-du-depot)
3. [Prérequis techniques](#prerequis-techniques)
4. [Mise en place de l'environnement](#mise-en-place)
5. [Jeux de données fournis](#jeux-de-donnees)
6. [Scripts disponibles](#scripts)
7. [Organisation de la base MongoDB](#architecture-mongodb)
8. [Utilisation détaillée](#utilisation-detaillee)
9. [Tests automatiques](#tests)
10. [FAQ & dépannage](#faq)
11. [Contribution & support](#contribution)
12. [Licence](#licence)

---

<a id="objectifs-du-projet"></a>
## Objectifs du projet

- Illustrer la migration d'un jeu de données médicales vers MongoDB en respectant les bonnes pratiques.
- Fiabiliser les types de données (dates, nombres, montants, etc.).
- Proposer des scripts d'analyse pour vérifier la qualité des données une fois migrées.
- Fournir une base de tests (unitaires et d'intégration) pour valider la chaîne de migration.

---

<a id="contenu-du-depot"></a>
## Contenu du dépôt

Présentation synthétique de l'architecture, avec les répertoires les plus utiles pour démarrer.

```
migration-mongodb/
├─ data/                    # Jeux de données bruts et nettoyés (CSV)
├─ divers/                  # Exemples, assets et fichiers divers (démos, images)
├─ routines/                # Routines d'analyse/agrégation MongoDB (voir détails ci-dessous)
├─ scripts/                 # Scripts de migration, nettoyage, intégrité et helpers
│  ├─ functions_crud/       # Utilitaires Python 
├─ tests/                   # Suite de tests (pytest, mongomock)
├─ simpledocker/            # Docker Compose, Dockerfile, exécution conteneurs
├─ .gitignore
├─ LICENSE
├─ README.md
├─ requirements.txt
└─ requirements-tests.txt
```

### Détail du répertoire `routines/`

Routines Python d'analyse et de reporting basées sur MongoDB. Elles illustrent des requêtes d'agrégation et des analyses exploratoires.

- `AgeByDesease.py` : âge moyen par pathologie.
- `ByBlood.py` : répartition par groupe sanguin.
- `DureeMoyenneSejourHospital.py` : durée moyenne de séjour par hôpital.
- `MedicationByCancerAndResults.py` : regroupement par médicament, type de cancer et résultat de tests.
- `TopHospital.py` : classement des hôpitaux par nombre de patients.
- `ValidateTopMedications.py` : contrôle/validation sur les médicaments les plus prescrits.

Remarque : une copie de ces routines est aussi disponible sous `simpledocker/routines/` pour la variante Docker simplifiée.

---

<a id="prerequis-techniques"></a>
## Prérequis techniques

| Outil    | Version recommandée | Notes                                               |
|----------|----------------------|-----------------------------------------------------|
| Python   | 3.10 ou supérieur    | Pour scripts et tests.                              |
| MongoDB  | 6.x (local ou Atlas) | Une instance locale suffit pour les tests manuels.  |
| pip      | Dernière version     | Gestionnaire de paquets Python.                     |
| Git      | Optionnel            | Pour cloner et versionner le projet.                |

---

<a id="mise-en-place"></a>
## Mise en place de l'environnement

### 1) Cloner le dépôt

```bash
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
```

### 2) Créer et activer un environnement virtuel

Windows PowerShell:
```powershell
python -m venv .venv
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Installer les dépendances

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Pour exécuter également les tests automatisés:
```bash
python -m pip install -r requirements-tests.txt
```

### 4) Préconfigurer MongoDB

- Installez MongoDB Community Server ou créez un cluster Atlas.
- Base par défaut: `FirstTry`, collection: `mediccrud` (créées automatiquement lors de l'import si absentes).
- Assurez-vous de disposer d'un utilisateur avec droits lecture/écriture (surtout sur Atlas).


- Pour la gestion des utilisateurs locaux, utilisez `scripts/setup_users.py` avec un fichier `.env` à la racine (voir `.env.example`).
- Copier le modèle: `cp .env.example .env` (ou `Copy-Item .env.example .env` sous PowerShell), puis remplir les mots de passe.
- Exécuter: `python scripts/setup_users.py` (idempotent: crée/ajuste dbOwner et read-only sur `MONGO_DB`).
---

<a id="jeux-de-donnees"></a>
## Jeux de données fournis

| Fichier                             | Description                                                        |
|-------------------------------------|--------------------------------------------------------------------|
| `data/healthcare_dataset.csv`       | Fichier source brut (peut contenir doublons/incohérences).         |
| `data/healthcare_dataset_purge.csv` | Version nettoyée, prête pour la migration.                         |

Le script `scripts/check_doublons.py` détecte les doublons et produit la version purgée.

---

<a id="scripts"></a>
## Scripts disponibles

### Migration & préparation

| Script                      | Rôle principal                                           |
|----------------------------|----------------------------------------------------------|
| `scripts/migration_crud.py` | Migration (import CSV via `import_csv`), recherche et opérations utilitaires |
| `scripts/check_doublons.py` | Détection et suppression des doublons dans le CSV (déjà exécuté; vous pouvez partir du CSV purgé) |
| `scripts/check_integrity.py`| Vérifications basiques d'intégrité des données (déjà exécuté; vous pouvez partir du CSV purgé) |

### Analyses (routines)

| Script                                    | Description                                                   |
|-------------------------------------------|---------------------------------------------------------------|
| `routines/TopHospital.py`                 | Classement des hôpitaux par nombre de patients               |
| `routines/AgeByDesease.py`                | Âge moyen par pathologie                                      |
| `routines/MedicationByCancerAndResults.py`| Patients par médicament, cancer et résultat des tests         |
| `routines/ByBlood.py`                     | Répartition par groupe sanguin                                |
| `routines/DureeMoyenneSejourHospital.py`  | Durée moyenne de séjour par hôpital                           |
| `routines/ValidateTopMedications.py`      | Validation des médicaments les plus prescrits                 |

Variables d'environnement supportées par les scripts: `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`.

---

<a id="architecture-mongodb"></a>
## Organisation de la base MongoDB

- Collection principale: `FirstTry.mediccrud`
- Champs principaux:
  - Chaînes: `Name`, `Medical Condition`, `Medication`, `Doctor`, `Hospital`, `Insurance Provider`, `Gender`, `Blood Type`, `Admission Type`, `Test Results`
  - Nombres: `Age`, `Billing Amount`, `Room Number`
  - Dates: `Date of Admission`, `Discharge Date`
  - Identifiant: `_id` (ObjectId généré automatiquement)

<!-- Section index retirée: plus de création d""index automatique -->


---

<a id="utilisation-detaillee"></a>
## Utilisation détaillée

1) (Optionnel) Nettoyer et préparer les données
Déjà appliqué dans ce dépôt: vous pouvez utiliser directement le fichier purgé `data/healthcare_dataset_purge.csv`.
```bash
python scripts/check_doublons.py
python scripts/check_integrity.py
```

2) Simuler la migration (dry-run)
```bash
python scripts/migration_crud.py import_csv --file data/healthcare_dataset_purge.csv --dry
```
Affiche un échantillon de documents convertis (sans insertion).

3) Importer réellement les données
```bash
python scripts/migration_crud.py import_csv --file data/healthcare_dataset_purge.csv
```


4) Lancer des analyses
```bash
python routines/TopHospital.py
python routines/AgeByDesease.py
python routines/MedicationByCancerAndResults.py
```
Exemple de sortie (MedicationByCancerAndResults):
```
{
  "Medication": "Paracetamol",
  "Cancer": "Lung",
  "TotalPatients": 42,
  "PositiveTests": 18,
  "NegativeTests": 24
}
```
Adaptez/dupliquez les routines selon vos besoins pour explorer les données.

---

<a id="tests"></a>
## Tests automatiques

Installer les dépendances de test:
```bash
python -m pip install -r requirements-tests.txt
```

Exécuter les tests:
```bash
pytest -v
```

Contenu principal:

- `tests/test_migration_crud.py` vérifie les fonctions internes (`_safe_int`, `_to_datetime`, `convert_dataframe_types`, etc.) et des opérations de base (avec `mongomock`).

Tests sur une vraie base (optionnel): créez `tests/test_integration_real.py` si nécessaire.

---

<a id="docker"></a>
## Exécution avec Docker (sans scripts shell d'init)

Cette section remplace et simplifie `simpledocker/READMEDOCKER.md`.

- Préparez `.env` à la racine du projet (non versionné) avec par exemple:
  - `MONGO_INITDB_ROOT_USERNAME=admin`
  - `MONGO_INITDB_ROOT_PASSWORD=CHANGER-MOI`
  - `MONGO_APP_USERNAME=appuser` (dbOwner sur `MONGO_DB`)
  - `MONGO_APP_PASSWORD=CHANGER-MOI-APP`
  - `MONGO_READONLY_USERNAME=readonly` (read sur `MONGO_DB`)
  - `MONGO_READONLY_PASSWORD=CHANGER-MOI-RO`
  - `MONGO_DB=FirstTry`
  - `MONGO_COLLECTION=mediccrud`

Copie rapide du modèle d'environnement (.env) à la racine:
```bash
cp .env.example .env
```
Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

1) Démarrer MongoDB (depuis `simpledocker/`):
```
docker compose up -d mongodb
```

2) Créer/mettre à jour les utilisateurs (manuel, idempotent):
```
python scripts/setup_users.py
```
- lit les variables d'environnement / `.env` et crée:
  - compte dbOwner: `MONGO_APP_USERNAME` sur `MONGO_DB`;
  - compte read-only: `MONGO_READONLY_USERNAME` sur `MONGO_DB`.
- aucune fuite de secrets; relancer met à jour mdp/roles.

3) Vérifier les accès (tests rapides intelligents):
```bash
# Depuis l'hôte (si variables exportées) ou via le conteneur dataflow:
docker compose up -d dataflow
docker compose exec dataflow python /app/scripts/setup_users.py   # si non fait
docker compose exec dataflow python /app/scripts/verify_access.py
```
- Vérifie que le compte dbOwner peut insérer/supprimer et que le compte read-only ne peut pas écrire (attendu).

4) Migration et routines:
```
docker compose up --build migration
docker compose up -d routines
docker compose exec routines python MedicationByCancerAndResults.py
```

5) Démo (insertion/mise à jour/suppression) locale (URI via env si `--uri` absent):
```
python scripts/demo_crud_flow.py --db FirstTry --collection mediccrud --readonly
```
- Recherche d'URI dans l'ordre: `MONGODB_URI`, `MONGO_URI`, `MONGO_URI_RW` (ou `MONGO_URI_RO` si `--readonly`), sinon `mongodb://localhost:27017`.

6) Sécurité:
- ne pas committer `.env` (mots de passe fournis séparément),
- éviter l'admin root dans les scripts applicatifs,
- rotation simple: modifier `.env` puis relancer `scripts/setup_users.py`.

Volumes et réinitialisation:
- Le volume Docker `mongo_data` persiste la base et les identifiants (root + utilisateurs). Changer `MONGO_INITDB_ROOT_*` dans `.env` n’a d’effet que lors du tout premier démarrage.
- Pour appliquer de nouveaux identifiants root, deux options:
  - Réinitialiser la base: `docker compose down -v` puis relancer MongoDB, rejouer `scripts/setup_users.py`.
  - Ou mettre à jour les utilisateurs applicatifs avec l’admin actuel: par exemple
```
docker compose exec dataflow python /app/scripts/setup_users.py --root_user root --root_pwd rootpass
```

<a id="faq"></a>
## FAQ & dépannage

<details>
  <summary>"Connection refused" lors de la connexion à MongoDB</summary>

- Vérifiez que le service MongoDB est démarré (`mongod`).
- Si vous utilisez MongoDB Atlas, autorisez votre IP dans le réseau.
- Vérifiez la variable d'environnement `MONGO_URI`.

</details>

<details>
  <summary>Quel CSV est utilisé par défaut ?</summary>

`migration_crud.py` utilise `data/healthcare_dataset_purge.csv`. Vous pouvez changer ce comportement en modifiant la constante correspondante dans le script.

</details>

<details>
  <summary>Mes dates ne sont pas converties correctement</summary>

Utilisez le mode `--dry` pour inspecter les conversions. Les dates doivent être au format ISO (`YYYY-MM-DD`) ou un format reconnu par `pandas.to_datetime`.

</details>

<details>
  <summary>Comment ajouter un nouveau test ?</summary>

Créez un nouveau fichier dans `tests/` (ex: `test_top_hospital.py`) et utilisez `mongomock` pour simuler la collection. Inspirez-vous de `tests/test_migration_crud.py`.

</details>

---

<a id="contribution"></a>
## Contribution & support

- Forkez le dépôt.
- Créez une branche dédiée: `git checkout -b feature/ma-fonctionnalite`.
- Faites vos modifications et ajoutez des tests si pertinent.
- Lancez `pytest -v` avant de soumettre votre Pull Request.
- Soumettez une PR descriptive. Pour toute question: ouvrez une issue.

---

<a id="licence"></a>
## Licence

Projet distribué sous licence MIT.

Bon apprentissage et bonne migration !

## Automatisation

- Script: `scripts/run_backup_and_migrate.ps1` (PowerShell)
- Rôle: sauvegarder la collection en JSONL, supprimer la collection, exécuter un dry-run, puis proposer la migration complète.
- Prise en compte de l'authentification: si `MONGODB_URI`/`MONGO_URI_RW`/`MONGO_URI` est défini, le script l'utilise; à défaut, il construit une URI à partir de `MONGO_APP_USERNAME`/`MONGO_APP_PASSWORD` et `MONGO_DB` (fallback `localhost:27017`).
- Exemple:
```
./scripts/run_backup_and_migrate.ps1 -Db FirstTry -Collection mediccrud
```
- Note: le message concernant la création d'index a été retiré car il n'y a plus de création d'index automatique.






