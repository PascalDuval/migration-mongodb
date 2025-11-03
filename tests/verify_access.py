#!/usr/bin/env python3
from __future__ import annotations

"""
Vérifications d'accès MongoDB basées sur les variables d'environnement (.env à la racine).

Valide que:
- le compte dbOwner peut insérer/supprimer sur la base applicative;
- le compte read-only peut lire mais ne peut pas écrire.

Utilisation:
  python -m pytest -q tests/verify_access.py   # en mode test
  python tests/verify_access.py                 # exécution directe (retourne 0/1)
"""

import os
import time
import uuid
from pymongo import MongoClient


def build_uri(user: str, pwd: str, host: str, port: int, db: str) -> str:
    return f"mongodb://{user}:{pwd}@{host}:{port}/{db}?authSource={db}"


def check_dbowner(uri: str, db: str) -> bool:
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    coll = client[db]["_role_probe"]
    tag = uuid.uuid4().hex[:8]
    doc = {"_probe": "dbowner", "tag": tag, "ts": time.time()}
    inserted_id = coll.insert_one(doc).inserted_id
    found = coll.find_one({"_id": inserted_id})
    deleted = coll.delete_one({"_id": inserted_id}).deleted_count
    return bool(found) and deleted == 1


def check_readonly(uri: str, db: str) -> bool:
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    coll = client[db]["__role_probe"]
    _ = coll.find_one({})
    try:
        coll.insert_one({"_probe": "readonly", "ts": time.time()})
        return False
    except Exception:
        return True


def main() -> int:
    host = os.getenv("MONGO_HOST", "localhost")
    port = int(os.getenv("MONGO_PORT", "27017"))
    db = os.getenv("MONGO_DB", "FirstTry")

    app_user = os.getenv("MONGO_APP_USERNAME")
    app_pwd = os.getenv("MONGO_APP_PASSWORD")
    ro_user = os.getenv("MONGO_READONLY_USERNAME")
    ro_pwd = os.getenv("MONGO_READONLY_PASSWORD")

    if not all([app_user, app_pwd, ro_user, ro_pwd]):
        print("Variables manquantes: MONGO_APP_*/MONGO_READONLY_* et MONGO_DB/MONGO_HOST/MONGO_PORT")
        return 2

    rw_uri = build_uri(app_user, app_pwd, host, port, db)
    ro_uri = build_uri(ro_user, ro_pwd, host, port, db)

    print("[Check] dbOwner insert/delete:", end=" ")
    ok_rw = check_dbowner(rw_uri, db)
    print("OK" if ok_rw else "FAIL")

    print("[Check] readOnly permissions:", end=" ")
    ok_ro = check_readonly(ro_uri, db)
    print("OK" if ok_ro else "FAIL")

    return 0 if (ok_rw and ok_ro) else 1


if __name__ == "__main__":
    raise SystemExit(main())

