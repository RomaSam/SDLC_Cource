---
name: db_create
description: Create or recreate the Cinema SQLite database from schema.sql
allowed-tools: Bash(py *), Bash(python3 *), Bash(test *), Bash(ls *)
argument-hint: [--recreate] [--init]
---

Target: $ARGUMENTS

1. Locate `Cinema/db/schema.sql` relative to the project root.
2. Check whether `Cinema/db/cinema.db` already exists.
   - If `--recreate` was passed (or is present in $ARGUMENTS), delete `Cinema/db/cinema.db` before proceeding.
   - If no flag was passed and the database already exists, inform the user and stop — do not overwrite.
3. Run the following command to create the database:
   ```
   py -c "
   import sqlite3, pathlib
   db = pathlib.Path('Cinema/db/cinema.db')
   schema = pathlib.Path('Cinema/db/schema.sql').read_text()
   with sqlite3.connect(db) as conn:
       conn.executescript(schema)
   print('Database ready:', db.resolve())
   "
   ```
4. If `--init` was passed (or is present in $ARGUMENTS), seed the database with 10 rows of realistic test data by running:
   ```
   py -c "
   import sqlite3, pathlib, random, datetime

   MOVIES = [
       ('The Grand Illusion', 'Drama', 114),
       ('Interstellar', 'Sci-Fi', 169),
       ('Parasite', 'Thriller', 132),
       ('Spirited Away', 'Animation', 125),
       ('The Dark Knight', 'Action', 152),
       ('Amélie', 'Romance', 122),
       ('Inception', 'Sci-Fi', 148),
       ('Whiplash', 'Drama', 107),
       ('Mad Max: Fury Road', 'Action', 120),
       ('Coco', 'Animation', 105),
   ]
   HALLS = ['Hall A', 'Hall B', 'Hall C']
   TIMES = ['10:00', '12:30', '15:00', '17:30', '20:00', '22:30']

   date1 = datetime.date.today().isoformat()
   date2 = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
   rows = []
   for i, (name, genre, duration) in enumerate(MOVIES):
       date = date1 if i < 5 else date2
       begins_at = random.choice(TIMES)
       hall = random.choice(HALLS)
       seats = random.choice([80, 120, 150, 200])
       rows.append((name, genre, duration, date, begins_at, hall, seats))

   db = pathlib.Path('Cinema/db/cinema.db')
   with sqlite3.connect(db) as conn:
       conn.executemany(
           'INSERT INTO screening (name, genre, duration_minutes, screening_date, begins_at, hall, seats) VALUES (?,?,?,?,?,?,?)',
           rows,
       )
   print(f'Seeded {len(rows)} rows.')
   "
   ```
5. Confirm success by reporting the absolute path of the created `cinema.db` and, if seeded, the number of rows inserted.
