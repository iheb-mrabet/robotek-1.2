CREATE TABLE platform_state (
    component VARCHAR(80) PRIMARY KEY,
    status VARCHAR(24) NOT NULL,
    release VARCHAR(80) NOT NULL,
    last_checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
