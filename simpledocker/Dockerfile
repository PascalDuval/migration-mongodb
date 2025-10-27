# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY migration_crud.py .
COPY data ./data

RUN pip install --no-cache-dir pandas pymongo

ENTRYPOINT ["python", "migration_crud.py"]
