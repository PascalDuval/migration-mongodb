# migration-mongodb

Ce dépôt contient des scripts Python pour préparer et migrer un jeu de données santé vers MongoDB, ainsi que plusieurs utilitaires d'analyse et de nettoyage.

Important : ce README n'évoque pas Docker — il explique comment cloner le projet, installer les dépendances et configurer MongoDB localement (Windows), puis lancer les scripts. Il inclut aussi des instructions pour se connecter et visualiser les données avec MongoDB Compass et pour utiliser MongoDB Atlas.

## Structure

- `scripts/` : scripts Python pour le nettoyage, la vérification, la migration et l'analyse (ex. `migration.py`, `check_doublons.py`, `check_integrity.py`, etc.).
- `data/` : jeux de données et schémas utilisés par les scripts. Contenu important :
  - `healthcare_dataset.csv` : dataset source (brut).
  - `healthcare_dataset_purge.csv` : dataset nettoyé (généré par `check_doublons.py`).
  - `FirstTry.medic2.json` : export JSON possible pour import dans MongoDB.
  - `schema-FirstTry-medic2-standardJSON.json` : schéma / mapping utile pour valider ou documenter la collection.

## Organisation de la collection MongoDB

### Schéma de la collection `FirstTry.medic2`

Chaque document de la collection importée possède les champs suivants :

