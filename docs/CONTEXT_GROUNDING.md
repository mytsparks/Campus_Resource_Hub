# Context Grounding Documentation

This document identifies where AI-generated code references materials from the `/docs/context/` folder.

## References to PRD (Product Requirements Document)

### 1. User Role Restrictions
**File:** `src/controllers/resource_routes.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.1 User Management & Authentication
**Implementation:**
```python
# Restrict resource creation to staff and admin only
if current_user.role == 'student':
    flash('Only staff and administrators can create resources. Students can only view, book, and review resources.', 'error')
    return redirect(url_for('resources.list_resources'))
```
**PRD Requirement:** "Roles: Student, Staff, Admin" - Students should only view, book, and review; Staff can create resources.

### 2. Booking Approval Workflow
**File:** `src/controllers/booking_routes.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.4 Booking & Scheduling
**Implementation:**
```python
# Determine approval status based on booking_type
# Open resources: auto-approve if published
# Restricted resources: always require manual approval
booking_type = getattr(resource, 'booking_type', 'open')
if booking_type == 'open' and resource.status == 'published':
    initial_status = 'approved'
else:
    initial_status = 'pending'
```
**PRD Requirement:** "Approval workflow (pending → approved/rejected)" - Implemented with open/restricted resource types.

### 3. Conflict Detection
**File:** `src/data_access/booking_dal.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.4 Booking & Scheduling
**Implementation:**
```python
def check_for_conflict(
    self,
    resource_id: int,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    # Complex time overlap detection logic
```
**PRD Requirement:** "Booking creation with conflict detection" - Prevents double-booking.

### 4. Reviews & Ratings
**File:** `src/forms/resource_forms.py`, `src/data_access/review_dal.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.6 Reviews & Ratings
**Implementation:**
```python
class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[(str(i), '⭐' * i) for i in range(1, 6)],
        validators=[DataRequired(message='Rating is required.')],
    )
```
**PRD Requirement:** "Ability for users to leave a rating (1-5) and feedback after a completed booking" - Implemented with 1-5 star system.

### 5. Aggregate Rating Calculation
**File:** `src/data_access/review_dal.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.6 Reviews & Ratings
**Implementation:**
```python
def get_resource_rating_stats(self, resource_id: int) -> dict:
    """Get aggregate rating statistics for a resource."""
    # Calculates COUNT, AVG, MIN, MAX ratings
```
**PRD Requirement:** "Aggregate rating calculation" - Calculates and displays average ratings.

### 6. Search & Filtering
**File:** `src/controllers/resource_routes.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.3 Search & Filtering
**Implementation:**
```python
resources = dal.get_published_resources(
    search_term=search_term,
    category=category,
    location=location,
    capacity=capacity,
)
```
**PRD Requirement:** "Keyword, category, location, date/time availability, capacity" - All implemented.

### 7. Messaging System
**File:** `src/controllers/message_routes.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.5 Messaging System
**Implementation:**
```python
@message_bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def view_thread(thread_id: int):
    """View and participate in a message thread."""
```
**PRD Requirement:** "Threaded messaging between requester and resource owner" - Implemented.

### 8. Admin Dashboard
**File:** `src/controllers/admin_routes.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.7 Admin Panel
**Implementation:**
```python
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and approval queue."""
```
**PRD Requirement:** "Dashboard for Admins to manage users, resources, and bookings" - Implemented.

## Test Files References

### Unit Tests
**Files:** 
- `tests/unit/test_booking_conflict.py`
- `tests/unit/test_review_aggregation.py`

**Reference:** `docs/context/PM/PRD.md` - Section 4.4 and 4.6
**Example:**
```python
"""
Unit tests for booking conflict detection logic.
References: docs/context/PM/PRD.md - Section 4.4 Booking & Scheduling
"""
```

### Integration Tests
**File:** `tests/integration/test_auth_flow.py`
**Reference:** `docs/context/PM/PRD.md` - Section 4.1
**Example:**
```python
"""
Integration tests for authentication flow.
References: docs/context/PM/PRD.md - Section 4.1 User Management & Authentication
"""
```

### Security Tests
**File:** `tests/security/test_sql_injection.py`
**Reference:** `docs/context/PM/PRD.md` - Section 7 Security & Validation
**Example:**
```python
"""
Security tests for SQL injection prevention.
References: docs/context/PM/PRD.md - Section 7 Security & Validation
"""
```

### End-to-End Documentation
**File:** `docs/E2E_BOOKING_SCENARIO.md`
**Reference:** `docs/context/PM/PRD.md` - Section 4.4
**Example:**
```markdown
**Reference:** `docs/context/PM/PRD.md` - Section 4.4 Booking & Scheduling
```

## Summary

All major features implemented reference the PRD document in `/docs/context/PM/PRD.md`:
- User roles and permissions (Section 4.1)
- Resource listings (Section 4.2)
- Search & filtering (Section 4.3)
- Booking & scheduling (Section 4.4)
- Messaging (Section 4.5)
- Reviews & ratings (Section 4.6)
- Admin panel (Section 4.7)
- Security requirements (Section 7)

The codebase maintains alignment with the PRD requirements throughout implementation.

