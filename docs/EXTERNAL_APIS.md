# External API Integration Details (R5, R6)

## Integration Summary

| API            | Type                   | Auth             | Timeout | Cache                  | Fallback      |
| -------------- | ---------------------- | ---------------- | ------- | ---------------------- | ------------- |
| Registrar Mock | Internal (starter kit) | API key (header) | 10s     | DB table               | Previous sync |
| Nager.Date     | Public                 | None             | 5s      | DB table (24h)         | Default date  |
| Open-Meteo     | Public                 | None             | 3s      | sessionStorage (30min) | Widget hidden |

## Registrar Mock API (R5)

**Source:** `registrar_mock_api.py` from starter kit (Flask, localhost:8001)
**Endpoint:** `GET /api/students`
**Auth:** `X-API-Key` header, key stored in `.env` as `REGISTRAR_API_KEY`
**Client:** `sync_registrar.py` (S4) using `httpx`
**Validation:** Pydantic model enforces student_id format, non-empty name, valid status enum
**Mapping:** See DATA_MAPPING.md Source 3
**Error Handling:**

- 5xx / timeout: 3 retries, exponential backoff (2s, 4s, 8s)
- All retries fail: log warning, skip sync, use cached data from previous run
- 401: token refresh attempt
  **Security:** HTTPS in production, HTTP localhost only in dev. Response validated before DB write.

## Nager.Date Holidays API (R6)

**Source:** `https://date.nager.at/api/v3/PublicHolidays/{year}/PH`
**Auth:** None (free, no key)
**Rate Limit:** ~10 requests/minute
**Purpose:** Compute clearance deadline (last working day before semester end)

**Deadline Logic:**

1. Fetch PH holidays for current year
2. Filter holidays within 14 days of SEMESTER_END_DATE
3. Walk backward from end date, skip weekends + holidays
4. First working day = clearance deadline
5. Cache in `holiday_cache` table for 24 hours

**Fallback:** `DEFAULT_CLEARANCE_DEADLINE` from `.env` if API unreachable
**Security:** URL constructed from server clock (no user input, no SSRF). HTTPS enforced. Response validated via Pydantic.

## Open-Meteo Weather API (R6 Bonus)

**Source:** `https://api.open-meteo.com/v1/forecast?latitude=7.31&longitude=125.67&current_weather=true`
**Auth:** None
**Purpose:** Campus weather widget on student dashboard
**Client:** Front-end JavaScript (Fetch API), not server-side
**Cache:** `sessionStorage`, 30 minutes
**Fallback:** Widget hidden silently on failure
**Impact:** Zero. Weather is decorative. Failure does not affect clearance processing.
