# 🧬 Migration d'une base médicale vers MongoDB

Ce dépôt contient un ensemble de scripts Python pour **nettoyer**, **préparer**, **migrer** et **analyser** un jeu de données médicales dans MongoDB. Il constitue un support pédagogique complet pour comprendre toutes les étapes d'une migration de données depuis un fichier CSV vers une collection MongoDB.

> 📦 Dépôt public : [https://github.com/PascalDuval/migration-mongodb](https://github.com/PascalDuval/migration-mongodb)

---

## 📚 Sommaire

1. [Objectifs du projet](#-objectifs-du-projet)
2. [Contenu du dépôt](#-contenu-du-dépôt)
3. [Prérequis techniques](#-prérequis-techniques)
4. [Mise en place de l'environnement](#-mise-en-place-de-lenvironnement)
5. [Jeux de données fournis](#-jeux-de-données-fournis)
6. [Scripts disponibles](#-scripts-disponibles)
7. [Organisation de la base MongoDB](#-organisation-de-la-base-mongodb)
8. [Utilisation détaillée](#-utilisation-détaillée)
9. [Tests automatiques](#-tests-automatiques)
10. [FAQ & dépannage](#-faq--dépannage)
11. [Contribution & support](#-contribution--support)
12. [Licence](#-licence)

---

## 🎯 Objectifs du projet

* Illustrer la migration d'un jeu de données médicales vers MongoDB en respectant les bonnes pratiques.
* Montrer comment fiabiliser les types de données (dates, nombres, montants, etc.).
* Proposer un ensemble de scripts CRUD d'analyse pour vérifier la qualité des données une fois migrées.
* Fournir une base de tests (unitaires et d'intégration) permettant de valider la chaîne de migration.

---

## 🗂️ Contenu du dépôt

migration-mongodb/
├── data/ # Jeux de données bruts et nettoyés
├── scripts/ # Scripts de migration, nettoyage et analyses CRUD
├── tests/ # Suite de tests pytest (unitaires + intégration)
├── Dockerfile # Image de développement/exécution optionnelle
├── requirements.txt # Dépendances nécessaires à l'exécution des scripts
├── requirements-tests.txt # Dépendances supplémentaires pour la suite de tests
└── README.md # Ce fichier

yaml
Copier le code

### Dossiers principaux

| Dossier | Description |
| ------- | ----------- |
| `scripts/` | Contient l'ensemble des scripts Python : migration, nettoyage, contrôles d'intégrité, analyses CRUD. |
| `data/` | Fichiers CSV (original + version purgée). |
| `tests/` | Tests automatisés basés sur `pytest`, `mongomock` et `pytest-mock`. |

---

## 🧰 Prérequis techniques

| Outil | Version recommandée | Notes |
| ----- | ------------------- | ----- |
| Python | 3.10 ou supérieur | Utilisé pour tous les scripts et tests. |
| MongoDB | 6.x (local ou Atlas) | Une instance locale suffit pour les tests manuels. |
| pip | Version la plus récente | Gestionnaire de paquets Python. |
| Git | Optionnel | Pour cloner et versionner le projet. |

---

## ⚙️ Mise en place de l'environnement

### 1. Cloner le dépôt

```bash
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
2. Créer et activer un environnement virtuel (Windows PowerShell)
powershell
Copier le code
python -m venv .venv
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
Linux / macOS

bash
Copier le code
python -m venv .venv
source .venv/bin/activate
3. Installer les dépendances
bash
Copier le code
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Pour exécuter également les tests automatisés :

bash
Copier le code
python -m pip install -r requirements-tests.txt
4. Configurer MongoDB (optionnel mais recommandé)
Installez MongoDB Community Server ou créez un cluster Atlas.

Créez une base FirstTry et une collection mediccrud (elles seront créées automatiquement lors de l'import si elles n'existent pas).

Assurez-vous d'avoir un utilisateur avec droits de lecture/écriture si vous utilisez Atlas.

🧾 Jeux de données fournis
Fichier	Description
data/healthcare_dataset.csv	Fichier source brut (peut contenir des doublons ou incohérences).
data/healthcare_dataset_purge.csv	Version nettoyée, prête pour la migration.

Le script scripts/check_doublons.py permet de détecter les doublons et de produire la version purgée.

🛠️ Scripts disponibles
Migration & préparation
Script	Rôle principal	Commandes clés
migration_crud.py	Migration et opérations CRUD sur la collection	import_csv, create_indexes, find, insert, update, delete, --dry
check_doublons.py	Détection et suppression des doublons dans le CSV	Génère healthcare_dataset_purge.csv
check_integrity.py	Vérifications basiques d'intégrité des données	Contrôle des colonnes essentielles

Analyses CRUD
Script	Description
TopHospitalCrud.py	Classement des hôpitaux par nombre de patients.
AgeByDeseaseCrud.py	Analyse de l'âge moyen par pathologie.
MedicationByCancerAndResultsCrud.py	Regroupe les patients par médicament, cancer et résultat des tests.
TopInsuranceCrud.py	Exemple supplémentaire d'analyse des assurances (à adapter selon vos besoins).

ℹ️ Tous les scripts prennent en charge les variables d'environnement MONGO_URI, MONGO_DB et MONGO_COLLECTION pour configurer la connexion.

🗃️ Organisation de la base MongoDB
Collection principale : FirstTry.mediccrud
Type	Champs principaux
Chaînes	Name, Medical Condition, Medication, Doctor, Hospital, Insurance Provider, Gender, Blood Type, Admission Type, Test Results
Nombres	Age, Billing Amount, Room Number
Dates	Date of Admission, Discharge Date
ID	_id (ObjectId généré automatiquement)

Index recommandés
Le script migration_crud.py create_indexes crée des index pour accélérer les recherches :

Index composé sur ("Medical Condition", "Hospital")

Index simple sur "Name"

Index simple sur "Insurance Provider"

▶️ Utilisation détaillée
1. Nettoyer et préparer les données
bash
Copier le code
python scripts/check_doublons.py
python scripts/check_integrity.py
Ces scripts génèrent la version nettoyée du CSV et valident les colonnes critiques.

2. Simuler la migration (mode dry-run)
bash
Copier le code
python scripts/migration_crud.py import_csv --dry
Lecture du CSV nettoyé (healthcare_dataset_purge.csv).

Conversion des types (Age → int, Billing Amount → float, dates → datetime).

Affichage d'un échantillon de documents sans insertion dans MongoDB.

3. Importer réellement les données
bash
Copier le code
python scripts/migration_crud.py import_csv
4. Créer les index
bash
Copier le code
python scripts/migration_crud.py create_indexes
5. Lancer des analyses CRUD
bash
Copier le code
python scripts/TopHospitalCrud.py
python scripts/AgeByDeseaseCrud.py
python scripts/MedicationByCancerAndResultsCrud.py
Adaptez les scripts d'analyse à vos propres besoins pour explorer les données.

✅ Tests automatiques
La suite de tests se trouve dans le dossier tests/ et se base sur pytest + mongomock pour simuler MongoDB.

Installation des dépendances de test
bash
Copier le code
python -m pip install -r requirements-tests.txt
Exécution des tests
bash
Copier le code
pytest -v
Contenu des tests
Type	Fichiers	Objectif
Unitaires	tests/test_migration_crud.py	Vérifie les fonctions internes (_safe_int, _to_datetime, convert_dataframe_types, etc.).
Intégration simulée	tests/test_migration_crud.py	Teste l'ensemble des opérations CRUD avec mongomock.

Tests sur une vraie base (optionnel)
Créez tests/test_integration_real.py pour valider la connexion à une instance réelle :

python
Copier le code
from pymongo import MongoClient
import scripts.migration_crud as mc

def test_real_connection():
    client = MongoClient("mongodb://localhost:27017")
    db = client["FirstTry"]
    coll = db["mediccrud"]
    assert coll is not None
    assert isinstance(coll.count_documents({}), int)
Puis exécutez :

bash
Copier le code
pytest -v tests/test_integration_real.py
🆘 FAQ & Dépannage
<details> <summary>🚫 "Connection refused" lors de la connexion à MongoDB</summary>
Vérifiez que le service MongoDB est démarré (mongod).

Si vous utilisez MongoDB Atlas, assurez-vous que votre IP est autorisée dans le réseau.

Vérifiez la variable d'environnement MONGO_URI.

</details> <details> <summary>📄 Quel CSV est utilisé par défaut ?</summary>
Le script migration_crud.py utilise data/healthcare_dataset_purge.csv. Vous pouvez changer ce comportement en modifiant la constante DEFAULT_DATA_FILE dans le script.

</details> <details> <summary>🗓️ Mes dates ne sont pas converties correctement</summary>
Utilisez le mode --dry pour inspecter les conversions. Les dates doivent être au format ISO (YYYY-MM-DD) ou un format reconnu par pandas.to_datetime.

</details> <details> <summary>🧪 Comment ajouter un nouveau test ?</summary>
Créez un nouveau fichier dans tests/ (ex. test_top_hospital.py) et utilisez mongomock pour simuler la collection. Inspirez-vous de tests/test_migration_crud.py.

</details>
🤝 Contribution & support
Forkez le dépôt.

Créez une branche dédiée : git checkout -b feature/ma-fonctionnalite.

Faites vos modifications et ajoutez des tests lorsque c'est pertinent.

Lancez pytest -v avant de soumettre votre Pull Request`.

Soumettez une PR descriptive.

Pour toute question : ouvrez une issue.

📜 Licence
Ce projet est distribué sous la licence MIT.

Bon apprentissage et bonne migration ! 🚀