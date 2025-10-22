# 🧬 migration-mongodb

Ce dépôt contient des scripts Python pour **préparer, nettoyer, migrer et analyser** un jeu de données de santé dans MongoDB.  
Certains scripts ont été modernisés pour fonctionner **en pur CRUD Python** (sans pipelines d’agrégation MongoDB), offrant une meilleure portabilité, lisibilité et maîtrise du traitement.

---

## 📁 Structure

- **`scripts/`** : scripts Python pour le nettoyage, la vérification, la migration et l’analyse.  
  (ex. `migration_crud.py`, `check_doublons.py`, `check_integrity.py`, etc.)
- **`data/`** : jeux de données utilisés :
  - `healthcare_dataset.csv` — dataset brut original.  
  - `healthcare_dataset_purge.csv` — dataset nettoyé (généré par `check_doublons.py`).  
---

## 🧩 Organisation de la collection MongoDB

### Schéma de la collection `FirstTry.mediccrud`

Chaque document comporte les champs :

| Type | Champs principaux |
|------|--------------------|
| Chaînes | `Name`, `Medical Condition`, `Medication`, `Doctor`, `Hospital`, `Insurance Provider`, `Admission Type`, `Gender`, `Blood Type`, `Test Results` |
| Nombres | `Age`, `Billing Amount`, `Room Number` |
| Dates | `Date of Admission`, `Discharge Date` |
| ID | `_id` (`ObjectId` généré automatiquement) |


---

## ⚙️ Index créés automatiquement

Création via :
```powershell
python scripts/migration_crud.py create_indexes
````

| Nom                          | Type        | Champ(s)                    | Utilisation                  |
| ---------------------------- | ----------- | --------------------------- | ---------------------------- |
| `_id_`                       | Automatique | `_id`                       | Index natif                  |
| `idx_name`                   | Simple      | `Name`                      | Recherche rapide par nom     |
| `idx_date_admission`         | Simple      | `Date of Admission`         | Filtres temporels            |
| `idx_medical_condition`      | Simple      | `Medical Condition`         | Regroupement pathologies     |
| `idx_name_date`              | Composé     | `Name`, `Date of Admission` | Combinaison identité + date  |
| `text_idx_medical_condition` | Texte       | `Medical Condition`         | Recherche textuelle efficace |

---

## 🚀 1) Cloner le projet

```powershell
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
```

---

## 🧠 2) Environnement et dépendances

### Prérequis

* Python 3.10+
* MongoDB (local - Compass/Atlas)
* `pip`

### Installation (Windows PowerShell)

```powershell
python -m venv .venv
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> 📦 Principales dépendances : `pymongo`, `pandas`

---

## 🗄️ 3) Démarrer MongoDB localement

### Étapes rapides

```powershell
mkdir C:\data\db
"C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath "C:\data\db"
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

### Interface graphique

Téléchargez [**MongoDB Compass**](https://www.mongodb.com/try/download/compass)
et connectez-vous à :

```
mongodb://localhost:27017
```

---

## ☁️ 4) Connexion à MongoDB Atlas (optionnel)

1. Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créez un cluster gratuit
3. Autorisez votre IP (`0.0.0.0/0` pour test)
4. Copiez l’URI de connexion et utilisez-la dans vos scripts :

   ```
   mongodb+srv://<user>:<password>@cluster0.mongodb.net
   ```

---

## 🧾 5) Script principal : `scripts/migration.py`

### Rôle

Importe le CSV lui-même préalablement nettoyé (`data/healthcare_dataset_purge.csv`) dans la collection MongoDB.

### Exécution

```powershell
python scripts/migration.py
```

### Détails

* Connexion à `mongodb://localhost:27017`
* Base : `FirstTry`, Collection : `mediccrud`
* Lecture du CSV → `insert_many`

---

## 📊 6) Scripts d’analyse CRUD Python

Les scripts d’analyse n'utilise pas des **pipelines MongoDB** ; ils ont été **réécrits en pur CRUD Python**. Ils effectuent leurs calculs côté client, directement en Python, pour plus de clarté et d’indépendance.

Tous utilisent :

* `functions_crud.crud_ops.get_collection()` pour la connexion.
* Des structures Python (`Counter`, `mean`, `pandas`) pour l’analyse.

### 🔍 Scripts disponibles

