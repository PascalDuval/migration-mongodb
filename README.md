# migration-mongodb

Ce dépôt contient des scripts Python pour préparer et migrer un jeu de données santé vers MongoDB, ainsi que plusieurs utilitaires d'analyse et de nettoyage.

Important : ce README n'évoque pas Docker — il explique comment cloner le projet, installer les dépendances et configurer MongoDB localement (Windows), puis lancer les scripts. Il inclut aussi des instructions pour se connecter et visualiser les données avec MongoDB Compass et pour utiliser MongoDB Atlas.

## Structure

- `scripts/` : scripts Python pour le nettoyage, la vérification, la migration et l'analyse (ex. `migration.py`, `check_doublons.py`, `check_integrity.py`, etc.).
- `data/` : jeux de données et schémas utilisés par les scripts. Contenu important :
  - `healthcare_dataset.csv` : dataset source (brut).
  - `healthcare_dataset_purge.csv` : dataset nettoyé (généré par `check_doublons.py`).
  - `FirstTry.medic2.json` : export JSON possible pour import dans MongoDB.
  - `schema-FirstTry-medic2-standardJSON.json` : schéma / mapping utile pour valider ou 

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

Installer les dépendances Python du projet :

```powershell
pip install -r requirements.txt
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

