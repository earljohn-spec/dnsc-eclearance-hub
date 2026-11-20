import os
import sqlite3
from pathlib import Path
from typing import Generator
from app.security import hash_password

DB_PATH = os.getenv("DATABASE_PATH", "data/clearance.db")

def get_db_path() -> Path:
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode = WAL;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clearance_holds (
        hold_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        source_system TEXT NOT NULL,
        hold_type TEXT NOT NULL,
        description TEXT NOT NULL,
        amount_due REAL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cleared_at TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_affairs_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        violation_type TEXT NOT NULL,
        sanction TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_system TEXT NOT NULL,
        records_processed INTEGER NOT NULL,
        records_successful INTEGER NOT NULL,
        records_failed INTEGER NOT NULL,
        errors_json TEXT NOT NULL,
        imported_by TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("SELECT user_id FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        admin_pw = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "AdminSecurePass2026!")
        admin_password_hash = hash_password(admin_pw)
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", admin_password_hash, "admin", "System Administrator", "admin@dnsc.edu.ph"),
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
