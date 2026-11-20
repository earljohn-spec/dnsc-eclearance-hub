import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Path as ApiPath, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import init_db, get_db
from app.models.schemas import (
    LoginRequest,
    LoginResponse,
    ClearanceStatusResponse,
    HoldSummary,
    HoldingResponse,
    HoldingUpdateRequest,
    HealthResponse,
    UserRole,
    SourceSystem,
    HoldStatus
)
from app.security import (
    verify_password,
    create_access_token,
    get_current_user,
    RoleChecker
)
from app.services.import_pipeline import process_import_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="DNSC e-Clearance Hub API",
    version="1.0.0",
    description="Centralized clearance processing and hold tracking system for Davao del Norte State College",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/static/index.html")


def _health_payload() -> HealthResponse:
    return HealthResponse(status="healthy", service="dnsc-eclearance-hub", version="1.0.0")

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return _health_payload()

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
def health_check_v1():
    return _health_payload()


@app.post("/api/v1/auth/login", response_model=LoginResponse, tags=["Authentication"])
def login(payload: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT user_id, username, password_hash, role, full_name FROM users WHERE username = ?", (payload.username,))
    user = cursor.fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=user["username"],
        role=user["role"],
        full_name=user["full_name"]
    )


@app.get("/api/v1/clearance/status/{student_id}", response_model=ClearanceStatusResponse, tags=["Clearance"])
def get_clearance_status(
    student_id: str = ApiPath(..., description="Student Identification Number"),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT hold_id, source_system, hold_type, description, amount_due, status, created_at
        FROM clearance_holds
        WHERE student_id = ? AND status = 'active'
        """,
        (student_id,)
    )
    rows = cursor.fetchall()

    holds = [
        HoldSummary(
            hold_id=row["hold_id"],
            source_system=row["source_system"],
            hold_type=row["hold_type"],
            description=row["description"],
            amount_due=row["amount_due"],
            status=row["status"],
            created_at=str(row["created_at"])
        )
        for row in rows
    ]

    is_cleared = len(holds) == 0
    message = "Student is cleared across all institutional departments." if is_cleared else f"Student has {len(holds)} active clearance hold(s)."

    return ClearanceStatusResponse(
        student_id=student_id,
        cleared=is_cleared,
        active_holds_count=len(holds),
        holds=holds,
        message=message
    )


@app.get("/api/v1/holds", response_model=List[HoldSummary], tags=["Holds"])
def list_holds(
    student_id: Optional[str] = Query(None, description="Optional Student ID filter"),
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    if student_id:
        cursor.execute("SELECT hold_id, source_system, hold_type, description, amount_due, status, created_at FROM clearance_holds WHERE student_id = ? ORDER BY created_at DESC", (student_id,))
    else:
        cursor.execute("SELECT hold_id, source_system, hold_type, description, amount_due, status, created_at FROM clearance_holds ORDER BY created_at DESC LIMIT 100")
        
    rows = cursor.fetchall()

    return [
        HoldSummary(
            hold_id=row["hold_id"],
            source_system=row["source_system"],
            hold_type=row["hold_type"],
            description=row["description"],
            amount_due=row["amount_due"],
            status=row["status"],
            created_at=str(row["created_at"])
        )
        for row in rows
    ]


STAFF_ROLES = [
    UserRole.ADMIN,
    UserRole.ACCOUNTING_STAFF,
    UserRole.REGISTRAR_STAFF,
    UserRole.LIBRARY_STAFF,
    UserRole.STUDENT_AFFAIRS_STAFF
]


@app.post("/api/v1/holds", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED, tags=["Holds"])
def create_hold(
    payload: HoldingUpdateRequest,
    current_user: dict = Depends(RoleChecker(STAFF_ROLES)),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO clearance_holds (student_id, source_system, hold_type, description, amount_due, status)
        VALUES (?, ?, ?, ?, ?, 'active')
        """,
        (payload.student_id, payload.source_system.value, payload.hold_type.value, payload.description, payload.amount_due)
    )
    db.commit()
    hold_id = cursor.lastrowid
    
    cursor.execute("SELECT hold_id, student_id, source_system, hold_type, description, amount_due, status, created_at FROM clearance_holds WHERE hold_id = ?", (hold_id,))
    row = cursor.fetchone()

    return HoldingResponse(
        hold_id=row["hold_id"],
        student_id=row["student_id"],
        source_system=row["source_system"],
        hold_type=row["hold_type"],
        description=row["description"],
        amount_due=row["amount_due"],
        status=row["status"],
        created_at=str(row["created_at"])
    )


@app.put("/api/v1/holds/{hold_id}/clear", response_model=HoldingResponse, tags=["Holds"])
def clear_hold(
    hold_id: int = ApiPath(..., description="Hold record identifier"),
    current_user: dict = Depends(RoleChecker(STAFF_ROLES)),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT hold_id, student_id, source_system, hold_type, description, amount_due, status, created_at FROM clearance_holds WHERE hold_id = ?", (hold_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hold ID {hold_id} not found")

    cursor.execute(
        """
        UPDATE clearance_holds
        SET status = 'cleared', cleared_at = CURRENT_TIMESTAMP
        WHERE hold_id = ?
        """,
        (hold_id,)
    )
    db.commit()

    cursor.execute("SELECT hold_id, student_id, source_system, hold_type, description, amount_due, status, created_at FROM clearance_holds WHERE hold_id = ?", (hold_id,))
    updated_row = cursor.fetchone()

    return HoldingResponse(
        hold_id=updated_row["hold_id"],
        student_id=updated_row["student_id"],
        source_system=updated_row["source_system"],
        hold_type=updated_row["hold_type"],
        description=updated_row["description"],
        amount_due=updated_row["amount_due"],
        status=updated_row["status"],
        created_at=str(updated_row["created_at"])
    )


MAX_FILE_SIZE = 10 * 1024 * 1024

@app.post("/api/v1/import/{source_system}", tags=["Data Import"])
async def import_data_feed(
    source_system: SourceSystem,
    file: UploadFile = File(...),
    current_user: dict = Depends(RoleChecker(STAFF_ROLES))
):
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded file exceeds 10MB limit")

    try:
        result = process_import_file(
            source_system=source_system.value,
            file_bytes=file_bytes,
            filename=file.filename or "import.csv",
            imported_by=current_user.get("sub", "system")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
