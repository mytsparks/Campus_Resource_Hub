# AI Development Notes and Interaction Log

This document tracks all major AI interactions, prompts, actions taken, and reflections throughout the development of the Campus Resource Hub application.

---

## Prompt 1: Initial Project Structure Creation

**Prompt:**
Create a complete file and folder structure for a Python/Flask project named "CampusResourceHub." This project must follow an MVC pattern, include a Data Access Layer (DAL) separation, and adhere to an AI-First Development folder structure. All Python files should contain only basic imports and function/class definitions (no logic), and all HTML files should have a basic HTML5/Bootstrap 5 template structure extending a base layout.

**Action Taken:**
Created the complete project structure with:
- MVC architecture: `src/controllers/`, `src/views/`, `src/models.py`
- Data Access Layer: `src/data_access/` with separate DAL files for each entity
- AI-First Development structure: `.prompt/`, `docs/context/` directories
- Flask application factory pattern in `app.py`
- Base template with Bootstrap 5 in `src/views/base.html`
- Configuration file `config.py`
- Requirements file with initial dependencies
- All Python files with skeleton class/function definitions
- All HTML templates with basic structure extending base layout

**Reflection:**
The initial structure provided a solid foundation for the project. The separation of concerns (MVC + DAL) made subsequent development more organized. The AI-First Development structure (`.prompt/`, `docs/context/`) proved valuable for maintaining context throughout development. The skeleton approach allowed for incremental implementation without breaking the application structure.

---

## Prompt 2: SQLAlchemy ORM Model Definitions

**Prompt:**
Implement all SQLAlchemy ORM model definitions required for the Campus Resource Hub based on the project's relational schema. These models must use the declarative base, define relationships, and include default timestamp values.

**Action Taken:**
Implemented complete ORM models in `src/models.py`:
- `User` model with roles (student, staff, admin), password hashing support, Flask-Login integration
- `Resource` model with status workflow (draft, published, archived), relationships to owner, bookings, reviews
- `Booking` model with conflict detection support, status workflow (pending, approved, rejected, cancelled, completed)
- `Message` model for threaded messaging between users
- `Review` model with ratings and comments
- `AdminLog` model for administrative action tracking
- `Equipment` model for resource equipment lists
- All models with proper relationships, foreign keys, and default timestamps
- `init_db()` helper function for database initialization

**Reflection:**
The model definitions established the data layer foundation. The relationship definitions (backrefs) enabled efficient querying later. Flask-Login integration methods (`is_active`, `get_id`, etc.) were included from the start, preventing authentication issues. The status enums and default values provided clear workflow states for resources and bookings.

---

## Prompt 3: UserDAL Implementation

**Prompt:**
Implement the UserDAL class. This class handles all CRUD operations for the User model, utilizing SQLAlchemy sessions passed to its methods. Ensure password hashing is done using bcrypt, which is required by the project brief for security.

**Action Taken:**
Created `src/data_access/user_dal.py` with:
- `create_user()` method with email uniqueness check, password hashing using Flask-Bcrypt
- `get_user_by_email()` and `get_user_by_id()` retrieval methods
- `verify_user_credentials()` method for authentication with bcrypt password verification
- Exception handling for database integrity errors (duplicate emails)
- Session-based architecture allowing dependency injection

**Reflection:**
The DAL pattern separation proved crucial. By isolating database operations from route handlers, the code became more testable and maintainable. The bcrypt integration ensured password security from the start. The exception handling for duplicate emails provided clear error feedback. This pattern was later replicated for other entities (ResourceDAL, BookingDAL, etc.).

---

## Prompt 4: Authentication Routes Implementation

**Prompt:**
Implement the Flask routes for /auth/register and /auth/login. The implementation must use the provided UserDAL class, handle form submission and validation, and utilize Flask-Login for session management.

