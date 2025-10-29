Parfait 👌 tu veux un **README unique, complet, clair et professionnel**, avec :

* la doc utilisateur,
* la doc d’admin (création des rôles, scripts d’init),
* les commandes de test et vérification,
* les explications détaillées du fonctionnement Docker/MongoDB.

Voici ton **`READMEDOCKER.md`** final — prêt à livrer 📘💪

---

# 📦 Migration MongoDB + Scripts d’analyse Dockerisés

Ce projet permet :

* d’importer automatiquement un fichier CSV dans MongoDB,
* d’exécuter des scripts CRUD ou analytiques situés dans `routines/`,
* d’exécuter un flow de démo (`demo_crud_flow.py`) en environnement Dockerisé.

---

## ✅ 1. Pré-requis

* Docker Desktop
* Docker Compose v2+

---

## 📁 2. Structure attendue

```bash
.
├── .env
├── docker-compose.yml
├── Dockerfile
├── migration_crud.py
├── demo_crud_flow.py
│
├── routines/
│   ├── MedicationByCancerAndResults.py
│   ├── AgeByDesease.py
│   ├── DureeMoyenneSejourHospital.py
│   └── ...
│
├── mongo-init/
│   ├── 01-create-user.sh          # ← Crée l’utilisateur principal appuser (readWrite)
│   ├── 02-create-readonly-user.sh # ← Crée un utilisateur lecture seule readonly
│   ├── 03-create-dbowner.sh       # ← Crée un administrateur local dbowner
│
└── data/
    └── healthcare_dataset_purge.csv
```

---

## ⚙️ 3. Variables d’environnement (`.env`)

```bash
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=rootpass

MONGO_APP_USERNAME=appuser
MONGO_APP_PASSWORD=apppass
MONGO_DB=FirstTry
```

Ces variables configurent le compte administrateur (`root`) et l’application (`appuser`).

---

## 🚀 4. Lancer le projet + migration automatique

```bash
docker compose up --build
```

🔄 Cette commande :

1. Démarre MongoDB
2. Exécute les scripts d’initialisation dans `mongo-init/`
3. Crée les utilisateurs (`appuser`, `readonly`, `dbowner`)
4. Lance `migration_crud.py` pour importer les données du fichier CSV dans `FirstTry.mediccrud`

---

## 🧩 5. Scripts d’initialisation (`mongo-init/*.sh`)

MongoDB exécute **automatiquement tous les scripts `.sh` et `.js`** contenus dans `mongo-init/` **au premier démarrage** du conteneur.

### 🧱 Ordre d’exécution

L’ordre dépend du nom du fichier (ordre alphabétique) :

```
01-create-user.sh
02-create-readonly-user.sh
03-create-dbowner.sh
```

---

### 🔐 Exemple : `01-create-user.sh`

```bash
#!/bin/bash
echo "🔐 Initialisation de la base MongoDB..."

mongosh <<EOF
use FirstTry
db.createUser({
  user: 'appuser',
  pwd: 'apppass',
  roles: [{ role: 'readWrite', db: 'FirstTry' }]
})
EOF
```

👉 Crée un utilisateur d’application (`appuser`) qui peut **lire et écrire** dans la base `FirstTry`.

---

### 👁️ `02-create-readonly-user.sh`

```bash
#!/bin/bash
echo "👁️ Création de l'utilisateur en lecture seule (readonly)..."

mongosh <<EOF
use FirstTry
db.createUser({
  user: 'readonly',
  pwd: 'readonly123',
  roles: [{ role: 'read', db: 'FirstTry' }]
})
EOF
```

👉 Crée un utilisateur avec **accès en lecture seule**.

---

### 🛠️ `03-create-dbowner.sh`

```bash
#!/bin/bash
echo "🛠️ Création de l'utilisateur dbOwner..."

mongosh <<EOF
use FirstTry
db.createUser({
  user: 'dbowner',
  pwd: 'dbowner123',
  roles: [{ role: 'dbOwner', db: 'FirstTry' }]
})
EOF
```

👉 Crée un administrateur local avec **tous les droits sur la base `FirstTry`** :

* lecture/écriture,
* gestion des index,
* création de collections, etc.

---

## 📚 6. Rôles MongoDB (résumé rapide)

