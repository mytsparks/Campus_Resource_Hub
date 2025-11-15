## **Campus Resource Hub: User Stories**

---

### **1. Student Persona**

**User Story:**  
_As a Student, I want to search for an available study room and book it for a specific time so that my project group has a guaranteed place to meet._

#### **Acceptance Criteria**

- **Search Filtering**  
  - **Given** I am on the homepage,  
    **When** I enter "study room," a date (e.g., "Nov 17"), a time (e.g., "2:00 PM – 4:00 PM"), and capacity ("4 people"),  
    **Then** the search page returns only study rooms that match those criteria.  
    *(Ref: The search page returns accurate results for a given date/time filter.)*

- **View Room Availability**  
  - **Given** I am on a specific study room's detail page,  
    **When** I view its calendar,  
    **Then** I can clearly see which time slots are booked and which are available.

- **Auto-Approved Bookings**  
  - **Given** I select an available time slot and click "Book,"  
    **When** the room is set to auto-approve,  
    **Then** my booking is immediately confirmed and its status becomes **Approved**.

- **Conflict Prevention**  
  - **Given** I attempt to book a time slot that is already **Approved** for another user,  
    **When** I submit my request,  
    **Then** the system shows an error message and does not create the booking.  
    *(Ref: Booking conflicts are detected and prevented.)*

- **Dashboard Confirmation**  
  - **Given** my booking is successfully approved,  
    **When** I check my dashboard,  
    **Then** I see it listed under **My Bookings**.

- **Booking Notification**  
  - **Given** my booking is confirmed,  
    **Then** I receive a system notification (or simulated email) containing the booking details.

---

### **2. Staff Persona**

**User Story:**  
_As a Staff member, I want to list a new, high-value lab instrument and require manual approval for all bookings so that I can control access and verify student prerequisites before use._

#### **Acceptance Criteria**

- **Create Resource Option**  
  - **Given** I am logged in with a Staff role,  
    **When** I navigate to my dashboard,  
    **Then** I see an option to **Create a New Resource**.  
    *(Ref: An authenticated user can create a resource and set its availability.)*

- **Manual-Approval Resource Setup**  
  - **Given** I am on the Create Resource form,  
    **When** I fill in the details (title, description, category, location) and set booking rules to **Requires Manual Approval**,  
    **Then** the resource is created and all new booking requests require staff approval.

- **View Approval Queue**  
  - **Given** a Student requests this instrument,  
    **When** I check my dashboard,  
    **Then** I see a new request in my **Approval Queue**.

- **Approve Booking**  
  - **Given** I am viewing a pending request,  
    **When** I click **Approve**,  
    **Then** the booking status updates to **Approved** and the student is notified.

- **Reject Booking**  
  - **Given** I am viewing a pending request,  
    **When** I click **Reject**,  
    **Then** the booking status updates to **Rejected** and the student is notified.

- **Students Cannot Modify Resources**  
  - **Given** I am logged in as a Student,  
    **When** I view this resource,  
    **Then** I do not see any option to edit or delete it.

---

### **3. Admin Persona**

**User Story:**  
_As an Administrator, I want to moderate user-generated content by deleting an inappropriate review so that I can maintain a safe and professional platform environment._

#### **Acceptance Criteria**

- **Admin Panel Navigation**  
  - **Given** I am logged in with an Admin role,  
    **When** I navigate to the Admin Panel,  
    **Then** I see management options for **Users**, **Resources**, **Bookings**, and **Reviews**.

- **Moderate Reviews**  
  - **Given** I am on the Reviews management page,  
    **When** I see a review with spam or inappropriate language,  
    **Then** I have a **Delete** button next to that review.

- **Delete Review**  
  - **Given** I click the Delete button for a review,  
    **When** I confirm the action,  
    **Then** the review is permanently removed from the database.  
    *(Ref: Admin can view and modify bookings and moderate content.)*

- **Review Visibility Updated**  
  - **Given** a review has been deleted,  
    **When** any user views the resource page,  
    **Then** the deleted review is no longer displayed.

- **Rating Recalculation**  
  - **Given** the review has been deleted,  
    **When** the resource’s rating is displayed,  
    **Then** the aggregate rating is recalculated without the deleted review’s score.

---
