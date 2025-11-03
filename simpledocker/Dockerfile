FROM python:3.11-slim
WORKDIR /app
# Installer les dépendances
RUN pip install --no-cache-dir pandas pymongo
# Scripts principaux
COPY migration_crud.py .
COPY demo_crud_flow.py .
# Scripts d’analyse
COPY routines ./routines/
# Données CSV
COPY data ./data/