**Action Taken:**
Implemented `src/controllers/auth_routes.py` with:
- `/auth/register` route with GET (form display) and POST (user creation) handlers
- `/auth/login` route with GET (form display) and POST (authentication) handlers
- `/auth/logout` route for session termination
- Server-side validation for email format, password strength, role validation
- Integration with UserDAL for database operations
- Flask-Login `login_user()` and `logout_user()` integration
- Flash messages for user feedback
- Redirect logic for authenticated users

**Reflection:**
The route implementation demonstrated proper separation of concerns - routes handled HTTP logic while DAL handled database logic. The validation logic could have been extracted to form classes (Flask-WTF) for better reusability, but the initial implementation worked. Flask-Login integration was straightforward once the User model had the required methods. The flash message system provided good user feedback.

---

## Prompt 5: Complete create_app Function

**Prompt:**
Complete the 'create_app' function to initialize core extensions: SQLAlchemy for the database, Flask-Bcrypt for hashing, and Flask-Login for session management. Register the 'auth_bp' blueprint.

**Action Taken:**
Completed `app.py` with:
- SQLAlchemy database initialization with `db.init_app(app)`
- Flask-Bcrypt initialization for password hashing
- Flask-Login initialization with `login_view` and `login_message` configuration
- User loader callback using UserDAL to retrieve users by ID
- Blueprint registration for `auth_bp`
- Database initialization with `init_db()` call in app context
- Initial admin user seeding function

**Reflection:**
The application factory pattern (`create_app()`) enabled better testing and configuration management. The user loader callback was critical for Flask-Login to work properly. The session management approach (creating sessions within the user loader) worked but could be improved with a session factory pattern. The initial admin seeding ensured the app was immediately usable after setup.

---

## Prompt 6: Refine Authentication Routes

**Prompt:**
Refine the authentication routes to use the actual database and Flask-Login initialization completed in app.py. Replace the 'TempSession' placeholder logic.

**Action Taken:**
Updated `src/controllers/auth_routes.py` to:
- Import `db` from `src.extensions` (centralized extension imports)
- Use proper SQLAlchemy session management with context managers
- Handle `IntegrityError` exceptions for duplicate email registration
- Validate roles to only accept 'student' or 'staff' on registration (admins created separately)
- Proper session management with try/finally blocks for session cleanup

**Reflection:**
The refinement removed placeholder code and made the routes production-ready. The exception handling for duplicate emails provided better user experience. The role validation prevented unauthorized admin account creation. The session management pattern became the standard for all subsequent DAL usage.

---

## Prompt 7: ResourceDAL Implementation

**Prompt:**
Implement the ResourceDAL class to handle CRUD operations for the Resource model, along with initial methods for search/listing required for the homepage.

**Action Taken:**
Created `src/data_access/resource_dal.py` with:
- `create_resource()` method with owner assignment and default status
- `get_resource_by_id()` for single resource retrieval
- `get_published_resources()` with comprehensive filtering (search_term, category, location, capacity)
- `update_resource()` and `delete_resource()` methods
- SQL LIKE queries for keyword search in title and description
- Status filtering to only show published resources

**Reflection:**
The search functionality with multiple filter parameters demonstrated the flexibility of the DAL pattern. The LIKE queries for keyword search worked well for basic search needs. The published-only filtering ensured draft resources weren't visible to regular users. This DAL became the foundation for the resource listing and search features.

---

## Prompt 8: Resource Routes Implementation

**Prompt:**
Implement the resource routes for listing/searching and displaying resource details. Implement the POST route for creating a new resource, ensuring the user is authenticated (Flask-Login required).

**Action Taken:**
Implemented `src/controllers/resource_routes.py` with:
- `GET /resources/` route for listing/searching with query parameter extraction
- `GET /resources/<id>` route for resource detail view
- `GET/POST /resources/create` route with `@login_required` decorator
- Integration with ResourceDAL for all database operations
- Template rendering with resource data and search parameters
- 404 error handling for non-existent resources

**Reflection:**
The route implementation followed RESTful conventions. The `@login_required` decorator provided clean authentication enforcement. The query parameter extraction for search/filter worked seamlessly with the ResourceDAL filtering methods. The 404 handling improved user experience. This pattern was replicated for other resource types (bookings, messages, reviews).