| Rôle        | Description                                               |
| ----------- | --------------------------------------------------------- |
| `read`      | Lecture seule                                             |
| `readWrite` | Lecture + écriture                                        |
| `dbAdmin`   | Administration de la base (index, stats, validation)      |
| `userAdmin` | Gestion des utilisateurs sur une base donnée              |
| `dbOwner`   | Plein contrôle sur une base spécifique                    |
| `root`      | Accès total à toutes les bases (super utilisateur global) |

---

## 🧪 7. Vérification après lancement

### 🧾 Vérifier les utilisateurs créés

```bash
docker exec -it mongo mongosh -u root -p rootpass
```

Puis dans le shell :

```js
use FirstTry
db.getUsers()
```

Tu devrais obtenir une sortie du type :

```json
[
  { "user": "appuser", "roles": [ { "role": "readWrite", "db": "FirstTry" } ] },
  { "user": "readonly", "roles": [ { "role": "read", "db": "FirstTry" } ] },
  { "user": "dbowner", "roles": [ { "role": "dbOwner", "db": "FirstTry" } ] }
]
```

---

### 🔄 Modifier les droits d’un utilisateur

Pour donner un rôle supplémentaire à `appuser` (par exemple `dbAdmin`) :

```bash
docker exec -it mongo mongosh -u root -p rootpass
```

```js
use FirstTry
db.updateUser("appuser", {
  roles: [
    { role: "readWrite", db: "FirstTry" },
    { role: "dbAdmin", db: "FirstTry" }
  ]
})
```

---

### 🔍 Tester la connexion avec chaque utilisateur

#### 🔹 Appuser (lecture + écriture)

```bash
docker exec -it mongo mongosh -u appuser -p apppass --authenticationDatabase FirstTry
use FirstTry
db.mediccrud.findOne()
db.mediccrud.insertOne({ test: "OK" })
```

#### 🔹 Readonly (lecture seule)

```bash
docker exec -it mongo mongosh -u readonly -p readonly123 --authenticationDatabase FirstTry
use FirstTry
db.mediccrud.findOne()
db.mediccrud.insertOne({ test: "KO" })  // ❌ Erreur attendue
```

#### 🔹 DbOwner (admin local)

```bash
docker exec -it mongo mongosh -u dbowner -p dbowner123 --authenticationDatabase FirstTry
use FirstTry
db.createCollection("test_collection")
```

---

## 📊 8. Vérifier les données importées

### ▶️ Depuis le shell MongoDB

```bash
docker exec -it mongo mongosh -u appuser -p apppass --authenticationDatabase FirstTry
```

```js
use FirstTry
db.mediccrud.countDocuments()
db.mediccrud.findOne()
```

### ▶️ Depuis le conteneur de migration

```bash
docker compose run --rm migration python migration_crud.py find --limit 3
```

---

## 🧰 9. Exécuter les scripts d’analyse

```bash
docker compose run --rm migration python routines/MedicationByCancerAndResults.py
docker compose run --rm migration python routines/PatientsByCity.py
docker compose run --rm migration python routines/ResultsByAgeGroup.py
```

---

## 🧪 10. Lancer la démo CRUD complète

```bash
docker compose run --rm migration python demo_crud_flow.py
```

---

## 🧹 11. Nettoyer

### Supprimer les conteneurs + volumes :

```bash
docker compose down -v
```

### Supprimer seulement la collection :

```bash
docker exec -it mongo mongosh -u root -p rootpass
use FirstTry
db.mediccrud.drop()
```

---

## 📌 12. Notes utiles

* Base MongoDB : `FirstTry`
* Collection principale : `mediccrud`
* URI Mongo standard :

  ```bash
  mongodb://appuser:apppass@mongo:27017/FirstTry?authSource=FirstTry
  ```

---

## 🎯 13. Exemple de test complet

```bash
docker compose down -v          # Réinitialiser tout
docker compose up --build       # Lancer la migration automatique
docker compose run --rm migration python routines/MedicationByCancerAndResults.py
docker exec -it mongo mongosh -u root -p rootpass --eval "use FirstTry; db.getUsers();"
```

---

🧠 **Résumé rapide**

* Les scripts `mongo-init` créent automatiquement les comptes utilisateurs.
* `migration_crud.py` importe le CSV et gère les opérations CRUD.
* Les scripts dans `routines/` font des analyses personnalisées.
* Tout est isolé et reproductible via Docker.
