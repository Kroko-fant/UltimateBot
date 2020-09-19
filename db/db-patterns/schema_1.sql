CREATE TABLE config
(
    name  TEXT,
    value TEXT
);
CREATE TABLE leveldata
(
    userId INT NOT NULL UNIQUE,
    level  INT NOT NULL,
    xp     INT NOT NULL
);
CREATE TABLE reactionroles
(
    message TEXT,
    emoji   TEXT,
    role    TEXT
);

PRAGMA user_version = 1;
