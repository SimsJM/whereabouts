# Migrations

Versioned SQLite schema migrations for Whereabouts (CB-61), applied by
`whereabouts.db` (`src/whereabouts/db.py`).

Conventions:

- Files are named `NNNN_description.sql` with a strictly increasing, zero-padded
  integer version. The runner applies them in ascending version order.
- Each file is applied inside its own transaction; the runner supplies the
  transaction and stamps the applied version into `PRAGMA user_version`. Files
  therefore contain DDL statements only — no `BEGIN`/`COMMIT`.
- The applied-revision state is the database's `PRAGMA user_version`, so
  `sqlite_master` holds only the application's own tables.
- Never edit a migration that has shipped. Add a new file with the next version.

Running `Database(path).migrate()` against an empty database creates exactly the
six tables of the approved data model: `users`, `homes`, `locations`, `items`,
`code_counters`, `events`.