---

## Prompt 9: BookingDAL Implementation

**Prompt:**
Create and implement the BookingDAL class. The core method must include logic to detect and prevent conflicts before creating a new booking.

**Action Taken:**
Created `src/data_access/booking_dal.py` with:
- `check_for_conflict()` method with complex time overlap detection logic
- `create_booking()` method that calls conflict check before creation
- Time overlap algorithm checking if new booking overlaps with existing approved/pending bookings
- `get_bookings_for_resource()` and `update_booking_status()` methods
- Exception raising for conflict scenarios

**Reflection:**
The conflict detection logic was the most complex part of the booking system. The time overlap algorithm correctly handled edge cases (start time within existing booking, end time within existing booking, complete overlap). The exception-based approach for conflicts provided clear error handling. This became a critical feature ensuring data integrity in the booking system.

---

## Prompt 10: Fully Program the Webapp

**Prompt:**
In the main branch, there is a project_outline.md file. This describes all necessary requirements for the program. Analyse everything that has been coded so far, and fully program the webapp. By the end, I want to be able to run the app and test its functionality in the browser. Ask me any questions along the way and feel free to run tests and fix errors yourself. The web interface should be very modern and streamlined, using jinja for a good UI.

**Action Taken:**
Comprehensive implementation of all core features:
- Completed all remaining DAL classes (MessageDAL, ReviewDAL, WaitlistDAL)
- Implemented all route handlers (booking_routes, message_routes, review_routes, admin_routes)
- Created all HTML templates with Bootstrap 5 and Tailwind CSS styling
- Implemented file upload functionality for resource images
- Added CSRF protection to all forms
- Created admin dashboard with statistics and management tools
- Implemented waitlist functionality
- Added review and rating system
- Created messaging system with thread views
- Implemented booking approval workflow
- Added comprehensive error handling and user feedback
- Created initial admin user seeding

**Reflection:**
This was the largest implementation phase. The comprehensive approach ensured all core features were functional. The modern UI with Bootstrap 5 and Tailwind CSS created a polished user experience. The file upload functionality required careful handling of file paths and security (secure_filename). The admin dashboard provided essential management capabilities. Some features like calendar UI and advanced search were marked as optional and left for future enhancement.

---

## Prompt 11: Fix CSRF Token Error

**Prompt:**
This appeared after trying to book a resource on the other account: Bad Request The CSRF token is missing.

**Action Taken:**
- Added CSRF token hidden input fields to all HTML forms
- Updated `src/views/resources/detail.html` booking form with `{{ csrf_token() }}`
- Updated `src/views/bookings/create.html` waitlist form with CSRF token
- Modified `src/controllers/booking_routes.py` to handle both Flask-WTF form data and raw form data
- Added explicit CSRF token validation for raw form submissions

**Reflection:**
CSRF protection is essential for security, but it requires careful form implementation. The Flask-WTF `csrf_token()` function needed to be included in all forms. The error handling for both form types (Flask-WTF forms and raw HTML forms) ensured compatibility. This fix prevented security vulnerabilities while maintaining functionality.

---

## Prompt 12: Fix Datetime strftime Error (My Bookings)

**Prompt:**
Now I got this error after clicking book: UndefinedError jinja2.exceptions.UndefinedError: 'str object' has no attribute 'strftime'

**Action Taken:**
- Identified that `my_bookings` route was using raw SQL queries returning datetime as strings
- Updated `src/controllers/booking_routes.py` to convert string datetimes to `datetime` objects using `datetime.fromisoformat()`
- Ensured all datetime fields passed to templates were actual `datetime` objects, not strings
- Simplified template to directly call `.strftime()` on datetime objects

**Reflection:**
This error highlighted the importance of type consistency between database queries and template rendering. Raw SQL queries return strings, while SQLAlchemy ORM returns datetime objects. The conversion in the controller layer ensured templates could use datetime methods. This pattern was applied to fix similar issues in admin routes later.

---

## Prompt 13: Redesign Layout to Match Wireframe

