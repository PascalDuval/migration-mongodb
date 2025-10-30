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
- Proposer des scripts CRUD d'analyse pour vérifier la qualité des données une fois migrées.
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
├─ scripts/                 # Scripts de migration, nettoyage, intégrité et helpers CRUD
│  ├─ functions_crud/       # Utilitaires Python 
├─ tests/                   # Suite de tests (pytest, mongomock)
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

### 4) Configurer MongoDB (optionnel mais recommandé)

- Installez MongoDB Community Server ou créez un cluster Atlas.
- Base par défaut: `FirstTry`, collection: `mediccrud` (créées automatiquement lors de l'import si absentes).
- Assurez-vous de disposer d'un utilisateur avec droits lecture/écriture (surtout sur Atlas).

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
| `scripts/migration_crud.py` | Migration et opérations CRUD (import, index, find, etc.) |
| `scripts/check_doublons.py` | Détection et suppression des doublons dans le CSV        |
| `scripts/check_integrity.py`| Vérifications basiques d'intégrité des données           |

### Analyses CRUD (routines)

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

Index recommandés (créés par `migration_crud.py create_indexes`):

- Index composé sur (`Medical Condition`, `Hospital`)
- Index simple sur `Name`
- Index simple sur `Insurance Provider`

---

<a id="utilisation-detaillee"></a>
## Utilisation détaillée

1) Nettoyer et préparer les données
```bash
python scripts/check_doublons.py
python scripts/check_integrity.py
```

2) Simuler la migration (dry-run)
```bash
python scripts/migration_crud.py import_csv --dry
```
Affiche un échantillon de documents convertis (sans insertion).

3) Importer réellement les données
```bash
python scripts/migration_crud.py import_csv
```

4) Créer les index
```bash
python scripts/migration_crud.py create_indexes
```

5) Lancer des analyses CRUD
```bash
python routines/TopHospital.py
python routines/AgeByDesease.py
python routines/MedicationByCancerAndResults.py
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

- `tests/test_migration_crud.py` vérifie les fonctions internes (`_safe_int`, `_to_datetime`, `convert_dataframe_types`, etc.) et des opérations CRUD (avec `mongomock`).

Tests sur une vraie base (optionnel): créez `tests/test_integration_real.py` si nécessaire.

---

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

