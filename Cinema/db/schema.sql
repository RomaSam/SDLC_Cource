CREATE TABLE screening (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    genre            TEXT,
    duration_minutes INTEGER NOT NULL,
    screening_date   TEXT    NOT NULL,  -- ISO 8601: 'YYYY-MM-DD'
    begins_at        TEXT    NOT NULL,  -- 'HH:MM'
    hall             TEXT    NOT NULL,
    seats            INTEGER NOT NULL
);