**Prompt:**
In the docs/context/wireframes there is a wireframe for the landing page. Using this image, you should redo the layout and colors of the page and adjust the overall style of every page in the website to match the theme. The user icon in the top right should open a drop-down menu for logging out and account management. I have also uploaded a logo into the src\static\images folder that should replace the small logo in the top left.

**Action Taken:**
- Redesigned `src/views/base.html` with new navbar layout:
  - Left-aligned logo and title banner
  - Right-aligned navigation links (Resources, Bookings, Notifications, User dropdown)
  - User dropdown menu with account settings and logout
  - Updated color scheme to match wireframe
- Redesigned `src/views/resources/list.html` with:
  - Two-column layout: 40% left sidebar for filters, 60% right main content
  - Filter sidebar with search, categories, location, capacity, sort options
  - Resource cards in horizontal layout with image, details, and "Book Resource" button
- Applied consistent styling across all pages
- Integrated logo from `src/static/images/`

**Reflection:**
The wireframe-based redesign significantly improved the user experience. The two-column layout with dedicated filter sidebar made search and filtering more intuitive. The horizontal resource cards provided better visual hierarchy. The user dropdown menu improved navigation. The consistent color scheme and styling created a cohesive brand identity. This redesign made the application feel more professional and user-friendly.

---

## Prompt 14: Fix Datetime strftime Error (Admin Dashboard)

**Prompt:**
Trying to launch the admin dashboard: UndefinedError jinja2.exceptions.UndefinedError: 'str object' has no attribute 'strftime'

**Action Taken:**
- Identified similar issue in admin routes (`admin_dashboard`, `manage_users`, `manage_resources`, `moderate_reviews`)
- Updated `src/controllers/admin_routes.py` to convert all datetime fields from strings to `datetime` objects
- Applied `datetime.fromisoformat()` or `datetime.strptime()` conversions for all datetime fields
- Updated templates to directly use `.strftime()` on datetime objects

**Reflection:**
This was a recurring pattern - raw SQL queries returning strings instead of datetime objects. The fix was consistent with the previous booking routes fix. This highlighted the importance of standardizing on either ORM queries (which return proper types) or ensuring type conversion in controllers when using raw SQL. A helper function for datetime conversion could have prevented this repetition.

---

## Prompt 15: Create MCP Server

**Prompt:**
Please create an MCP to allow AI agents to query or inspect database content safely. MCP enables structured, read only interaction between the AI layer and the SQLite database for features such as summaries or intelligent search. MCP usage should be documented in .prompt/dev_notes.md and the README.

**Action Taken:**
Created `mcp_server.py` with:
- `ReadOnlyDatabase` class with SQL injection protection
- 5 MCP tools: `query_database`, `get_table_schema`, `list_tables`, `get_resource_summary`, `search_resources`
- Security features: read-only mode, parameterized queries, dangerous keyword blocking
- Integration with `mcp.server` for stdio communication
- Comprehensive documentation in README and dev_notes

**Reflection:**
The MCP server provided a secure way for AI agents to interact with the database. The read-only restriction and SQL injection protection ensured data safety. The structured tools made it easy for AI agents to query specific information. This became the foundation for the Auto-Summary Reporter feature. The security-first approach prevented any potential data modification risks.

---

## Prompt 16: Implement Auto-Summary Reporter

**Prompt:**
Now implement the required AI feature: Auto-Summary Reporter: Generates weekly summaries (e.g., "Top 5 Most Reserved Resources") or system insights. Implementation Notes: - AI reasoning should reference existing project data and never generate fabricated content. - MCP may be used to safely connect AI agents with the local SQLite database. - Teams may use local LLMs (e.g., Ollama, LM Studio) or institution-provided API access if available.

