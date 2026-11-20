"""
Pydantic v2 Schemas and Enums for DNSC e-Clearance Hub
Requirements covered: R5-R8, R11-R13
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserRole(str, Enum):
    STUDENT = "student"
    LIBRARY_STAFF = "library_staff"
    ACCOUNTING_STAFF = "accounting_staff"
    REGISTRAR_STAFF = "registrar_staff"
    STUDENT_AFFAIRS_STAFF = "student_affairs_staff"
    ADMIN = "admin"


class HoldStatus(str, Enum):
    CLEARED = "cleared"
    UNCLEARED = "uncleared"


class SourceSystem(str, Enum):
    LIBRARY = "library"
    ACCOUNTING = "accounting"
    REGISTRAR = "registrar"
    STUDENT_AFFAIRS = "student_affairs"


class HoldType(str, Enum):
    OVERDUE_BOOKS = "overdue_books"
    UNPAID_FEES = "unpaid_fees"
    MISSING_DOCUMENT = "missing_document"
    DISCIPLINARY_ACTION = "disciplinary_action"


class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


class LoginRequest(BaseModel):
    user_id: str = Field(..., description="Student ID (dddd-ddddd) or Staff username")
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    expires_in: int = Field(default=3600, description="Token validity in seconds (1 hour)")


class HoldSummary(BaseModel):
    source_system: SourceSystem
    status: HoldStatus
    count: int = Field(ge=0)
    total_amount: float = Field(default=0.0, ge=0.0)
    remarks: Optional[str] = None


class ClearanceStatusResponse(BaseModel):
    student_id: str = Field(..., description="Masked format (YYYY-****-NN) for student views")
    full_name: str
    program: str
    overall_status: HoldStatus
    holds: List[HoldSummary]
    computed_at: datetime


class DeadlineResponse(BaseModel):
    clearance_deadline: str = Field(..., description="ISO 8601 date YYYY-MM-DD")
    days_remaining: int
    is_holiday: bool
    holiday_name: Optional[str] = None
    status: str


class SlipResponse(BaseModel):
    verification_token: str
    qr_code_data: str
    issue_date: datetime
    valid_until: datetime


class VerifyResponse(BaseModel):
    valid: bool
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    program: Optional[str] = None
    overall_status: Optional[HoldStatus] = None
    verified_at: datetime


class HoldingUpdateRequest(BaseModel):
    status: HoldStatus
    remarks: Optional[str] = None


class HoldingResponse(BaseModel):
    id: int
    student_id: str
    source_system: SourceSystem
    hold_type: HoldType
    amount_due: float = Field(default=0.0, ge=0.0)
    status: HoldStatus
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentAffairsRecordRequest(BaseModel):
    student_id: str = Field(..., pattern=r"^\d{4}-\d{5}$")
    hold_type: HoldType
    description: str = Field(..., min_length=3, max_length=255)
    amount_due: float = Field(default=0.0, ge=0.0)


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    service: str = Field(default="dnsc-eclearance-hub")
    timestamp: datetime
    database_status: str = Field(default="connected")
