from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    ACCOUNTING_STAFF = "accounting_staff"
    REGISTRAR_STAFF = "registrar_staff"
    LIBRARY_STAFF = "library_staff"
    STUDENT_AFFAIRS_STAFF = "student_affairs_staff"
    STUDENT = "student"

    @property
    def allowed_source_system(self) -> Optional["SourceSystem"]:
        return ROLE_TO_SOURCE_SYSTEM.get(self)


class SourceSystem(str, Enum):
    LIBRARY = "library"
    REGISTRAR = "registrar"
    CASHIER = "cashier"
    STUDENT_AFFAIRS = "student_affairs"


class HoldType(str, Enum):
    ACADEMIC = "academic"
    FINANCIAL = "financial"
    DISCIPLINARY = "disciplinary"
    ADMINISTRATIVE = "administrative"


class HoldStatus(str, Enum):
    ACTIVE = "active"
    CLEARED = "cleared"


class ReportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


ROLE_TO_SOURCE_SYSTEM: Dict[UserRole, SourceSystem] = {
    UserRole.LIBRARY_STAFF: SourceSystem.LIBRARY,
    UserRole.ACCOUNTING_STAFF: SourceSystem.CASHIER,
    UserRole.REGISTRAR_STAFF: SourceSystem.REGISTRAR,
    UserRole.STUDENT_AFFAIRS_STAFF: SourceSystem.STUDENT_AFFAIRS,
}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
    user_id: Optional[int] = None


class UserBase(BaseModel):
    username: str
    role: UserRole
    full_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int
    created_at: str


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="System username")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: UserRole
    full_name: str


class HoldSummary(BaseModel):
    hold_id: int
    source_system: SourceSystem
    hold_type: HoldType
    description: str
    amount_due: float
    status: HoldStatus
    created_at: str


class ClearanceStatusResponse(BaseModel):
    student_id: str
    cleared: bool
    active_holds_count: int
    holds: List[HoldSummary]
    message: str


class HoldingResponse(BaseModel):
    hold_id: int
    student_id: str
    source_system: SourceSystem
    hold_type: HoldType
    description: str
    amount_due: float
    status: HoldStatus
    created_at: str


class HoldingUpdateRequest(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=50)
    source_system: SourceSystem
    hold_type: HoldType
    description: str = Field(..., min_length=3, max_length=255)
    amount_due: float = Field(default=0.0, ge=0.0)


class ClearanceHoldBase(BaseModel):
    student_id: str
    source_system: SourceSystem
    hold_type: HoldType
    description: str
    amount_due: float = 0.0


class ClearanceHoldCreate(ClearanceHoldBase):
    pass


class ClearanceHoldUpdate(BaseModel):
    status: Optional[HoldStatus] = None
    description: Optional[str] = None
    amount_due: Optional[float] = None


class ClearanceHoldResponse(ClearanceHoldBase):
    hold_id: int
    status: HoldStatus
    created_at: str
    cleared_at: Optional[str] = None


class AuditLogBase(BaseModel):
    actor_user_id: int
    action: str
    entity_type: str
    entity_id: int
    old_values_json: Optional[str] = None
    new_values_json: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    audit_id: int
    created_at: str


class ImportLogBase(BaseModel):
    source_system: SourceSystem
    records_imported: int
    imported_by: str
    filename: str
    status: str
    message: Optional[str] = None


class ImportLogResponse(ImportLogBase):
    log_id: int
    created_at: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
