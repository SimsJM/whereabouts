"""SQLite persistence foundation for Whereabouts.

Deliberately headless: nothing in this module imports FastAPI, so the data layer
is usable from plain pytest and, later, from the service package and the web app
alike.

- The schema lives in versioned migration files under ``migrations/`` at the
  repository root (``NNNN_description.sql``, applied in ascending order).
- The highest applied revision is recorded in the database itself as
  ``PRAGMA user_version`` — inspectable with plain SQL, with no bookkeeping
  table, so ``sqlite_master`` holds exactly the application tables.
- Every connection handed out by :class:`Database` has ``PRAGMA foreign_keys =
  ON``.
- The database location is always caller-supplied (path, ``sqlite:///`` URL, or
  in-memory); nothing is hard-coded, so tests point at temporary files.
"""

from __future__ import annotations

import os
import re
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

# src/whereabouts/db.py -> repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MIGRATIONS_DIR = REPO_ROOT / "migrations"

_MIGRATION_NAME = re.compile(r"^(?P<version>\d+)_[0-9A-Za-z_]*\.sql$")


class MigrationError(RuntimeError):
    """The migrations directory or a migration script is broken."""


def _find_migrations(migrations_dir: Path) -> list[tuple[int, Path]]:
    """Return the ``(version, path)`` pairs in ``migrations_dir``, ascending."""
    if not migrations_dir.is_dir():
        raise MigrationError(f"migrations directory not found: {migrations_dir}")
    migrations: list[tuple[int, Path]] = []
    for entry in migrations_dir.iterdir():
        match = _MIGRATION_NAME.match(entry.name)
        if match:
            migrations.append((int(match["version"]), entry))
    versions = [version for version, _ in migrations]
    if len(set(versions)) != len(versions):
        raise MigrationError(f"duplicate migration versions in {migrations_dir}")
    migrations.sort(key=lambda migration: migration[0])
    return migrations


def latest_revision(migrations_dir: Path = DEFAULT_MIGRATIONS_DIR) -> int:
    """The highest migration version on disk (0 when there are none)."""
    versions = [version for version, _ in _find_migrations(migrations_dir)]
    return versions[-1] if versions else 0


def _normalise_url(url: str | os.PathLike[str]) -> tuple[str, bool, bool]:
    """Turn the caller's path or URL into ``(target, is_uri, in_memory)``.

    In-memory databases get a unique shared-cache name so that all connections
    of one :class:`Database` see the same data while two instances never share.
    """
    raw = os.fspath(url)
    if raw in (":memory:", "sqlite://", "sqlite:///:memory:"):
        return f"file:whereabouts-mem-{uuid.uuid4().hex}?mode=memory&cache=shared", True, True
    if raw.startswith("file:"):
        return raw, True, False
    if raw.startswith("sqlite://"):
        return raw.removeprefix("sqlite://") or ":memory:", False, False
    return raw, False, False


class Database:
    """An SQLite database holding the Whereabouts schema.

    ``url`` is a filesystem path (``str`` or :class:`os.PathLike`), a
    ``sqlite:///`` URL, or ``:memory:`` / ``sqlite:///:memory:`` for an
    in-memory database. Use :meth:`migrate` to create or update the schema and
    :meth:`connect` for connections; :attr:`revision` reports the applied
    migration state.
    """

    def __init__(
        self,
        url: str | os.PathLike[str],
        *,
        migrations_dir: Path = DEFAULT_MIGRATIONS_DIR,
    ) -> None:
        self._target, self._is_uri, in_memory = _normalise_url(url)
        self._migrations_dir = migrations_dir
        self._anchor: sqlite3.Connection | None = None
        if in_memory:
            # Shared-cache in-memory databases live only while a connection is
            # open: this anchor keeps ours alive for the object's lifetime.
            self._anchor = self.connect()

    def connect(self) -> sqlite3.Connection:
        """Open a new connection, always with ``PRAGMA foreign_keys=ON``."""
        conn = sqlite3.connect(self._target, uri=self._is_uri)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def migrate(self) -> int:
        """Apply every pending migration in order; return the current revision."""
        migrations = _find_migrations(self._migrations_dir)
        with closing(self.connect()) as conn:
            applied: int = conn.execute("PRAGMA user_version").fetchone()[0]
            for version, path in migrations:
                if version <= applied:
                    continue
                script = (
                    "BEGIN IMMEDIATE;\n"
                    + path.read_text(encoding="utf-8")
                    + f"\nPRAGMA user_version = {version};\nCOMMIT;\n"
                )
                try:
                    conn.executescript(script)
                except sqlite3.Error as exc:
                    conn.rollback()
                    raise MigrationError(f"migration {path.name} failed: {exc}") from exc
                applied = version
        return applied

    @property
    def revision(self) -> int:
        """The highest applied migration (``PRAGMA user_version``); 0 means empty."""
        with closing(self.connect()) as conn:
            return conn.execute("PRAGMA user_version").fetchone()[0]  # type: ignore[no-any-return]

    def close(self) -> None:
        """Release resources (only in-memory databases hold any)."""
        if self._anchor is not None:
            self._anchor.close()
            self._anchor = None

    def __enter__(self) -> Database:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
