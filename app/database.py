import sqlite3
from app.models.schemas import UserRole

DB_PATH = "eclearance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = FULL;")
    return conn

def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
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
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cleared_at TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_system TEXT NOT NULL,
        records_imported INTEGER NOT NULL,
        imported_by TEXT NOT NULL,
        filename TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_system TEXT NOT NULL,
        imported_by TEXT NOT NULL,
        filename TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER NOT NULL,
        old_values_json TEXT,
        new_values_json TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (actor_user_id) REFERENCES users (user_id)
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        from app.security import get_password_hash
        default_users = [
            ('admin', get_password_hash('admin123'), UserRole.ADMIN.value, 'System Administrator'),
            ('cashier_staff', get_password_hash('staff123'), UserRole.ACCOUNTING_STAFF.value, 'Accounting Staff'),
            ('registrar_staff', get_password_hash('staff123'), UserRole.REGISTRAR_STAFF.value, 'Registrar Staff'),
            ('library_staff', get_password_hash('staff123'), UserRole.LIBRARY_STAFF.value, 'Library Staff'),
            ('sa_staff', get_password_hash('staff123'), UserRole.STUDENT_AFFAIRS_STAFF.value, 'Student Affairs Staff')
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            default_users
        )

    conn.commit()
    conn.close()
