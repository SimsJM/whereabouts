-- 0001_initial_schema.sql
-- CB-61 data model: the complete Whereabouts core schema.
-- Applied inside one transaction by whereabouts.db; the runner appends the
-- PRAGMA user_version stamp, so this file contains DDL only. Tables are created
-- in dependency order.

-- Who uses the app. Identity/display only: no credential columns (O-02).
CREATE TABLE users (
    id          INTEGER PRIMARY KEY,
    display_name TEXT   NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    archived_at TEXT    -- NULL means not archived (D-14: no hard deletes)
);

-- One home, one owner; a user can own many homes. The owner is the household
-- stand-in until D-20 membership arrives.
CREATE TABLE homes (
    id            INTEGER PRIMARY KEY,
    owner_user_id INTEGER NOT NULL REFERENCES users (id),
    name          TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    archived_at   TEXT
);

-- Adjacency-list tree under a home (D-11): parent_id NULL means directly under
-- the home. Hierarchy rules and codes (D-13) are enforced by the service layer;
-- the database enforces kind and the tree's wiring.
CREATE TABLE locations (
    id          INTEGER PRIMARY KEY,
    home_id     INTEGER NOT NULL REFERENCES homes (id),
    parent_id   INTEGER REFERENCES locations (id),
    kind        TEXT    NOT NULL CHECK (kind IN ('room', 'place', 'box')),
    code        TEXT,   -- B-NNNN / P-NNNN for boxes and places; NULL for rooms (D-13)
    name        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    archived_at TEXT
);

-- One item row = one location (O-03 default). Quantity may be 0 (D-14), never
-- negative.
CREATE TABLE items (
    id          INTEGER PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations (id),
    name        TEXT    NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),
    category    TEXT,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    archived_at TEXT
);

-- Per-owner sequential code counters (D-13): one row per owner per prefix,
-- incremented atomically with the location insert. Codes are never reused, so
-- last_value only ever moves forward.
CREATE TABLE code_counters (
    owner_user_id INTEGER NOT NULL REFERENCES users (id),
    prefix        TEXT    NOT NULL CHECK (prefix IN ('B', 'P')),
    last_value    INTEGER NOT NULL,
    PRIMARY KEY (owner_user_id, prefix)
);

-- Append-only event log (D-15). entity_id is a soft reference into whichever
-- table entity_type names, so it carries no FOREIGN KEY clause.
CREATE TABLE events (
    id          INTEGER PRIMARY KEY,
    actor       TEXT    NOT NULL,   -- a user id, or 'agent:<name>' / 'system'
    entity_type TEXT    NOT NULL,
    entity_id   INTEGER NOT NULL,
    action      TEXT    NOT NULL,
    detail      TEXT,               -- JSON describing what changed
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
