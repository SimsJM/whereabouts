-- Whereabouts — DRAFT schema v0.1 (31 Oct 2026)
-- Status: PROPOSED. The Architect confirms or replaces this in the first data-model issue.
-- migrations/ is a high-risk path: Jamie merges. SQLite 3.35+ (WAL, FTS5, recursive CTEs).

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE households (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE users (
  id            INTEGER PRIMARY KEY,
  display_name  TEXT NOT NULL,
  email         TEXT UNIQUE,
  created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
-- Credentials (passkeys / OIDC subject) are defined by ADR-0003.

CREATE TABLE memberships (
  household_id  INTEGER NOT NULL REFERENCES households(id),
  user_id       INTEGER NOT NULL REFERENCES users(id),
  role          TEXT NOT NULL CHECK (role IN ('admin','member','readonly')),
  PRIMARY KEY (household_id, user_id)
);

-- One location tree. 'location' is an internal word only.
CREATE TABLE locations (
  id            INTEGER PRIMARY KEY,
  household_id  INTEGER NOT NULL REFERENCES households(id),
  parent_id     INTEGER REFERENCES locations(id),
  kind          TEXT NOT NULL CHECK (kind IN ('home','room','place','box')),
  name          TEXT NOT NULL,
  label_code    TEXT,                       -- 'B-0042' / 'P-0003'; NULL for home and room
  move_state    TEXT CHECK (move_state IN ('packed','unpacked')),
  photo_ref     TEXT,
  archived_at   TEXT,
  created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  CHECK ((kind = 'home') = (parent_id IS NULL)),
  CHECK ((kind IN ('place','box')) = (label_code IS NOT NULL)),
  CHECK (move_state IS NULL OR kind = 'box')
);
-- Codes unique per household forever (archived rows keep theirs).
CREATE UNIQUE INDEX ux_locations_code ON locations(household_id, label_code) WHERE label_code IS NOT NULL;
CREATE INDEX ix_locations_parent ON locations(household_id, parent_id);
-- Ordering rule (parent rank lower than child, box-in-box allowed, no cycles) is enforced
-- in the domain/service layer; optionally also by triggers. [Architect]

CREATE TABLE code_counters (
  household_id  INTEGER NOT NULL REFERENCES households(id),
  prefix        TEXT NOT NULL CHECK (prefix IN ('B','P')),
  next_value    INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (household_id, prefix)
);

CREATE TABLE items (
  id            INTEGER PRIMARY KEY,
  household_id  INTEGER NOT NULL REFERENCES households(id),
  location_id   INTEGER NOT NULL REFERENCES locations(id),  -- room or deeper (service-enforced)
  name          TEXT NOT NULL,
  category      TEXT,
  quantity      INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),
  unit          TEXT,
  tags          TEXT,                       -- JSON array
  photo_ref     TEXT,
  notes         TEXT,
  archived_at   TEXT,
  created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX ix_items_location ON items(location_id);

-- Append-only event log. Never DELETE; only the 'undone' flag may change.
CREATE TABLE events (
  id              INTEGER PRIMARY KEY,
  household_id    INTEGER NOT NULL REFERENCES households(id),
  occurred_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  actor_type      TEXT NOT NULL CHECK (actor_type IN ('user','agent','system')),
  actor_id        INTEGER,
  actor_name      TEXT NOT NULL,
  verb            TEXT NOT NULL,            -- e.g. 'item.moved'
  subject_type    TEXT NOT NULL,            -- 'item' | 'location' | 'label' | 'move' | 'import'
  subject_id      INTEGER,
  summary         TEXT NOT NULL,            -- human line: 'Moved to Toolbox'
  before_json     TEXT,
  after_json      TEXT,
  batch_id        TEXT,
  undoes_event_id INTEGER REFERENCES events(id),
  undone          INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX ix_events_household_time ON events(household_id, occurred_at DESC);
CREATE INDEX ix_events_subject ON events(subject_type, subject_id);
CREATE TRIGGER events_no_delete BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;

CREATE TABLE pins (
  user_id     INTEGER NOT NULL REFERENCES users(id),
  item_id     INTEGER NOT NULL REFERENCES items(id),
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  PRIMARY KEY (user_id, item_id)
);

CREATE TABLE item_views (
  user_id     INTEGER NOT NULL REFERENCES users(id),
  item_id     INTEGER NOT NULL REFERENCES items(id),
  viewed_at   TEXT NOT NULL,
  PRIMARY KEY (user_id, item_id)
);

CREATE TABLE user_state (
  user_id          INTEGER PRIMARY KEY REFERENCES users(id),
  changes_seen_at  TEXT
);

CREATE TABLE loans (
  id           INTEGER PRIMARY KEY,
  item_id      INTEGER NOT NULL REFERENCES items(id),
  lent_to      TEXT NOT NULL,
  lent_since   TEXT NOT NULL,
  due_on       TEXT,
  returned_at  TEXT
);
CREATE UNIQUE INDEX ux_loans_open ON loans(item_id) WHERE returned_at IS NULL;

CREATE TABLE moves (
  id            INTEGER PRIMARY KEY,
  household_id  INTEGER NOT NULL REFERENCES households(id),
  from_home_id  INTEGER NOT NULL REFERENCES locations(id),
  to_home_id    INTEGER NOT NULL REFERENCES locations(id),
  moving_day    TEXT,                       -- NULL = 'Not decided yet'
  started_at    TEXT NOT NULL,
  finished_at   TEXT
);
CREATE UNIQUE INDEX ux_moves_open ON moves(household_id) WHERE finished_at IS NULL;

CREATE TABLE label_queue (
  household_id  INTEGER NOT NULL REFERENCES households(id),
  location_id   INTEGER NOT NULL REFERENCES locations(id),
  added_at      TEXT NOT NULL,
  PRIMARY KEY (household_id, location_id)
);

CREATE TABLE label_settings (
  household_id  INTEGER PRIMARY KEY REFERENCES households(id),
  offset_x_mm   REAL NOT NULL DEFAULT 0,
  offset_y_mm   REAL NOT NULL DEFAULT 0
);

-- v1.1 (MCP). Reserved now so the schema needs no rework.
CREATE TABLE api_tokens (
  id            INTEGER PRIMARY KEY,
  household_id  INTEGER NOT NULL REFERENCES households(id),
  user_id       INTEGER NOT NULL REFERENCES users(id),
  name          TEXT NOT NULL,              -- 'Claude', 'Home Assistant'
  scope         TEXT NOT NULL CHECK (scope IN ('read','read_write')),
  token_hash    TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  last_used_at  TEXT,
  revoked_at    TEXT
);

-- Search (FTS5). Keep in sync with triggers or service code. [Architect]
CREATE VIRTUAL TABLE search_index USING fts5(
  kind, ref_id UNINDEXED, household_id UNINDEXED, home_id UNINDEXED,
  name, category, code, tokenize = 'porter unicode61'
);
