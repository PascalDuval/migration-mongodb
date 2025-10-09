# Migration MongoDB

Ce projet contient un script de migration vers MongoDB, conteneurisé avec Docker.

## Structure
- `/script` : contient le script Python de migration.
- `Dockerfile` : construit l’image Docker pour exécuter le script.

## Utilisation
- Construire l’image : `docker build -t migration .`
- Lancer le conteneur : `docker run migration`

