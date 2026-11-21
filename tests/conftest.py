import pytest
import sqlite3
from app.main import app
from app.database import get_db
import app.database as db_module

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_path = str(tmp_path / "test_eclearance.db")
    monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
    
    db_module.init_db()
    
    def override_get_db():
        conn = sqlite3.connect(test_db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
