FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY routines/ ./routines/
COPY data/ ./data

ENV PYTHONPATH=/app

# Étape 6 : définir l'entrée par défaut (scripts/migration_crud.py)
ENTRYPOINT ["python", "scripts/migration_crud.py"]
CMD ["--help"]