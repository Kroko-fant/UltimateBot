CREATE TABLE leveldata(
    userId INT NOT NULL UNIQUE,
    level INT NOT NULL,
    xp INT NOT NULL
);

PRAGMA user_version = 3;
