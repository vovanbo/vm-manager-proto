CREATE TABLE IF NOT EXISTS "users" (
  "id"    TEXT NOT NULL PRIMARY KEY,
  "email" TEXT NOT NULL,
  CONSTRAINT "unique_id" UNIQUE ("id"),
  CONSTRAINT "unique_email" UNIQUE ("email")
);

CREATE TABLE IF NOT EXISTS "accounts" (
  "id"             INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "user_id"        TEXT    NOT NULL,
  "provider"       TEXT    NOT NULL,
  "sub"            TEXT    NOT NULL,
  "email"          TEXT    NOT NULL,
  "email_verified" BOOLEAN NOT NULL,
  "name"           TEXT,
  "given_name"     TEXT,
  "family_name"    TEXT,
  "profile"        TEXT,
  "picture"        TEXT,
  "gender"         TEXT,
  CONSTRAINT "lnk_accounts_users" FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  CONSTRAINT "provider_sub_email" UNIQUE ("provider", "sub", "email")
);

CREATE INDEX IF NOT EXISTS "index_email1" ON "accounts" ("email");
CREATE INDEX IF NOT EXISTS "index_provider" ON "accounts" ("provider");
CREATE INDEX IF NOT EXISTS "index_sub" ON "accounts" ("sub");
CREATE INDEX IF NOT EXISTS "index_user_id" ON "accounts" ("user_id");

CREATE TABLE IF NOT EXISTS "tokens" (
  "id"         TEXT     NOT NULL PRIMARY KEY,
  "user_id"    TEXT     NOT NULL,
  "issued"     TIMESTAMP NOT NULL,
  "expired"    TIMESTAMP NOT NULL,
  CONSTRAINT "lnk_tokens_users" FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  CONSTRAINT "unique_id" UNIQUE ("id")
);

CREATE INDEX IF NOT EXISTS "index_expired" ON "tokens" ("expired");
CREATE INDEX IF NOT EXISTS "index_user_id1" ON "tokens" ("user_id");

CREATE TABLE IF NOT EXISTS "tasks" (
  "id"       TEXT NOT NULL PRIMARY KEY,
  "user_id"  TEXT NOT NULL,
  "command"  TEXT,
  "params"   TEXT,
  "result"   TEXT,
  "status"   INTEGER NOT NULL,
  "created"  TIMESTAMP NOT NULL,
  "started"  TIMESTAMP,
  "finished" TIMESTAMP,
  CONSTRAINT "lnk_tasks_users" FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  CONSTRAINT "unique_id" UNIQUE ("id")
);

CREATE INDEX IF NOT EXISTS "index_status" ON "tasks" ("status");
CREATE INDEX IF NOT EXISTS "index_user_id2" ON "tasks" ("user_id");
