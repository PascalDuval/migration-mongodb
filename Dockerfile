# Étape 1 : partir d'une image Python légère
FROM python:3.9-slim

# Étape 2 : définir le dossier de travail
WORKDIR /app

# Étape 3 : copier les fichiers nécessaires
# (requirements.txt en premier pour tirer parti du cache Docker)
COPY requirements.txt ./

# Étape 4 : installer les dépendances Python sans cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : copier ton script Python
COPY scripts/migration.py .

# Étape 6 : définir la commande par défaut au lancement du conteneur
CMD ["python", "migration.py"]
