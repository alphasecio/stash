CREATE TABLE IF NOT EXISTS stash (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_created_at
ON stash(created_at);
