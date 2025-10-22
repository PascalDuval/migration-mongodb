# 🧬 migration-mongodb

Ce dépôt GitHub contient des scripts Python pour **préparer, nettoyer, migrer et analyser** un jeu de données médicales dans MongoDB.  
Il est hébergé sur :  
👉 **[https://github.com/PascalDuval/migration-mongodb](https://github.com/PascalDuval/migration-mongodb)**

---

## 🚀 Cloner le projet

Ouvrez un terminal PowerShell (Windows) ou bash (Linux/macOS) et exécutez :

```bash
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
````

Cela créera un dossier local `migration-mongodb/` contenant tous les scripts, données et tests du projet.

---

## 📁 Structure

* **`scripts/`** : scripts Python de migration, vérification et analyses CRUD.
  (ex. `migration_crud.py`, `check_doublons.py`, `TopHospitalCrud.py`, etc.)
* **`data/`** : jeux de données (`healthcare_dataset.csv`, `healthcare_dataset_purge.csv`).
* **`tests/`** : tests unitaires et d’intégration pour valider le bon fonctionnement du projet.

---

## 🧩 Organisation de la collection MongoDB

### Schéma de la collection `FirstTry.mediccrud`

| Type    | Champs principaux                                                                                                                               |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Chaînes | `Name`, `Medical Condition`, `Medication`, `Doctor`, `Hospital`, `Insurance Provider`, `Gender`, `Blood Type`, `Admission Type`, `Test Results` |
| Nombres | `Age`, `Billing Amount`, `Room Number`                                                                                                          |
| Dates   | `Date of Admission`, `Discharge Date`                                                                                                           |
| ID      | `_id` (`ObjectId` automatique)                                                                                                                  |

---

## ⚙️ Installation et environnement

### Prérequis

* **Python 3.10+**
* **MongoDB** (local ou Atlas)
* **pip** installé

### Installation recommandée (Windows PowerShell)

```powershell
python -m venv .venv
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> Principales dépendances : `pymongo`, `pandas`

---

## 🧾 Script principal : `scripts/migration_crud.py`

Ce script gère la **migration complète** du CSV nettoyé vers MongoDB.


### Fonctionnalités principales

* Import CSV → MongoDB (`import_csv`)
* Conversion automatique :

  * `Age` → entier
  * `Date of Admission` / `Discharge Date` → `datetime`
  * `Billing Amount` → float
* Création d’index
* Commandes CRUD (find, insert, update, delete)
* Mode `--dry` (voir ci-dessous)

---

## 🧪 Le mode `--dry` (dry-run)

Le mode `--dry` permet de **tester la migration sans rien insérer dans MongoDB**.
Les données sont lues, converties et affichées, mais **aucun `insert` n’est effectué**.

### Exemple :

```powershell
python scripts/migration_crud.py import_csv --dry
```

👉 Le script charge le CSV, effectue toutes les conversions de type,
et affiche un extrait des données converties sans modifier la base.

Ce mode est **idéal pour valider les conversions** avant une migration réelle.

---

## 🔍 Les conversions de types

Le script utilise des fonctions internes pour fiabiliser les types :

| Fonction         | Rôle                                          | Exemple                                  |
| ---------------- | --------------------------------------------- | ---------------------------------------- |
| `_safe_int()`    | Convertit une valeur en entier si possible    | `"42"` → `42`, `"abc"` → `None`          |
| `_to_datetime()` | Transforme une date texte en objet `datetime` | `"2024-01-10"` → `datetime(2024, 1, 10)` |
| `_safe_float()`  | Convertit une chaîne en float sécurisé        | `"10.5"` → `10.5`, `"n/a"` → `None`      |

Ces fonctions évitent que le script plante si le CSV contient des valeurs non conformes.

---

## ✅ Tests unitaires et d’intégration (`tests/`)

Une suite de tests pytest a été ajoutée pour vérifier que `migration_crud.py` fonctionne correctement.

### 📁 Fichier principal :

`scripts/tests/test_migration_crud.py`

### 🔧 Technologies utilisées :

* **pytest** → moteur de test Python
* **mongomock** → simule MongoDB sans serveur réel
* **pytest-mock** → gestion des mocks automatiques

### 🧩 Ce que les tests valident :

| Type de test             | Fonction testée                                        | Objectif                                        |
| ------------------------ | ------------------------------------------------------ | ----------------------------------------------- |
| **Unitaires**            | `_safe_int`, `_to_datetime`, `convert_dataframe_types` | Vérifient les conversions de type               |
| **CRUD simulé**          | `insert_one`, `find`, `update_one`, `delete_one`       | Vérifient les opérations CRUD sur base mockée   |
| **Indexation**           | `create_indexes`                                       | Vérifie la création des index                   |
| **Import CSV (dry-run)** | `import_csv`                                           | Vérifie la lecture et conversion sans insertion |

---

### 🧠 Explication : qu’est-ce qu’un `assert` ?

Un **`assert`** est une instruction de test :
elle vérifie qu’une condition est vraie.
Si elle ne l’est pas, le test échoue immédiatement.

Exemples :

```python
assert 1 + 1 == 2         # ✅ Passe
assert "Alice" in ["Bob"] # ❌ Échec
```

Dans nos tests :

```python
assert isinstance(records[0]["Age"], int)
```

➡️ Vérifie que le champ `Age` est bien un entier après conversion.

---

## 🧰 Lancer les tests

Depuis la racine du projet :

```bash
# Installer les dépendances de test
pip install pytest mongomock pytest-mock pandas

# Lancer les tests
pytest -v
```

### Exemple de sortie attendue :

```
==================== test session starts ====================
collected 9 items

tests/test_migration_crud.py .........                        [100%]

==================== 9 passed in 2.3s ========================
```

---

## 🔄 Quand exécuter les tests ?

🧪 Les tests doivent être exécutés **avant toute migration réelle**,
afin de s’assurer que :

* les conversions sont correctes,
* le CSV est bien lu,
* les index sont valides,
* et les opérations CRUD fonctionnent.

👉 Cela constitue une **phase de validation pré-migration**.

---

## 🧩 Tests d’intégration réels (optionnels)

En complément des tests mockés, il est possible de **tester sur une vraie base MongoDB locale**
(`mongodb://localhost:27017`).

Crée un fichier `tests/test_integration_real.py` contenant :

```python
from pymongo import MongoClient
import migration_crud as mc

def test_real_connection():
    client = MongoClient("mongodb://localhost:27017")
    db = client["FirstTry"]
    coll = db["mediccrud"]
    assert coll is not None
    assert isinstance(coll.count_documents({}), int)
```

Puis exécute :

```bash
pytest -v tests/test_integration_real.py
```

⚠️ Ces tests modifient potentiellement la base — à utiliser sur une copie ou une base de test.

---

## 📈  Résumé des étapes

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/PascalDuval/migration-mongodb.git
   cd migration-mongodb
   ```

2. Créer et activer un environnement virtuel :

   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Installer les dépendances :

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Nettoyer les données :

   ```bash
   python scripts/check_doublons.py
   ```

5. Vérifier l’intégrité :

   ```bash
   python scripts/check_integrity.py
   ```

6. **Exécuter les tests unitaires et d’intégration :**

   ```bash
   pytest -v
   ```

7. Si tout est vert ✅ :

   ```bash
   python scripts/migration_crud.py import_csv
   ```

8. Créer les index :

   ```bash
   python scripts/migration_crud.py create_indexes
   ```

9. Lancer les analyses CRUD afinb de vérifier que tout marche bien:

   ```bash
   python scripts/TopHospitalCrud.py
   python scripts/AgeByDeseaseCrud.py
   python scripts/MedicationByCancerAndResultsCrud.py
   etc...
   ```

---

## 💬 Support

Pour toute question ou suggestion :
👉 [Ouvrez une issue sur GitHub](https://github.com/PascalDuval/migration-mongodb/issues)

