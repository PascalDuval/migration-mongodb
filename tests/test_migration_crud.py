"""
tests/test_migration_crud.py

Tests unitaires et d’intégration pour migration_crud.py
Utilise mongomock pour simuler une base MongoDB locale.
"""

import io
import json
import tempfile
import pandas as pd
import pytest
import mongomock
from datetime import datetime

import sys
from pathlib import Path

# Ajouter le dossier 'scripts' au PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))

import migration_crud as mc


# === FIXTURES ============================================================= #

@pytest.fixture
def mock_db(monkeypatch):
    """Simule une base MongoDB via mongomock et redéfinit get_collection()."""
    client = mongomock.MongoClient()
    db = client["FirstTry"]
    coll = db["mediccrud"]

    # get_collection doit retourner notre collection mockée
    monkeypatch.setattr(mc, "get_collection", lambda uri, db_name, coll_name: coll)

    return coll



@pytest.fixture
def sample_df():
    """Petit DataFrame pour tester la conversion."""
    return pd.DataFrame([
        {"Name": "Alice", "Age": "30", "Date of Admission": "2024-01-10"},
        {"Name": "Bob", "Age": "40", "Date of Admission": "2024-01-15"},
    ])


# === TESTS UNITAIRES ====================================================== #

def test_safe_int_conversion():
    assert mc._safe_int("10") == 10
    assert mc._safe_int("10.5") == 10
    assert mc._safe_int(None) is None
    assert mc._safe_int("abc") is None


def test_to_datetime_variants():
    assert isinstance(mc._to_datetime("2024-01-10"), datetime)
    assert mc._to_datetime(None) is None
    assert mc._to_datetime("not a date") is None


def test_convert_dataframe_types(sample_df):
    records = mc.convert_dataframe_types(sample_df)
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)
    assert isinstance(records[0]["Age"], int)
    assert isinstance(records[0]["Date of Admission"], datetime)


# === TESTS CRUD SIMULÉS =================================================== #

def test_insert_one(mock_db):
    """Teste l’insertion simple via insert_one()."""
    doc = '{"Name": "Charlie", "Age": "28", "Date of Admission": "2024-02-01"}'
    mc.insert_one("uri", "FirstTry", "mediccrud", doc)
    results = list(mock_db.find({}))
    assert len(results) == 1
    assert results[0]["Name"] == "Charlie"
    assert isinstance(results[0]["Date of Admission"], datetime)


def test_update_one(mock_db):
    mock_db.insert_one({"Name": "Alice", "Age": 30})
    mc.update_one("uri", "FirstTry", "mediccrud",
                  '{"Name": "Alice"}',
                  '{"Age": 35}')
    doc = mock_db.find_one({"Name": "Alice"})
    assert doc["Age"] == 35


def test_delete_one(mock_db):
    mock_db.insert_one({"Name": "Temp"})
    mc.delete_one("uri", "FirstTry", "mediccrud", '{"Name": "Temp"}')
    assert mock_db.count_documents({"Name": "Temp"}) == 0


def test_find_and_find_one(mock_db, capsys):
    mock_db.insert_many([
        {"Name": "Test1"}, {"Name": "Test2"}
    ])
    mc.find("uri", "FirstTry", "mediccrud", None, limit=1)
    output = capsys.readouterr().out
    assert "Test" in output

    mc.find_one("uri", "FirstTry", "mediccrud", '{"Name": "Test2"}')
    output = capsys.readouterr().out
    assert "Test2" in output


def test_create_indexes(mock_db):
    """Teste la création d’index (mongomock accepte create_index)."""
    mc.create_indexes("uri", "FirstTry", "mediccrud")
    indexes = mock_db.index_information()
    assert "idx_name" in indexes
    assert "idx_date_admission" in indexes
    assert "idx_medical_condition" in indexes


# === TESTS IMPORT CSV (avec dry-run) ===================================== #

def test_import_csv_dry_run(tmp_path, monkeypatch):
    """Crée un faux CSV temporaire et vérifie que dry-run fonctionne."""
    data = pd.DataFrame([
        {"Name": "Alice", "Age": "30", "Date of Admission": "2024-01-10"},
        {"Name": "Bob", "Age": "40", "Date of Admission": "2024-01-11"},
    ])
    csv_file = tmp_path / "test.csv"
    data.to_csv(csv_file, index=False)

    monkeypatch.setattr(mc, "get_collection", lambda uri, db, coll: mongomock.MongoClient()["FirstTry"]["mediccrud"])

    mc.import_csv("uri", "FirstTry", "mediccrud", str(csv_file), dry_run=True)
