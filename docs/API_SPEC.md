# Hub API Specification (R7)

## Authentication

All endpoints except `/api/health` and `/api/clearance/verify/{token}` require:

Authorization: Bearer <JWT>

Tokens expire after 1 hour. Obtained via `POST /api/auth/login`.

## ID Handling Rules

| Actor     | Requests                         | Responses                |
| --------- | -------------------------------- | ------------------------ |
| Student   | JWT identifies them (no ID sent) | Masked: YYYY-\*\*\*\*-NN |
| Staff     | Real student ID in URL           | Full ID                  |
| Admin     | Real student ID in URL           | Full ID                  |
| Audit Log | N/A                              | Real ID internal only    |

## Endpoints

### 1. POST /api/auth/login

- **Auth:** None
- **Body:** `{ "username": "string", "password": "string" }`
- **200:** `{ "access_token": "jwt", "token_type": "bearer", "role": "student|staff|admin" }`
- **401:** `{ "detail": "Invalid credentials" }` (generic, no enumeration)
- **429:** `{ "detail": "Too many attempts. Try again in 60s" }`

### 2. GET /api/clearance/me

- **Auth:** JWT (student)
- **200:** `{ "student_id": "2022-****-01", "name": "Juan D.", "status": "not_cleared", "holds": [...], "deadline": "2026-12-16" }`
- **403:** If role is not student

### 3. GET /api/clearance/student/{real_student_id}

- **Auth:** JWT (staff/admin)
- **200:** Full student record with unmasked ID and all holds
- **403:** If role is student
- **404:** Student not found

### 4. GET /api/clearance/deadline

- **Auth:** JWT (any role)
- **200:** `{ "deadline": "2026-12-16", "source": "nager_date|default" }`
- Uses Nager.Date API, falls back to DEFAULT_CLEARANCE_DEADLINE

### 5. POST /api/clearance/slip

- **Auth:** JWT (student)
- **200:** `{ "token": "signed_hmac_token", "qr_url": "/verify/{token}", "expires": "2026-12-16T23:59:59" }`
- **400:** `{ "detail": "Clearance not complete" }` if any hold is active

### 6. GET /api/clearance/verify/{signed_token}

- **Auth:** None (public)
- **200:** `{ "verified": true|false, "student_id": "2022-****-01", "name": "Juan D.", "cleared_date": "2026-11-28", "expires": "2026-12-16" }`

### 7. PUT /api/holdings/{holding_id}

- **Auth:** JWT (staff)
- **Body:** `{ "status": "cleared", "cleared_by": "staff_id" }`
- **200:** Updated holding record
- **403:** If staff office does not match holding source
- **404:** Holding not found
- **409:** Concurrent update conflict

### 8. POST /api/student-affairs/records

- **Auth:** JWT (staff/admin)
- **Body:** `{ "student_id": "2022-0045-01", "hold_type": "disciplinary", "description": "...", "semester": "2026-2027-1" }`
- **201:** Created record
- **422:** Pydantic validation error

### 9. GET /api/reports/registrar?format={csv|json|xml}

- **Auth:** JWT (admin)
- **200:** File download with appropriate Content-Type
- **400:** Unsupported format
- **403:** If role is not admin

### 10. GET /api/health

- **Auth:** None
- **200:** `{ "status": "ok", "timestamp": "2026-11-28T10:00:00Z" }`
- No sensitive data exposed (no active_users count, no DB details)

## Status Code Summary

| Code | Meaning                        |
| ---- | ------------------------------ |
| 200  | Success                        |
| 201  | Created                        |
| 400  | Bad request                    |
| 401  | Unauthenticated                |
| 403  | Unauthorized (wrong role)      |
| 404  | Not found                      |
| 405  | Method not allowed             |
| 409  | Conflict                       |
| 413  | Payload too large              |
| 422  | Validation error               |
| 429  | Rate limited                   |
| 500  | Server error (generic message) |
| 503  | Service unavailable            |