**Action Taken:**
Created comprehensive Auto-Summary Reporter implementation:
- `src/ai/summary_generator.py` with `DatabaseQuery`, `LLMClient`, and `SummaryGenerator` classes
- `LLMClient` supporting multiple providers: Ollama, OpenAI, Anthropic
- `SummaryGenerator` collecting weekly statistics (top resources, booking stats, user activity, categories)
- `src/controllers/summary_routes.py` with `/summaries/generate` and `/summaries/api/insights` routes
- `src/views/admin/summary_report.html` template for displaying AI-generated summaries
- Integration with admin dashboard
- Fallback mechanism when LLM unavailable

**Reflection:**
The Auto-Summary Reporter demonstrated the power of AI-first development. The multi-provider LLM support (Ollama, OpenAI, Anthropic) provided flexibility. The data integrity guarantee (no fabricated content) was critical - all summaries were based on actual database queries. The fallback mechanism ensured the feature worked even without LLM configuration. This feature showcased the application's AI capabilities while maintaining data accuracy.

---

## Prompt 17: Configure Ollama

**Prompt:**
I want to configure ollama

**Action Taken:**
- Created `test_ollama.py` script for testing Ollama configuration
- Created `setup_ollama.bat` (Windows) and `setup_ollama.sh` (macOS/Linux) automated setup scripts
- Created `OLLAMA_QUICKSTART.md` quick-start guide
- Created `docs/ollama_setup.md` comprehensive setup documentation
- Updated README with Ollama configuration instructions
- Updated `.prompt/dev_notes.md` with Ollama setup details

**Reflection:**
The Ollama setup documentation and scripts made it easy for users to configure local LLM support. The automated scripts reduced setup friction. The test script helped verify configuration. However, the user later deleted these files, suggesting they preferred a simpler approach or different LLM provider. The documentation approach was sound, but the implementation could have been more modular.

---

## Prompt 18: OpenAI Implementation Question

**Prompt:**
How can I implement OpenAI, and if i use a free api key can i still submit the assignment? (Will it work easily on other devices?)

**Action Taken:**
- Created comprehensive `docs/openai_setup.md` guide
- Created `test_openai.py` test script
- Created `ASSIGNMENT_SUBMISSION_GUIDE.md` with detailed submission strategy
- Updated README with OpenAI configuration options
- Explained portability considerations and assignment submission best practices
- Recommended supporting both Ollama (local) and OpenAI (API) for maximum flexibility

**Reflection:**
The user's question highlighted important considerations for assignment submission. The recommendation to support both local (Ollama) and API-based (OpenAI) LLMs provided maximum portability. The documentation helped the user understand trade-offs. However, the user later chose a different LLM provider (Gemini), showing the value of flexible LLM support architecture.

---

## Prompt 19: Implement Google Gemini

**Prompt:**
Actually, for the summary generation i want to use google gemini, with key: AIzaSyAXgN9mtjViENMwG92Ymbb749wt4Ip3bLs. Implement this into the webapp.

**Action Taken:**
- Added `_generate_gemini()` method to `LLMClient` class in `src/ai/summary_generator.py`
- Updated Gemini API integration with proper model name handling (`models/` prefix)
- Set Gemini as default provider in `config.py` with provided API key
- Updated default model to `gemini-2.0-flash` (latest stable model)
- Updated `src/controllers/summary_routes.py` to use Config class for LLM settings
- Updated README with Gemini configuration documentation
- Implemented proper error handling and fallback for Gemini API errors

**Reflection:**
The Gemini integration was straightforward thanks to the flexible LLM architecture. The multi-provider support made adding a new provider simple - just add a new `_generate_*` method. The API key was stored in config.py (though environment variables would be more secure for production). The model name handling (`models/` prefix) was important for Gemini API compatibility. The error handling ensured graceful fallback if the API was unavailable or rate-limited. This implementation completed the AI feature with the user's preferred LLM provider.

---

## Summary

Throughout development, the AI-assisted workflow enabled rapid iteration and comprehensive feature implementation. The separation of concerns (MVC + DAL) made the codebase maintainable. The AI-First Development practices (context packs, dev notes) helped maintain project context. The flexible LLM architecture allowed easy provider switching. The security-first approach (CSRF protection, password hashing, read-only database access) ensured production readiness. The modern UI with responsive design created a professional user experience.