| Script                                        | Fonction                                                                                               | Méthode                                         |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `scripts/AverageAgeByConditionCrud.py`        | Calcule l’âge moyen (arrondi) des patients par pathologie.                                             | Lecture CRUD + moyenne Python                   |
| `scripts/BloodTypeDistributionCrud.py`        | Répartition des groupes sanguins avec pourcentages.                                                    | Lecture CRUD + `Counter()`                      |
| `scripts/MedicationByCancerAndResultsCrud.py` | Analyse des résultats de tests (Normal / Anormal / Inconclusive) pour chaque médicament lié au cancer. | Lecture CRUD + regroupement Python              |
| `scripts/ValidateTopMedicationsCrud.py`       | Médicaments les plus prescrits aux patients atteints de cancer.                                        | Lecture CRUD + tri Python                       |
| `scripts/DureeMoyenneSejourHospitalCrud.py`   | Calcule la durée moyenne des séjours hospitaliers.                                                     | Lecture CRUD + calcul de durée                  |
| `scripts/TopHospitalCrud.py`                  | Identifie l’hôpital avec le plus d’admissions.                                                         | Lecture CRUD + `Counter()`                      |
| `scripts/demo_crud_flow.py`                   | Démonstration complète des opérations CRUD.                                                            | Lecture / insertion / mise à jour / suppression |

### 🧠 Comparatif

| Avant (agrégation MongoDB) | Maintenant (CRUD Python)         |
| -------------------------- | -------------------------------- |
| `$group`, `$avg`, `$sort`  | Calculs via `Counter` / `mean()` |
| Calcul serveur             | Calcul client                    |
| Pipelines complexes        | Code simple et lisible           |
| Risque de `COLLSCAN`       | Lecture directe sur index        |

### ⚙️ Exécution - Exemples

```powershell
python scripts/AverageAgeByConditionCrud.py
python scripts/TopHospitalCrud.py
python scripts/ValidateTopMedicationsCrud.py --top 5
```

---

## 🧰 7) `scripts/migration_crud.py`

Script principal pour :

* Importer les données nettoyées (avec conversion automatique des types)
* Réaliser des opérations CRUD
* Créer et lister les index

### Exemples

```powershell
python scripts/migration_crud.py import_csv --dry
python scripts/migration_crud.py create_indexes
python scripts/migration_crud.py find --filter '{"Name": "Dupont"}' --limit 5
python scripts/migration_crud.py insert_one '{"Name": "Alice", "Age": 30}'
```

---

## 🔄 8) Workflow recommandé

1. **Cloner le dépôt**
2. **Créer un environnement virtuel**
3. **Installer MongoDB ou se connecter à Atlas**
4. **Nettoyer les données** → `check_doublons.py`
5. **Vérifier l’intégrité** → `check_integrity.py`
6. **Importer les données** → `migration_crud.py`
7. **Créer les index**
8. **Lancer les scripts d’analyse CRUD**

---

## ⚡ 9) Automatisation : `scripts/run_backup_and_migrate.ps1`

Script PowerShell pour :

* Sauvegarder la collection `mediccrud`
* Supprimer la collection existante
* Lancer un dry-run d’import
* Confirmer l’import complet

```powershell
./scripts/run_backup_and_migrate.ps1
```

Paramètres optionnels :

* `-Uri`, `-Db`, `-Collection`, `-Python`

---

## 🧪 10) Tests analytiques et validations

Avant et après migration, exécutez :

```powershell
python scripts/check_doublons.py
python scripts/check_integrity.py
python scripts/migration_crud.py create_indexes
python scripts/AverageAgeByConditionCrud.py
python scripts/TopHospitalCrud.py
```

---

## 📈 11) Exemple de résultat

| Médicament  | Tests | % Anormal | % Inconclusive | % Normal |
| ----------- | ----- | --------- | -------------- | -------- |
| Lipitor     | 1725  | 32.41%    | 34.09%         | 33.51%   |
| Ibuprofen   | 1683  | 34.22%    | 32.62%         | 33.16%   |
| Paracetamol | 1669  | 33.73%    | 33.37%         | 32.89%   |
| Penicillin  | 1610  | 34.10%    | 33.60%         | 32.30%   |
| Aspirin     | 1607  | 34.23%    | 32.11%         | 33.67%   |

---

## 💬 12) Support

En cas de problème ou suggestion d’amélioration :
👉 [Ouvrez une issue sur GitHub](https://github.com/PascalDuval/migration-mongodb/issues)

```

---

💡 **Prêt à copier-coller** : tout le contenu ci-dessus peut être inséré directement dans ton fichier  
`migration-mongodb/README.md`.  
Tu n’as rien à fusionner : c’est un seul document Markdown complet et cohérent.
```
