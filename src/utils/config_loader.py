"""Explicit, portable configuration; database credentials come from the environment."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigLoader:
    def __init__(self, config_path: str | Path | None = None, *, root: Path | None = None):
        self.root = Path(root or PROJECT_ROOT).resolve()
        path = Path(config_path or "config/config.yaml")
        self.config_path = path if path.is_absolute() else self.root / path
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        with self.config_path.open(encoding="utf-8") as handle:
            self.config = yaml.safe_load(handle)
        if not isinstance(self.config, dict):
            raise ValueError("Configuration must be a YAML mapping")

    def get(self, key: str, default: Any = None) -> Any:
        value: Any = self.config
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    def path(self, key: str) -> Path:
        value = self.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Missing path setting: {key}")
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def database_parameters(self) -> dict[str, Any]:
        if os.getenv("DATABASE_URL"):
            return {"dsn": os.environ["DATABASE_URL"], "connect_timeout": 10}
        password = os.getenv("DB_PASSWORD")
        if not password:
            raise ValueError("Set DB_PASSWORD or DATABASE_URL before using --with-database")
        return {
            "host": os.getenv("DB_HOST", str(self.get("database.host", "127.0.0.1"))),
            "port": int(os.getenv("DB_PORT", str(self.get("database.port", 5432)))),
            "dbname": os.getenv("DB_NAME", str(self.get("database.name", "intermodal_analytics"))),
            "user": os.getenv("DB_USER", str(self.get("database.user", "data_engineer"))),
            "password": password,
            "connect_timeout": 10,
        }
