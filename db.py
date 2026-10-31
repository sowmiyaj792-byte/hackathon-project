import sqlite3
from pathlib import Path
DB_PATH=Path(__file__).resolve().parent/'subscriptions.db'
def connect():
    con=sqlite3.connect(DB_PATH)
    con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con
def initialize():
    with connect() as con:
        con.executescript((Path(__file__).parent/'schema.sql').read_text(encoding='utf-8'))
