#!/usr/bin/env python3
"""
Idempotent MongoDB user setup (no docker-entrypoint init scripts).

Creates/updates:
- app dbOwner: MONGO_APP_USERNAME / MONGO_APP_PASSWORD (on APP_DB)
- read-only:   MONGO_READONLY_USERNAME / MONGO_READONLY_PASSWORD (on APP_DB)

Reads configuration from environment variables by default, and allows CLI overrides.
Does NOT print secrets.
"""
from __future__ import annotations

import os
import argparse
from typing import List, Dict, Any
from pymongo import MongoClient


def _required_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise SystemExit(f"Missing required environment variable: {name}")
    return val


def users_info(db, username: str) -> Dict[str, Any] | None:
    try:
        res = db.command({"usersInfo": username})
        users = res.get("users", [])
        return users[0] if users else None
    except Exception:
        return None


def ensure_user(db, username: str, password: str, roles: List[Dict[str, str]]):
    exists = users_info(db, username)
    if not exists:
        db.command(
            {
                "createUser": username,
                "pwd": password,
                "roles": roles,
            }
        )
        print(f"Created user: {username}")
    else:
        db.command(
            {
                "updateUser": username,
                "pwd": password,
                "roles": roles,
            }
        )
        print(f"Updated user: {username}")


def main():
    p = argparse.ArgumentParser(description="Create/Update MongoDB app users and roles")
    p.add_argument("--host", default=os.getenv("MONGO_HOST", "localhost"))
    p.add_argument("--port", type=int, default=int(os.getenv("MONGO_PORT", "27017")))
    p.add_argument("--root_user", default=os.getenv("MONGO_INITDB_ROOT_USERNAME"))
    p.add_argument("--root_pwd", default=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    p.add_argument("--db", default=os.getenv("MONGO_DB") or os.getenv("APP_DB_NAME", "FirstTry"))

    # dbOwner account (uses existing names from compose/.env)
    p.add_argument("--app_user", default=os.getenv("MONGO_APP_USERNAME", "appuser"))
    p.add_argument("--app_pwd", default=os.getenv("MONGO_APP_PASSWORD"))

    # read-only account
    p.add_argument("--ro_user", default=os.getenv("MONGO_READONLY_USERNAME", "readonly"))
    p.add_argument("--ro_pwd", default=os.getenv("MONGO_READONLY_PASSWORD"))


    args = p.parse_args()

    # Resolve required values
    root_user = args.root_user or _required_env("MONGO_INITDB_ROOT_USERNAME")
    root_pwd = args.root_pwd or _required_env("MONGO_INITDB_ROOT_PASSWORD")
    app_db = args.db
    app_user = args.app_user
    app_pwd = args.app_pwd or _required_env("MONGO_APP_PASSWORD")
    ro_user = args.ro_user
    ro_pwd = args.ro_pwd or _required_env("MONGO_READONLY_PASSWORD")

    admin_uri = f"mongodb://{root_user}:{root_pwd}@{args.host}:{args.port}/admin"
    client = MongoClient(admin_uri)
    db = client[app_db]

    # dbOwner on application DB (covers readWrite + admin on that DB)
    ensure_user(db, app_user, app_pwd, roles=[{"role": "dbOwner", "db": app_db}])

    # read-only on application DB
    ensure_user(db, ro_user, ro_pwd, roles=[{"role": "read", "db": app_db}])

    print("Done.")


if __name__ == "__main__":
    main()
