# Backend Changes - Dispatcher Operations Center

## Date: 2026-01-30

### 1. Authentication - Added Dispatcher Role

**File:** `backend/src/auth/simple/schemas.py`

```python
class UserRole(str, Enum):
    """User role enumeration"""
    DRIVER = "driver"
    USER = "user"
    ADMIN = "admin"
    DISPATCHER = "dispatcher"  # NEW
```

**Impact:** Minimal - extends existing enum

---

### 2. Seed Script - Added Dispatcher Test Account

**File:** `backend/scripts/seed_users.py`

Added test account:
- **Email:** `dispatcher@pilive.com`
- **Password:** `dispatcher123`
- **Role:** `dispatcher`

**Impact:** None - only affects test data seeding

---

### Future Backend Requirements (Not Yet Implemented)

These will be needed when wiring up the dispatcher UI to real APIs:

1. **Dispatch Management API**
   - Create/update/cancel dispatch requests
   - Assign drivers to calls
   - Update dispatch status
   
2. **Real-time Call Queue**
   - WebSocket or polling for incoming calls
   - Priority queue management
   - Emergency call handling

3. **Driver Availability API**
   - Query available drivers by location
   - Check driver compatibility (vehicle type, accessibility features)
   - Get driver status and location

4. **Dispatch Analytics**
   - Call volume metrics
   - Response time tracking
   - Driver performance stats

5. **Role-based Access Control**
   - Protect dispatcher endpoints with `require_role([UserRole.DISPATCHER])`
   - Separate dispatcher permissions from admin

---

## Summary

**Total Backend Changes:** 2 files (minimal)
- Added `DISPATCHER` enum value
- Added test account to seed script

**No API changes, no database migrations, no new endpoints.**
