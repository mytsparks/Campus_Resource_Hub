# End-to-End Booking Scenario

This document describes the complete flow for booking a resource in the Campus Resource Hub application.

**Reference:** `docs/context/PM/PRD.md` - Section 4.4 Booking & Scheduling

## Scenario: Student Books a Study Room

### Prerequisites
1. A staff member has created and published a resource (e.g., "Study Room 101")
2. The resource is set to "open" booking type (auto-approved) or "restricted" (requires approval)
3. A student user account exists

### Step-by-Step Flow

#### 1. User Authentication
- **Action:** Student navigates to the application and logs in
- **URL:** `/auth/login`
- **Input:** Email and password
- **Expected:** User is authenticated and redirected to resource listing page

#### 2. Browse Resources
- **Action:** Student views available resources
- **URL:** `/resources/`
- **Expected:** List of published resources is displayed
- **Features:**
  - Can filter by category, location, capacity
  - Can search by keyword
  - Can sort by name, recent, most booked, top rated
  - Can click "View Details" to see resource info in modal
  - Can click "Book Resource" to go to booking page

#### 3. View Resource Details (Optional)
- **Action:** Student clicks "View Details" button
- **Expected:** Modal popup displays:
  - Resource image
  - Full description
  - Equipment list
  - Reviews and ratings
  - Booking type indicator
  - Action buttons (View Full Page, Book Resource)

#### 4. Navigate to Booking Page
- **Action:** Student clicks "Book Resource" button
- **URL:** `/bookings/create/<resource_id>`
- **Expected:** Booking form is displayed with:
  - Start date/time picker
  - End date/time picker
  - Optional message field
  - Calendar showing existing bookings

#### 5. Fill Booking Form
- **Action:** Student enters:
  - Start date/time: Tomorrow at 10:00 AM
  - End date/time: Tomorrow at 12:00 PM
  - Optional message: "Need quiet space for group study"
- **Validation:**
  - End time must be after start time
  - Times must be in the future
  - No conflict with existing bookings

#### 6. Submit Booking Request
- **Action:** Student clicks "Request Booking" button
- **Backend Processing:**
  1. Validate form data
  2. Check for time conflicts with existing bookings
  3. Determine approval status:
     - If resource is "open" and published → status = "approved"
     - If resource is "restricted" → status = "pending"
  4. Create booking record
  5. If message provided, create message to resource owner
  6. If conflict detected:
     - Notify admin of conflict
     - Redirect user to message page with pre-filled message

#### 7. Booking Confirmation
- **Expected Result (Open Resource):**
  - Booking is automatically approved
  - Flash message: "Booking approved successfully!"
  - Redirect to `/bookings/my-bookings`
  - Booking appears in "My Bookings" with status "Approved"

- **Expected Result (Restricted Resource):**
  - Booking status is "pending"
  - Flash message: "Booking requested successfully!"
  - Resource owner receives notification
  - Admin can see booking in approval queue
  - Student can see booking in "My Bookings" with status "Pending"

#### 8. View My Bookings
- **Action:** Student navigates to dashboard
- **URL:** `/user/dashboard` or `/bookings/my-bookings`
- **Expected:** 
  - Booking is listed with:
    - Resource title
    - Location
    - Start/end times
    - Status badge (Approved/Pending)
  - Can cancel pending bookings
  - Can view resource details

### Alternative Flows

#### Conflict Detection Flow
If a booking conflict is detected:
1. User sees flash message: "This time slot is already booked. Please send a message to the resource owner to discuss availability."
2. Admin receives automatic notification message
3. User is redirected to message page with pre-filled message
4. User can discuss alternative times with resource owner

#### Approval Flow (Restricted Resources)
1. Staff/Admin views pending bookings in admin dashboard
2. Staff/Admin can approve or reject booking
3. If approved:
   - Booking status changes to "approved"
   - Student receives notification (if implemented)
4. If rejected:
   - Booking status changes to "rejected"
   - Student can see rejection in their bookings

### Manual Testing Checklist

- [ ] User can register and login
- [ ] User can browse and filter resources
- [ ] "View Details" modal displays correctly
- [ ] Booking form validates input correctly
- [ ] Conflict detection works for overlapping times
- [ ] Open resources are auto-approved
- [ ] Restricted resources require approval
- [ ] Admin is notified of conflicts
- [ ] Bookings appear in user dashboard
- [ ] Bookings can be cancelled
- [ ] Mobile responsive design works

### Automated Testing

See `tests/integration/test_auth_flow.py` and `tests/unit/test_booking_conflict.py` for automated test coverage.

### Related Features

- **Reviews:** After booking is completed, user can leave a review
- **Messaging:** Users can message resource owners about bookings
- **Waitlist:** If resource is fully booked, users can join waitlist

