# Migration MongoDB

Ce projet contient un script de migration vers MongoDB, conteneurisé avec Docker.

## Structure
- `/scripts` : contient le script Python de migration.
- `Dockerfile` : construit l’image Docker pour exécuter le script.

Pour importer les données dans MongoDB, lance le script principal :

# migration-mongodb

Ce dépôt contient des scripts Python pour préparer et migrer un jeu de données santé vers MongoDB, ainsi que plusieurs utilitaires d'analyse et de nettoyage.

Important : ce README n'évoque pas Docker — il explique comment cloner le projet, installer les dépendances et configurer MongoDB localement (Windows), puis lancer les scripts.

## 1) Cloner le projet

Ouvrez un terminal et exécutez :

```powershell
git clone https://github.com/PascalDuval/migration-mongodb.git
cd migration-mongodb
```

## 2) Prérequis

- Python 3.10+ installé (Windows). Vérifiez avec : `python --version`.
- Pip (gestionnaire de paquets Python).
- MongoDB installé et accessible localement (instructions ci-dessous).

Installer les dépendances Python du projet :

```powershell
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient au minimum :

- pymongo (client MongoDB)
- pandas (pour certains scripts d'analyse)

## 3) Installer et démarrer MongoDB (Windows)

Voici une procédure simple pour installer MongoDB Community Server sur Windows et l'exécuter localement :

1. Téléchargez l'installateur MSI depuis le site officiel : https://www.mongodb.com/try/download/community
2. Lancez l'installateur et choisissez l'installation « Complete ».
3. Pendant l'installation, vous pouvez cocher l'option « Install MongoDB as a Service ». Si vous choisissez cette option, MongoDB démarrera automatiquement comme service Windows.
4. Si vous préférez démarrer MongoDB manuellement, repérez le dossier d'installation (par défaut `C:\Program Files\MongoDB\Server\<version>\bin`) et lancez :

```powershell
"C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath "C:\data\db"
```

Remplacez `<version>` par votre version. Créez le dossier `C:\data\db` si nécessaire :

```powershell
mkdir C:\data\db
```

5. Vérifiez que MongoDB écoute sur le port 27017 (par défaut) :

```powershell
mongo --eval "db.runCommand({ connectionStatus: 1 })"
```

Si la commande `mongo` n'est pas disponible, utilisez le client `mongosh` (fourni avec les nouvelles versions) ou testez la connexion depuis Python (ex : `pymongo.MongoClient('mongodb://localhost:27017')`).

## 4) Script principal : `scripts/migration.py`

But
- Importer un fichier CSV nettoyé dans une collection MongoDB.

Comportement (par défaut)
- Se connecte à MongoDB sur `mongodb://localhost:27017`.
- Utilise la base `FirstTry` et la collection `medic2`.
- Lit le fichier CSV situé par défaut dans `data/healthcare_dataset_purge.csv`.
- Insère tous les enregistrements lus via `insert_many` puis affiche 5 documents insérés.

Exécution

```powershell
python scripts/migration.py
```

Remarques utiles
- Assurez-vous que MongoDB est démarré et accessible.
- Vous pouvez modifier le chemin du fichier CSV directement dans `scripts/migration.py` si nécessaire.
- Le script lit les lignes CSV en tant que dictionnaires (DictReader) — il n'effectue pas de transformation de types (dates, nombres) : si vous avez besoin d'un prétraitement, nettoyez et convertissez les champs avec les scripts du dossier `scripts/` avant d'importer.

## 5) Autres scripts disponibles (description rapide)

Tous les scripts se trouvent dans le dossier `scripts/`. Ci-dessous un résumé et la commande d'exécution :

- `scripts/check_integrity.py`
	- Vérifie l'intégrité d'un fichier CSV/Excel (`../data/healthcare_dataset_purge.csv` par défaut).
	- Signale colonnes manquantes, valeurs nulles, doublons et donne des recommandations.
	- Exécution : `python scripts/check_integrity.py`

- `scripts/check_doublons.py`
	- Détecte et traite automatiquement les doublons selon des règles (nom, âge proche, etc.).
	- Fusionne ou supprime les lignes en fonction des différences de diagnostic ou date d'admission.
	- Lit `../data/healthcare_dataset.csv` et écrit `../data/healthcare_dataset_purge.csv`.
	- Exécution : `python scripts/check_doublons.py`

- `scripts/AgeByDesease.py`
	- Calcule l'âge moyen par pathologie à partir de la collection MongoDB (agrégation MongoDB puis sortie via pandas).
	- Exécution : `python scripts/AgeByDesease.py`

- `scripts/ByBlood.py`
	- Génère un histogramme (tableau) des groupes sanguins à partir de la collection MongoDB (avec pourcentages).
	- Exécution : `python scripts/ByBlood.py`

- `scripts/MedicationByCancer.py` et `scripts/MedicationByCancerAndResults.py`
	- Scripts d'analyse des traitements médicamenteux pour les patients atteints de cancer.
	- Exécution : `python scripts/MedicationByCancer.py`

- `scripts/DureeMoyenneSejourHopital.py`
	- Calcule la durée moyenne de séjour à partir des données (aggregation attendue dans MongoDB).
	- Exécution : `python scripts/DureeMoyenneSejourHopital.py`

- `scripts/TopHospital.py`
	- Identifie les hôpitaux les plus fréquents dans le dataset.
	- Exécution : `python scripts/TopHospital.py`

- `scripts/CrudTry1.py`
	- Script d'essai pour opérations CRUD sur MongoDB (insérer, lire, mettre à jour, supprimer).
	- Exécution : `python scripts/CrudTry1.py`

- `scripts/check_integrity_json.py`
	- Variante de vérification d'intégrité spécialisée pour JSON/format spécifique.
	- Exécution : `python scripts/check_integrity_json.py`

> Remarque : plusieurs scripts se connectent à `mongodb://localhost:27017` et à la base `FirstTry` / collection `medic2`. Adaptez la connexion si vous utilisez une autre base/collection ou des identifiants.

## 6) Exemple de workflow recommandé

1. Cloner le dépôt.
2. Installer Python et les dépendances (`pip install -r requirements.txt`).
3. Installer/démarrer MongoDB localement.
4. Nettoyer les données brutes : `python scripts/check_doublons.py` (génère `healthcare_dataset_purge.csv`).
5. Vérifier l'intégrité : `python scripts/check_integrity.py`.
6. Lancer la migration : `python scripts/migration.py`.
7. Lancer des analyses depuis MongoDB (`AgeByDesease.py`, `ByBlood.py`, etc.).

## 7) Bonnes pratiques et conseils

- Sauvegardez toujours votre CSV original avant d'exécuter les scripts de purge.
- Testez les scripts sur un petit sous-ensemble de données avant de lancer une importation complète.
- Si vos champs contiennent des dates ou des nombres, adaptez `migration.py` pour convertir les types avant insertion (par ex. convertir `Age` en int, `Date of Admission` en ISODate).

## 8) Besoin d'aide ?

Ouvrez une issue sur le dépôt GitHub : https://github.com/PascalDuval/migration-mongodb/issues

---
Résumé des changements : mise à jour complète du README pour expliquer le clonage, l'installation (Python et MongoDB sous Windows), l'exécution du script principal `migration.py` et la description des autres scripts.