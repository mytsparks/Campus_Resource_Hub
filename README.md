# Campus Resource Hub - AiDD Capstone 2025

A full-stack web application for managing campus resource booking and sharing, built with Python/Flask following MVC architecture and AI-First Development practices.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   cd Campus_Resource_Hub
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - Open your browser to: `http://127.0.0.1:5000`
   - Default admin credentials:
     - **Username:** `admin` or `admin@campushub.local`
     - **Password:** `Password1`

## 📋 Core Features

### ✅ Implemented Features

1. **User Management & Authentication**
   - User registration and login with email/password
   - Password hashing using bcrypt
   - Role-based access control (Student, Staff, Admin)
   - Session management with Flask-Login

2. **Resource Listings**
   - Full CRUD operations for resources
   - File upload support for images
   - Equipment list management
   - Status workflow: draft → published → archived
   - Resource ownership tracking

3. **Search & Filter**
   - Keyword search (title, description)
   - Filter by category, location, capacity
   - Published resources only

4. **Booking & Scheduling**
   - Booking creation with conflict detection
   - Approval workflow (pending → approved/rejected)
   - Booking status management
   - Time-based conflict prevention

5. **Messaging System**
   - Threaded messaging between requester and resource owner
   - Message inbox and thread views

6. **Reviews & Ratings**
   - Post-booking review submission
   - 1-5 star ratings
   - Aggregate rating calculation
   - Review display on resource pages

7. **Admin Panel**
   - Dashboard with system statistics
   - User management
   - Resource management
   - Booking approval queue
   - Review moderation

8. **Waitlist Features**
   - Waitlist for fully booked resources
   - Waitlist management DAL

### 🚧 Optional Features (Partially Implemented)

- **Advanced Search:** Embedding-based retrieval (infrastructure ready, needs implementation)
- **Sort Options:** Recent, most booked, top rated (backend ready)
- **Calendar UI:** Visual calendar for booking (needs frontend implementation)
- **Notifications:** Simulated notification system (ready for enhancement)

## 🏗️ Architecture

### Project Structure
```
Campus_Resource_Hub/
├── app.py                 # Flask application factory
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── src/
│   ├── controllers/       # Flask route handlers (MVC Controller)
│   │   ├── auth_routes.py
│   │   ├── resource_routes.py
│   │   ├── booking_routes.py
│   │   ├── message_routes.py
│   │   ├── review_routes.py
│   │   └── admin_routes.py
│   ├── data_access/       # Data Access Layer (DAL)
│   │   ├── user_dal.py
│   │   ├── resource_dal.py
│   │   ├── booking_dal.py
│   │   ├── message_dal.py
│   │   ├── review_dal.py
│   │   └── waitlist_dal.py
│   ├── models.py          # SQLAlchemy ORM models
│   ├── forms/             # Flask-WTF form definitions
│   │   ├── auth_forms.py
│   │   └── resource_forms.py
│   ├── views/             # Jinja2 templates (MVC View)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── resources/
│   │   ├── bookings/
│   │   ├── messages/
│   │   ├── reviews/
│   │   └── admin/
│   └── static/            # Static files (CSS, JS, uploads)
│       └── uploads/        # User-uploaded images
├── tests/                 # Test suite
│   ├── unit/
│   └── ai_eval/
├── docs/                  # Documentation and context
│   └── context/
└── .prompt/               # AI development logs
```

### Database Schema

The application uses SQLite for local development with the following main tables:
- `users` - User accounts (Student, Staff, Admin)
- `resources` - Resource listings
- `bookings` - Booking requests and reservations
- `messages` - Threaded messages
- `reviews` - User reviews and ratings
- `equipment` - Equipment associated with resources
- `waitlist` - Waitlist for fully booked resources
- `admin_logs` - Administrative action logs

See `src/models.py` for complete schema definitions.

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///site.db
```

### File Uploads

- Upload folder: `src/static/uploads/`
- Max file size: 16MB
- Allowed extensions: JPG, JPEG, PNG, GIF, WEBP

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest tests/unit/test_auth.py
pytest tests/unit/test_booking_logic.py
pytest tests/unit/test_resource_dal.py
```

## 📚 API Endpoints

### Authentication
- `GET/POST /auth/register` - User registration
- `GET/POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Resources
- `GET /resources/` - List/search resources
- `GET /resources/<id>` - Resource details
- `GET/POST /resources/create` - Create resource (auth required)
- `GET/POST /resources/<id>/edit` - Edit resource (owner only)

### Bookings
- `GET/POST /bookings/create/<resource_id>` - Create booking (auth required)
- `GET /bookings/my-bookings` - User's bookings (auth required)
- `GET /bookings/approve/<id>` - Approve booking (admin/staff)
- `GET /bookings/cancel/<id>` - Cancel booking (auth required)

### Messages
- `GET /messages/inbox` - Message inbox (auth required)
- `GET/POST /messages/thread/<thread_id>` - View/send messages (auth required)

### Reviews
- `GET/POST /reviews/create/<resource_id>` - Submit review (auth required)

### Admin
- `GET /admin/dashboard` - Admin dashboard (admin only)
- `GET /admin/users` - User management (admin only)
- `GET /admin/resources` - Resource management (admin only)
- `GET /admin/reviews` - Review moderation (admin only)

## 🔐 Security Features

- **Password Hashing:** Bcrypt with salt
- **CSRF Protection:** Flask-WTF CSRF tokens on all forms
- **Input Validation:** Server-side validation for all inputs
- **File Upload Security:** Secure filename handling, type validation
- **SQL Injection Prevention:** Parameterized queries via SQLAlchemy
- **XSS Protection:** Jinja2 auto-escaping

## 🤖 AI-First Development

This project follows AI-First Development practices:

- **Context Pack Structure:** `.prompt/` and `docs/context/` folders for AI collaboration
- **AI Development Logs:** See `.prompt/dev_notes.md`
- **Golden Prompts:** See `.prompt/golden_prompts.md`
- **Context Artifacts:** Design Thinking, Product Management, and Process artifacts in `docs/context/`

## 📝 Database Migration

The database is automatically created on first run. To reset:

1. Delete `site.db` file
2. Restart the application
3. Tables will be recreated automatically

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
- Change port in `app.py`: `app.run(debug=True, port=5001)`

**Database errors:**
- Ensure write permissions in project directory
- Delete `site.db` to recreate database

**Import errors:**
- Ensure you're in the project root directory
- Run: `pip install -r requirements.txt`

**File upload errors:**
- Check `src/static/uploads/` directory exists and is writable

## 📖 Documentation

- **Feature Status:** See `FEATURE_STATUS.md`
- **Implementation Plan:** See `IMPLEMENTATION_PLAN.md`
- **Project Outline:** See `PROJECT_OUTLINE.md`

## 👥 Default Users

After first run, the following admin user is automatically created:
- **Email:** `admin@campushub.local`
- **Username:** `admin`
- **Password:** `Password1`
- **Role:** `admin`

## 🎯 Next Steps for Development

1. Implement advanced search with embeddings
2. Add calendar UI for booking visualization
3. Enhance notification system
4. Add sorting options to search
5. Implement waitlist UI and notifications
6. Add resource editing functionality
7. Enhance admin moderation tools

## 📄 License

This project is part of the AiDD 2025 Capstone Project.

## 🙏 Acknowledgments

Built following AI-First Development practices with context-aware AI collaboration.
