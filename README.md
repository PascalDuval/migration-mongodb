# Migration MongoDB

Ce projet contient un script de migration vers MongoDB, conteneurisé avec Docker.

## Structure
- `/script` : contient le script Python de migration.
- `Dockerfile` : construit l’image Docker pour exécuter le script.

Pour importer les données dans MongoDB, lance le script principal :

```bash
python script/migration.py
```

Assure-toi d’avoir installé les dépendances Python :

```bash
pip install -r requirements.txt
```


## Utilisation
- Construire l’image : `docker build -t migration .`
- Lancer le conteneur : `docker run migration`