- `_id` (`ObjectId` généré par MongoDB).
- `Name`, `Medical Condition`, `Medication`, `Doctor`, `Hospital`, `Insurance Provider`, `Admission Type`, `Gender`, `Blood Type`, `Test Results` (chaînes de caractères).
- `Age`, `Billing Amount`, `Room Number` (chaînes de caractères dans le dataset d'origine).
- `Date of Admission`, `Discharge Date` (dates stockées en chaîne de caractères dans le fichier source ; pensez à les convertir en `ISODate` si vous souhaitez bénéficier des opérateurs de comparaison temporelle natifs).

### Rappel rapide : comment MongoDB exploite les index

- Un index est une structure similaire à l'index d'un livre : elle permet au moteur de requêtes de localiser rapidement les documents correspondant à un filtre, au lieu de parcourir toute la collection (`COLLSCAN`).
- Les plans d'exécution (`explain`) exposent notamment :
  - `totalKeysExamined` : nombre d'entrées d'index lues (si > 0, un index a été consulté).
  - `totalDocsExamined` : nombre de documents effectivement retournés par le moteur après lecture de l'index (à comparer avec la taille totale de la collection).
  - `nReturned` : nombre de résultats transmis au client.
  - `executionTimeMillis` : durée totale de la requête.
  - `winning_plan.stage` : `COLLSCAN` (lecture complète), `IXSCAN`/`FETCH` (lecture d'index), `TEXT_MATCH` (plan textuel), etc.
- Interprétation pratique :
  - `keysExamined = 1` et `docsExamined = 1` → l'index identifie immédiatement le document.
  - `keysExamined ≈ docsExamined ≫ 1` mais bien inférieur à la taille totale → l'index aide mais renvoie de nombreuses correspondances (filtre peu sélectif).
  - `keysExamined = 0` et `docsExamined = taille_collection` → le plan exécute un `COLLSCAN` (pas d'index utilisable).

### Index créés

Les index sont créés via `python scripts/migration_crud.py create_indexes` (cf. fonction `create_indexes`), sur la base `FirstTry`, collection `mediccrud`.

| Nom de l'index | Type | Champ(s) | Observation (explain) |
| --- | --- | --- | --- |
| `_id_` | Index par défaut | `_id` | Index natif créé automatiquement par MongoDB.
| `idx_name` | Index simple (`ASC`) | `Name` | Requête `find_by_name` : `totalKeysExamined = 1`, `totalDocsExamined = 1` → lecture ultra ciblée.
| `idx_date_admission` | Index simple (`ASC`) | `Date of Admission` | Requête `range_date_admission` : 24 clés/documents examinés, au lieu de 50k.
| `idx_medical_condition` | Index simple (`ASC`) | `Medical Condition` | Requête `filter_medical_condition` : ~8 294 clés/documents examinés — index utile mais filtre peu sélectif.
| `idx_name_date` | Index composé (`ASC`, `ASC`) | `Name`, `Date of Admission` | Optimise les recherches combinant identité + période.
| `text_idx_medical_condition` | Index texte | `Medical Condition` | Requête `text_search_medical` : plan `TEXT_MATCH`, plus efficace que le filtre classique sur la même requête textuelle.

### Quand l'index ne sera pas exploité

- Application d'une fonction non sargable dans le filtre (`$toLower`, `$substr`, etc.).
- Mismatch de type entre l'index et les valeurs stockées (ex. index sur `Date` mais champ enregistré en texte).
- Filtre trop peu sélectif (ex. retourne ~50 % de la collection) : le planificateur peut privilégier `COLLSCAN`.
- Combinaison d'opérateurs non compatibles avec l'index.  

## 1) Cloner le projet

Ouvrez un terminal et exécutez :

```powershell
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
```

## 2) Prérequis

- Python 3.10+ installé (Windows). Vérifiez avec : `python --version`.
- Pip (gestionnaire de paquets Python).
- MongoDB (local) ou un accès MongoDB Atlas/remote si vous préférez.

Installer les dépendances Python du projet — utilisez un environnement virtuel isolé :

Important — créez et utilisez un environnement virtuel Python avant d'installer les dépendances : cela évite de polluer l'installation globale et garantit que les versions de paquets utilisées par le projet sont isolées.

Windows (PowerShell) — étapes recommandées :

1. Ouvrez PowerShell (si besoin en administrateur pour modifier la politique d'exécution).
2. Créez un virtualenv nommé `.venv` à la racine du dépôt :

```powershell
python -m venv .venv
```

3. (Facultatif) autorisez l'exécution de scripts pour la session PowerShell :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
```

4. Activez l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
# l'invite PowerShell devient '(.venv) PS C:\...'
```

5. Mettez pip à jour et installez les dépendances :

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

6. Exécutez les scripts via `python` (qui pointe maintenant vers `.venv\Scripts\python.exe`) :

```powershell
python scripts\migration_crud.py import_csv --dry
```

Alternatives :

- Sous l'invite Windows (cmd.exe) :

```cmd
.venv\Scripts\activate.bat
```

- Sous Git Bash / WSL / macOS / Linux :

```bash
source .venv/bin/activate
```

Remarque : si vous préférez ne pas activer l'environnement, vous pouvez lancer directement l'interpréteur dans `.venv` :

```powershell
.venv\Scripts\python.exe scripts\migration_crud.py import_csv --dry
```

Le fichier `requirements.txt` contient au minimum :

- `pymongo` (client MongoDB)
- `pandas` (pour certains scripts d'analyse)

## 3) Installer et démarrer MongoDB (Windows)

Procédure rapide pour MongoDB Community Server (local) :

1. Téléchargez l'installateur MSI depuis : https://www.mongodb.com/try/download/community
2. Lancez l'installateur et choisissez l'installation « Complete ».
3. Pendant l'installation, vous pouvez cocher « Install MongoDB as a Service » pour un démarrage automatique.
4. Pour démarrer manuellement (exemple) :

```powershell
mkdir C:\data\db
"C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath "C:\data\db"
```

5. Vérifier la connexion :

```powershell
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

Si `mongosh` ou `mongo` n'est pas dans le PATH, utilisez l'exécutable dans le dossier d'installation ou testez la connexion depuis Python :

```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
print(client.list_database_names())
```

### MongoDB Compass (visualisation locale)

MongoDB Compass est l'interface graphique officielle pour explorer vos bases MongoDB.

1. Téléchargez Compass : https://www.mongodb.com/try/download/compass
2. Installez Compass.
3. Ouvrez Compass et connectez-vous à votre instance locale en utilisant l'URI :

```
mongodb://localhost:27017
```

4. Dans Compass vous pouvez :
   - Parcourir bases et collections (`FirstTry`, `medic2`).
   - Importer un fichier JSON/CSV directement dans une collection via l'option `IMPORT DATA` (utile pour `FirstTry.medic2.json` ou `healthcare_dataset_purge.csv`).

### MongoDB Atlas (cloud)

Si vous préférez utiliser MongoDB Atlas (service cloud) :

1. Créez un compte gratuit sur https://www.mongodb.com/cloud/atlas
2. Créez un cluster gratuit (Free Tier) et notez l'URI de connexion (ex. `mongodb+srv://<user>:<password>@cluster0.xyz.mongodb.net`).
3. Autorisez l'adresse IP de votre machine (ou 0.0.0.0/0 pour tests rapides, non recommandé en production).
4. Connectez-vous depuis Compass ou votre application en utilisant l'URI Atlas.

Remarque : pour utiliser Atlas avec `scripts/migration.py`, remplacez la ligne de connexion `MongoClient('mongodb://localhost:27017')` par votre URI Atlas (en veillant à utiliser les identifiants corrects et le paramètre de base).

## 4) Script principal : `scripts/migration.py`

But
- Importer un fichier CSV nettoyé (`data/healthcare_dataset_purge.csv`) dans la collection MongoDB.

Comportement (par défaut)
- Se connecte à MongoDB sur `mongodb://localhost:27017`.
- Utilise la base `FirstTry` et la collection `medic2`.
- Lit les lignes du CSV via `csv.DictReader` et insère le lot via `insert_many`.
- Affiche un message de fin et 5 documents d'exemple.

Exécution

```powershell
python scripts/migration.py
```

Remarques
- Assurez-vous que MongoDB (local ou Atlas) est accessible avant l'exécution.
- Le script ne convertit pas automatiquement les types (dates, nombres) : si nécessaire, prétraitez `healthcare_dataset_purge.csv` avec les scripts de `scripts/` ou adaptez `migration.py`.

## 5) Autres scripts disponibles (résumé rapide)

- `scripts/check_doublons.py` : nettoie les doublons et génère `data/healthcare_dataset_purge.csv` à partir du CSV brut.
- `scripts/check_integrity.py` : vérifie la présence de colonnes, valeurs manquantes, doublons et fournit des recommandations.
- `scripts/AgeByDesease.py` : calcule âge moyen par pathologie (agrégation MongoDB → pandas).
- `scripts/ByBlood.py` : histogramme des groupes sanguins (agrégation + pandas).
- `scripts/MedicationByCancer.py`, `scripts/MedicationByCancerAndResults.py` : analyses ciblées sur traitements et résultats.
- `scripts/DureeMoyenneSejourHopital.py` : calcule la durée moyenne de séjour.
- `scripts/TopHospital.py` : liste des hôpitaux les plus fréquents.
- `scripts/CrudTry1.py` : exemples CRUD sur MongoDB.
- `scripts/check_integrity_json.py` : vérifications pour fichiers JSON.

### Nouveau : `scripts/migration_crud.py` (CRUD + import robuste)

`migration_crud.py` est un utilitaire plus complet pour :

- importer le CSV nettoyé avec conversion de types (Age -> int, Date of Admission -> datetime),
- réaliser des opérations CRUD depuis la ligne de commande (find, find_one, insert_one, update_one, delete_one),
- créer et lister des index (commande `create_indexes` / `show_indexes`).

Exemples d'utilisation :

- Dry-run d'import (convertit et affiche un échantillon sans insérer) :

```powershell
python scripts\migration_crud.py import_csv --dry
```

- Importer réellement (par défaut lit `../data/healthcare_dataset_purge.csv`) :

```powershell
python scripts\migration_crud.py import_csv
```

- Rechercher des documents (filtre JSON) :

```powershell
python scripts\migration_crud.py find --filter '{"Name": "Dupont"}' --limit 50
```

- Insérer un document JSON :

```powershell
python scripts\migration_crud.py insert_one '{"Name": "Alice", "Age": 30, "Date of Admission": "2024-01-10"}'
```

- Mettre à jour un document (upsert optionnel) :

```powershell
python scripts\migration_crud.py update_one '{"Name": "Alice"}' '{"Age": 31}' --upsert
```

- Supprimer un document :

```powershell
python scripts\migration_crud.py delete_one '{"Name": "Alice"}'
```

Options utiles :

- `--uri` : changer l'URI MongoDB (ex. Atlas)
- `--db` / `--collection` : nom de la base et de la collection (défaut `FirstTry` / `mediccrud`)
- `--batch` : taille des batches pour `import_csv`

Le script convertit automatiquement quelques champs connus et crée des index recommandés (Name, Date of Admission, Medical Condition, index composé et index texte) via `create_indexes`.

Exécution générale :

```powershell
python scripts/<NomDuScript>.py
```

## 6) Workflow recommandé

1. Cloner le dépôt.
2. Installer Python et les dépendances (`pip install -r requirements.txt`).
3. Installer/démarrer MongoDB localement ou créer un cluster Atlas.
4. Nettoyer les données brutes : `python scripts/check_doublons.py`.
5. Vérifier l'intégrité : `python scripts/check_integrity.py`.
6. Migrer : `python scripts/migration.py`.
7. Analyser depuis MongoDB (`AgeByDesease.py`, `ByBlood.py`, ...).

## 7) Conseils

- Conservez une copie du CSV original.
- Testez le pipeline sur un petit échantillon avant import complet.
- Adaptez la connexion MongoDB pour Atlas ou pour un utilisateur/port différent.

## 8) Besoin d'aide ?

Ouvrez une issue sur le dépôt : https://github.com/PascalDuval/migration-mongodb/issues

## 9) Script d'automatisation (Windows PowerShell)

Un script PowerShell d'automatisation est fourni : `scripts/run_backup_and_migrate.ps1`.
Il exécute dans l'ordre :

- sauvegarde de la collection `mediccrud` dans `data/backup_mediccrud_YYYYmmdd_HHMMSS.jsonl` (via `backup_and_drop.py`),
- suppression (drop) de la collection,
- dry-run de l'import (`migration_crud.py import_csv --dry`),
- puis propose de lancer l'import réel si tu confirmes.

Usage :

```powershell
# exécuter depuis la racine du projet
./scripts/run_backup_and_migrate.ps1
```

Le script utilise l'interpréteur Python de l'environnement virtuel `.venv` par défaut ;
tu peux modifier le chemin vers Python en passant le paramètre `-Python` si besoin.

Exemple (avec URI Atlas) :

```powershell
./scripts/run_backup_and_migrate.ps1 -Uri "mongodb+srv://<user>:<pass>@cluster0.xyz.mongodb.net" -Db "FirstTry" -Collection "mediccrud"

## 10) Tests et vérifications à effectuer

Avant et après la migration, voici une liste de contrôles recommandés, le rôle de chaque script et comment les exécuter.

1) Pré-migration — qualité et nettoyage
- `scripts/check_doublons.py` : détecte et traite les doublons (génère `data/healthcare_dataset_purge.csv`).
  - Exécution : `python scripts/check_doublons.py`
- `scripts/check_integrity.py` : vérifie colonnes, valeurs manquantes, types mixtes et donne des recommandations.
  - Exécution : `python scripts/check_integrity.py`

2) Migration (automatisée)
- `scripts/run_backup_and_migrate.ps1` : automatise la sauvegarde, le drop, le dry-run et, sur confirmation, la migration complète.
  - Exécution (PowerShell) : `./scripts/run_backup_and_migrate.ps1`

3) Post-migration — validations rapides
- Vérifier la présence de documents :
  - `python scripts/migration_crud.py find --filter '{}' --limit 5`
- Créer les index recommandés :
  - `python scripts/migration_crud.py create_indexes`
  - Rôle : accélérer les recherches par `Name`, les filtres et tris par `Date of Admission`, les regroupements par `Medical Condition` et la détection de doublons via un index composé `Name + Date of Admission`. Un index texte sur `Medical Condition` aide la recherche libre.

4) Tests analytiques (exemples)
- `scripts/AgeByDesease.py` : calcule l'âge moyen par pathologie — exécution : `python scripts/AgeByDesease.py`
- `scripts/ByBlood.py` : histogramme des groupes sanguins — exécution : `python scripts/ByBlood.py`
- `scripts/MedicationByCancer.py` et `scripts/MedicationByCancerAndResults.py` : analyses spécifiques sur les traitements pour le cancer.

5) Scripts de validation CRUD (nouveaux)
- `scripts/validate_medication_by_cancer_crud.py` : exemple CRUD pour lister les médicaments prescrits aux patients avec une pathologie contenant 'Cancer'.
  - Exécution : `python scripts/validate_medication_by_cancer_crud.py`
- `scripts/validate_top_medications.py` : agrégation MongoDB pour lister les médicaments les plus prescrits chez les patients atteints de cancer.
  - Exécution : `python scripts/validate_top_medications.py`

Conseil : suivez l'ordre — nettoyage, sauvegarde, dry-run, migration complète, création d'index, puis validations analytiques.

### Exemples de résultats obtenus (validation)

- Nombre total de patients avec 'Cancer' dans `Medical Condition` (exemple exécuté) : 8294
- Top médicaments prescrits pour patients atteints de cancer (top 5) :
  1. Lipitor (1725)
  2. Ibuprofen (1683)
  3. Paracetamol (1669)
  4. Penicillin (1610)
  5. Aspirin (1607)

Exemple de tableau (format texte et Markdown) produit par `scripts/MedicationByCancerAndResults_crud.py` :

Médicament  | Tests | % Anormal | % Inconclusive | % Normal
-----------------------------------------------------------
Lipitor     |  1725 |    32.41% |         34.09% |   33.51%
Ibuprofen   |  1683 |    34.22% |         32.62% |   33.16%
Paracetamol |  1669 |    33.73% |         33.37% |   32.89%
Penicillin  |  1610 |     34.1% |          33.6% |    32.3%
Aspirin     |  1607 |    34.23% |         32.11% |   33.67%

Tableau Markdown (copier/coller) :

| Médicament | Tests | % Anormal | % Inconclusive | % Normal |
| --- | --- | --- | --- | --- |
| Lipitor | 1725 | 32.41% | 34.09% | 33.51% |
| Ibuprofen | 1683 | 34.22% | 32.62% | 33.16% |
| Paracetamol | 1669 | 33.73% | 33.37% | 32.89% |
| Penicillin | 1610 | 34.1% | 33.6% | 32.3% |
| Aspirin | 1607 | 34.23% | 32.11% | 33.67% |

Les index recommandés ont été créés sur la collection `FirstTry.mediccrud` (voir `migration_crud.py create_indexes`).
```

