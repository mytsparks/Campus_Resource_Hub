# Product Requirements Document (PRD)
## Campus Resource Hub  
**Module:** AiDD / X501   
**Date:** Fall 2025  

---

## 1. Product Overview
The **Campus Resource Hub** is a full-stack web application that allows university departments, student organizations, and individuals to list, share, and reserve campus resources such as study rooms, AV equipment, lab instruments, event spaces, and tutoring time. The platform enables discovery, booking, approval workflows, messaging, and reviews, with role-based access for students, staff, and administrators.

The product supports the broader program goal of building production-quality software using AI-first development practices within a modern, context-aware repository.

---

## 2. Objectives & Goals
### Primary Objective  
Enable a centralized, user-friendly system to search for, reserve, and manage university resources with transparent approval workflows and clear availability.

### Goals  
- Reduce friction in reserving campus resources.  
- Improve visibility of resource availability across campus units.  
- Provide consistent booking, messaging, and review experiences.  
- Support admin oversight for conflict resolution and activity monitoring.  
- Enable extensibility for advanced features (e.g., AI concierge, scheduling insights).

---

## 3. Key Stakeholders
- **Students:** Discover resources, book rooms/equipment, leave reviews.  
- **Staff / Resource Owners:** Publish and manage resources, approve bookings, view usage.  
- **Administrators:** Oversee users, moderate content, manage approvals/abuse cases.  
- **Development Team:** Responsible for implementation, testing, documentation.  
- **Instructors/Academic Staff:** Evaluate functionality, code quality, documentation, and AI usage.

---

## 4. Scope
### In Scope (Core Features)
1. **User Management & Authentication**  
   - Sign up, sign in, sign out.  
   - Roles: Student, Staff, Admin.  
   - Hashed password storage.

2. **Resource Listings**  
   - CRUD operations for resources.  
   - Attributes: title, description, images, location, capacity, equipment, availability rules.  
   - Listing states: draft, published, archived.

3. **Search & Filtering**  
   - Keyword, category, location, date/time availability, capacity.  
   - Sort: recent, most booked, top rated.

4. **Booking & Scheduling**  
   - Calendar-based booking (start/end time, optional recurrence).  
   - Conflict detection and approval workflow (auto or staff/admin).  
   - Email or simulated notification confirmations.

5. **Messaging & Notifications**  
   - Threaded message exchange between requester and resource owner.

6. **Reviews & Ratings**  
   - 1–5 star ratings and comments for completed bookings.  
   - Aggregate rating display and badges.

7. **Admin Dashboard**  
   - User moderation, approvals queue, resource and booking management.

8. **AI-First Requirements** (minimum)  
   - `.prompt/` folder with dev notes & golden prompts.  
   - AI-assisted documentation.  
   - One AI-powered feature (e.g., concierge, scheduler, auto-summary).  

### Out of Scope (Non-Goals)
- Real-time chat using WebSockets.  
- Full mobile-native application.  
- Automated calendar integrations with Google/iCal (optional).  
- ML-based recommendation systems (beyond required AI feature).

---

## 5. Success Metrics
- **Functionality:** Core booking and resource workflows operate without errors.  
- **Search Accuracy:** Relevant resources returned based on filters and availability.  
- **Conflict Resolution:** 100% of double-booking attempts correctly blocked.  
- **User Experience:** Intuitive navigation, responsive UI, minimal validation errors.  
- **Admin Efficiency:** Clear moderation flows for users, resources, and reviews.  
- **AI Integration Quality:** AI feature demonstrates meaningful context awareness and accuracy.

---

## 6. User Flows (High-Level)
### 6.1 Student Books a Study Room
1. Student searches by “study room” + date/time.  
2. Results show available rooms & availability calendar.  
3. Booking request submitted → pending or auto-approved.  
4. Confirmation sent to requester; booking appears in dashboard.

### 6.2 Staff Lists a Lab Instrument
1. Staff creates listing requiring approval.  
2. Student submits request.  
3. Staff reviews prerequisites and approves.  
4. Booking status updated; notifications sent.

### 6.3 Admin Moderates Abuse
1. Admin views flagged reviews or messages.  
2. Admin hides/deletes content or suspends user.  
3. Actions logged in admin logs.

---

## 7. Functional Requirements
### 7.1 Authentication
- Must validate email, password strength, and role assignment.  
- Passwords hashed using bcrypt or equivalent.

### 7.2 Resource Management
- CRUD operations restricted based on ownership and role.  
- Validate availability rules server-side.

### 7.3 Booking Logic
- Prevent overlapping bookings for the same resource.  
- Support approval workflows.  
- Store booking status transitions (pending → approved → completed/cancelled).

### 7.4 Messaging System
- Store sender/receiver IDs, timestamps, and message content.  
- Messages accessible from user dashboard.

### 7.5 Reviews  
- One review per completed booking.  
- Aggregate scores shown on listing pages.

### 7.6 Admin Tools  
- Manage users, resources, and bookings.  
- View reports or usage summaries.

---

## 8. Non-Functional Requirements
- **Architecture:** MVC structure with a dedicated Data Access Layer.  
- **Security:**  
  - Server-side validation of all fields.  
  - Parameterized queries/ORM to prevent SQL injection.  
  - XSS protection via template escaping.  
  - CSRF tokens on all forms.  
- **Accessibility:** Semantic HTML, keyboard navigation, appropriate contrast.  
- **Performance:** Resource search and booking operations complete within 1 second under normal load.

---

## 9. AI Feature Requirement
At least one of the following must be implemented:
- **Resource Concierge:** Natural-language Q&A referencing project context and database content.  
- **AI Scheduler:** Suggests optimal booking times or resolves conflict alternatives.  
- **Auto-Summary Reporter:** Weekly insights, e.g., “Top resources by usage.”

AI outputs must be verified, grounded in real data, and documented in `.prompt/dev_notes.md`.

---

## 10. Success Criteria for Completion
- All core features delivered and functional.  
- Clear README, ERD, and setup instructions.  
- Complete PRD, wireframes, prompt logs, and working demo.  
- Required AI feature implemented and demonstrably useful.  
- Project deploys locally with accurate data and validation.

---

*End of PRD*
