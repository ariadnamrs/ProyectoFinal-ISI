import sqlite3
DATABASE_NAME = "sql/restaurante.db"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

