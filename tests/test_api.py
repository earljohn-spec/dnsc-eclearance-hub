import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoints():
    r1 = client.get("/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "healthy"

    r2 = client.get("/api/v1/health")
    assert r2.status_code == 200
    assert r2.json()["service"] == "dnsc-eclearance-hub"

def test_login_and_cross_department_clearance_denial():
    # Login as Library Staff
    lib_res = client.post("/api/v1/auth/login", json={"username": "library_staff", "password": "staff123"})
    assert lib_res.status_code == 200
    lib_token = lib_res.json()["access_token"]

    # Login as Cashier Staff
    cash_res = client.post("/api/v1/auth/login", json={"username": "cashier_staff", "password": "staff123"})
    assert cash_res.status_code == 200
    cash_token = cash_res.json()["access_token"]

    # Cashier creates a financial hold
    hold_payload = {
        "student_id": "TEST-2026-0001",
        "source_system": "cashier",
        "hold_type": "financial",
        "description": "Unpaid Tuition Fee",
        "amount_due": 1500.00
    }
    create_res = client.post(
        "/api/v1/holds",
        json=hold_payload,
        headers={"Authorization": f"Bearer {cash_token}"}
    )
    assert create_res.status_code == 201
    hold_id = create_res.json()["hold_id"]

    # Negative Test: Library Staff attempts to clear Cashier hold -> 403 Forbidden
    clear_denied = client.put(
        f"/api/v1/holds/{hold_id}/clear",
        headers={"Authorization": f"Bearer {lib_token}"}
    )
    assert clear_denied.status_code == 403
    assert "cannot alter holds" in clear_denied.json()["detail"].lower()

    # Positive Test: Cashier Staff clears their own department hold -> 200 OK
    clear_allowed = client.put(
        f"/api/v1/holds/{hold_id}/clear",
        headers={"Authorization": f"Bearer {cash_token}"}
    )
    assert clear_allowed.status_code == 200
    assert clear_allowed.json()["status"] == "cleared"
