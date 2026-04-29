import sqlite3


def get_connection() -> sqlite3.Connection:
    # Deferred import: avoids a circular dependency at module load time.
    from config import settings
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn
