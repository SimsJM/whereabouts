"""Tests for the headless data layer (CB-61.1, CB-61.2).

These exercise :mod:`whereabouts.db` directly from plain pytest — no FastAPI,
no web server — always against temporary or in-memory SQLite databases.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import closing

import pytest

from whereabouts.db import Database, MigrationError, latest_revision

EXPECTED_TABLES = ["code_counters", "events", "homes", "items", "locations", "users"]


@pytest.fixture
def db(tmp_path) -> Iterator[Database]:
    with Database(tmp_path / "test.sqlite3") as database:
        yield database


def table_names(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
    return [row["name"] for row in rows]


def assert_rejected(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql, params)
    conn.rollback()


# --- CB-61.1: schema comes from versioned migrations --------------------------


def test_migrate_creates_exactly_the_spec_tables(db: Database) -> None:
    db.migrate()
    with closing(db.connect()) as conn:
        assert table_names(conn) == EXPECTED_TABLES
        # No extra tables and no hand-made indexes: the only extra sqlite_master
        # entry is the auto-index SQLite creates for the code_counters PK.
        indexes = conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
        assert [row["name"] for row in indexes] == ["sqlite_autoindex_code_counters_1"]


def test_spec_columns_and_constraints(db: Database) -> None:
    db.migrate()
    with closing(db.connect()) as conn:
        columns = {
            table: [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
            for table in EXPECTED_TABLES
        }
    assert columns["users"] == ["id", "display_name", "created_at", "archived_at"]
    assert columns["homes"] == ["id", "owner_user_id", "name", "created_at", "archived_at"]
    assert columns["locations"] == [
        "id", "home_id", "parent_id", "kind", "code", "name", "created_at", "archived_at",
    ]
    assert columns["items"] == [
        "id", "location_id", "name", "quantity", "category", "notes",
        "created_at", "archived_at",
    ]
    assert columns["code_counters"] == ["owner_user_id", "prefix", "last_value"]
    assert columns["events"] == ["id", "actor", "entity_type", "entity_id", "action",
                                 "detail", "created_at"]
    # The users table holds identity/display data only (O-02): no credentials.
    assert not {"password", "passkey", "oidc", "credentials"} & set(columns["users"])


def test_revision_marker_is_inspectable_and_matches_latest(db: Database) -> None:
    assert latest_revision() >= 1
    assert db.revision == 0
    assert db.migrate() == latest_revision()
    assert db.revision == latest_revision()
    with closing(db.connect()) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == latest_revision()


def test_migrate_is_idempotent(db: Database) -> None:
    assert db.migrate() == latest_revision()
    assert db.migrate() == latest_revision()
    with closing(db.connect()) as conn:
        assert table_names(conn) == EXPECTED_TABLES


def test_failed_migration_rolls_back(tmp_path) -> None:
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "0001_fine.sql").write_text(
        "CREATE TABLE fine (id INTEGER PRIMARY KEY);", encoding="utf-8"
    )
    (migrations / "0002_broken.sql").write_text(
        "CREATE TABLE fine (id INTEGER PRIMARY KEY);", encoding="utf-8"
    )
    with Database(tmp_path / "db.sqlite3", migrations_dir=migrations) as database:
        with pytest.raises(MigrationError, match="0002_broken"):
            database.migrate()
        assert database.revision == 1
        with closing(database.connect()) as conn:
            assert table_names(conn) == ["fine"]


def test_foreign_keys_are_enforced(db: Database) -> None:
    db.migrate()
    with closing(db.connect()) as conn:
        assert_rejected(conn, "INSERT INTO homes (owner_user_id, name) VALUES (999, 'H')")

    # A real chain: user -> home -> room -> item -> counter is accepted.
    with closing(db.connect()) as conn:
        conn.execute("INSERT INTO users (id, display_name) VALUES (1, 'Jamie')")
        conn.execute("INSERT INTO homes (id, owner_user_id, name) VALUES (10, 1, 'Home A')")
        conn.execute(
            "INSERT INTO locations (id, home_id, kind, name) VALUES (20, 10, 'room', 'Kitchen')"
        )
        conn.execute(
            "INSERT INTO items (id, location_id, name) VALUES (30, 20, 'Tin opener')"
        )
        conn.execute(
            "INSERT INTO code_counters (owner_user_id, prefix, last_value) VALUES (1, 'B', 7)"
        )
        conn.commit()

        assert_rejected(conn, "INSERT INTO homes (owner_user_id, name) VALUES (999, 'H2')")
        assert_rejected(
            conn, "INSERT INTO locations (home_id, kind, name) VALUES (999, 'room', 'R')"
        )
        assert_rejected(
            conn,
            "INSERT INTO locations (home_id, parent_id, kind, name) VALUES (10, 999, 'box', 'B')",
        )
        assert_rejected(conn, "INSERT INTO items (location_id, name) VALUES (999, 'X')")
        assert_rejected(
            conn,
            "INSERT INTO code_counters (owner_user_id, prefix, last_value) "
            "VALUES (999, 'P', 1)",
        )


def test_check_constraints_are_enforced(db: Database) -> None:
    db.migrate()
    with closing(db.connect()) as conn:
        conn.execute("INSERT INTO users (id, display_name) VALUES (1, 'Jamie')")
        conn.execute("INSERT INTO homes (id, owner_user_id, name) VALUES (10, 1, 'Home A')")
        conn.commit()

        # kind must be room / place / box.
        assert_rejected(
            conn, "INSERT INTO locations (home_id, kind, name) VALUES (10, 'shelf', 'S')"
        )
        # prefix must be B or P.
        assert_rejected(
            conn,
            "INSERT INTO code_counters (owner_user_id, prefix, last_value) "
            "VALUES (1, 'X', 1)",
        )
        # quantity must be >= 0 ...
        conn.execute(
            "INSERT INTO locations (id, home_id, kind, name) VALUES (20, 10, 'room', 'Kitchen')"
        )
        conn.commit()  # accepted inserts commit before assert_rejected rolls back
        assert_rejected(
            conn, "INSERT INTO items (location_id, name, quantity) VALUES (20, 'X', -1)"
        )
        # ... but 0 is fine (D-14).
        conn.execute("INSERT INTO items (location_id, name, quantity) VALUES (20, 'X', 0)")
        conn.commit()


# --- CB-61.2: the data layer runs headless and test-local ---------------------


def test_every_connection_has_foreign_keys_on(db: Database) -> None:
    db.migrate()
    for _ in range(3):
        with closing(db.connect()) as conn:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


@pytest.mark.parametrize(
    "make_url",
    [
        lambda p: p,  # pathlib.Path
        str,  # plain string path
        lambda p: f"sqlite:///{p}",  # sqlite URL
    ],
    ids=["path", "str", "sqlite-url"],
)
def test_database_location_is_configurable(tmp_path, make_url) -> None:
    with Database(make_url(tmp_path / "configured.sqlite3")) as database:
        assert database.migrate() == latest_revision()
        with closing(database.connect()) as conn:
            assert table_names(conn) == EXPECTED_TABLES


@pytest.mark.parametrize("url", [":memory:", "sqlite:///:memory:"])
def test_in_memory_database_is_shared_across_connections(url: str) -> None:
    with Database(url) as database:
        database.migrate()
        with closing(database.connect()) as conn:
            conn.execute("INSERT INTO users (display_name) VALUES ('Jamie')")
            conn.commit()
        with closing(database.connect()) as conn:
            assert table_names(conn) == EXPECTED_TABLES
            assert conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"] == 1


def test_in_memory_databases_do_not_leak_between_instances() -> None:
    with Database(":memory:") as first, Database(":memory:") as second:
        first.migrate()
        assert first.revision == latest_revision()
        assert second.revision == 0
