FROM python:3.9-slim
WORKDIR /app
COPY script/migration.py .
CMD ["python", "migration.py"]