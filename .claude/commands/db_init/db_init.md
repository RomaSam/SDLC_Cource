---
name: db_init
description: Create or recreate the Cinema SQLite database from schema.sql
allowed-tools: Bash(py *), Bash(python3 *), Bash(test *), Bash(ls *)
argument-hint: [--recreate]
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
   schema = pathlib.Path('Cinema/db/cinema.db').read_text()
   with sqlite3.connect(db) as conn:
       conn.executescript(schema)
   print('Database ready:', db.resolve())
   "
   ```
4. Confirm success by reporting the absolute path of the created `cinema.db`.
