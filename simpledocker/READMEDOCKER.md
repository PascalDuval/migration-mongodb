Parfait, tu joues le rôle de l’utilisateur final 👷. Voici exactement ce qu’il te faut 👇

---

## ✅ Liste des fichiers nécessaires

Le projet doit contenir **exactement** ces fichiers/structures :

```
migration-project/
│
├── .env                           ← ✅ Fichier d’environnement (MongoDB credentials)
├── docker-compose.yml             ← ✅ Lance MongoDB + script de migration
├── Dockerfile                     ← ✅ Build du service de migration
├── migration_crud.py              ← ✅ Ton script Python de migration (fourni)
│
├── mongo-init/                    ← ✅ Scripts d'initialisation MongoDB
│   └── 01-create-user.sh
│
├── data/                          ← ✅ Contient le fichier CSV à importer
│   └── healthcare_dataset_purge.csv
│
└── README.md                      ← ✅ Pour l’utilisateur
```

---

## 📘 README.md — à donner à l'utilisateur final

```markdown
# 📦 Migration MongoDB en Docker

Ce projet permet d’importer un fichier CSV dans une base MongoDB **automatiquement** à l’aide de Docker Compose.

---

## ✅ Pré-requis

- [Docker installé](https://docs.docker.com/get-docker/)
- [Docker Compose v2+](https://docs.docker.com/compose/install/)

---

## 📁 Fichiers nécessaires

Assurez-vous d’avoir les fichiers suivants :

```

.
├── .env
├── docker-compose.yml
├── Dockerfile
├── migration_crud.py
├── mongo-init/01-create-user.sh
└── data/healthcare_dataset_purge.csv

```

---

## ⚙️ Variables de configuration

Contenues dans le fichier `.env` :

```

MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=rootpass
MONGO_APP_USERNAME=appuser
MONGO_APP_PASSWORD=apppass
MONGO_DB=FirstTry

````

> Vous pouvez modifier ces valeurs selon vos besoins.

---

## 🚀 Lancer la migration

Dans le terminal :

```bash
docker compose up --build
````

🛠️ Ce que ça fait :

1. Démarre MongoDB avec un utilisateur configuré
2. Lance automatiquement `migration_crud.py` pour importer le fichier `data/healthcare_dataset_purge.csv`

---

## 🔁 Autres commandes manuelles

```bash
docker compose run --rm migration find --filter '{"Age": {"$gt": 40}}'
```

---

## 🧼 Nettoyage

Pour supprimer tous les conteneurs + volumes :

```bash
docker compose down -v
```

---

## 🧠 Notes

* Le script `migration_crud.py` supporte aussi `insert_one`, `update_one`, `delete_one`, etc.
* La base MongoDB par défaut est `FirstTry` avec une collection `mediccrud`.

````

---

## ❓ Dois-tu supprimer ta base MongoDB existante ?

Pas forcément. Deux cas :

### ✅ Si ta base existante **ne contient pas** de documents critiques :
Tu peux **l’effacer sans souci** :

```bash
docker exec -it mongo mongosh -u root -p rootpass
> use FirstTry
> db.mediccrud.drop()
````

Sinon...

### 🔁 Si tu veux préserver tes données :

Lance le projet tel quel, il va simplement **ajouter les nouveaux documents**.

* Mais attention aux doublons si les documents du CSV sont déjà présents !

---

