import pytest


def test_database_password_has_no_source_default(config, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="DB_PASSWORD"):
        config.database_parameters()


def test_database_port_comes_from_environment(config, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_PASSWORD", "test-only-password")
    monkeypatch.setenv("DB_PORT", "5544")
    assert config.database_parameters()["port"] == 5544
