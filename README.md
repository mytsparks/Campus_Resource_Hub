# Campus Resource Hub - AiDD Capstone 2025

A full-stack web application for managing campus resource booking and sharing, built with Python/Flask following MVC architecture and AI-First Development practices.

## Cloud Deployment

This app is also deployed on Google Cloud Platform, with a Postgres database hosted on SupaBase.

https://campus-resource-hub-449695188584.europe-west1.run.app/

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Campus_Resource_Hub
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables (Optional for local development):**
   
   For basic local development, the app will work with default settings (SQLite database). However, if you want to:
   - Use AI-powered summary features (requires LLM API key)
   - Use PostgreSQL instead of SQLite
   - Configure Google Cloud Storage for file uploads
   
   Copy the example environment file and update it:
   ```bash
   cp env.example .env
   ```
   
   Then edit `.env` and set your values:
   - `SECRET_KEY`: Generate a secure random key (optional for local dev, has default)
   - `DATABASE_URL`: PostgreSQL connection string (optional, defaults to SQLite)
   - `LLM_API_KEY`: Required for AI summary features (get from Google Gemini, OpenAI, or Anthropic)
   - `LLM_PROVIDER`: LLM provider to use (defaults to 'gemini')
   - `USE_GCS`: Set to 'true' to use Google Cloud Storage (defaults to 'false' for local filesystem)
   
   **Note:** The `.env` file is gitignored and will not be committed to the repository.

4. **Run the application:**
   ```bash
   python application.py
   ```

5. **Access the application:**
   - Open your browser to: `http://127.0.0.1:5000`
   - Default admin credentials:
     - **Email:** `admin@campushub.local`
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

### ✅ AI Features

9. **Auto-Summary Reporter**
   - Weekly summary generation with AI-powered insights
   - Top 5 most reserved resources analysis
   - Booking trends and approval rate statistics
   - User activity and engagement metrics
   - Category breakdown and recommendations
   - Supports local LLMs (Ollama) and API-based models (OpenAI, Anthropic)
   - Data-driven summaries (no fabricated content)

### 🚧 Optional Features (Partially Implemented)

- **Advanced Search:** Embedding-based retrieval (infrastructure ready, needs implementation)
- **Sort Options:** Recent, most booked, top rated (backend ready)
- **Calendar UI:** Visual calendar for booking (needs frontend implementation)
- **Notifications:** Simulated notification system (ready for enhancement)

## 🏗️ Architecture

### Project Structure
```
Campus_Resource_Hub/
├── application.py         # Flask application entry point
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

### Environment Variables

The application works with default settings for local development, but you can customize behavior using environment variables.

#### Quick Setup

1. **Copy the example file:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your values** (see below for what each variable does)

#### Available Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | Auto-generated | Flask secret key for sessions (use a secure random string in production) |
| `DATABASE_URL` | No | `sqlite:///site.db` | Database connection string. Use PostgreSQL format for production: `postgresql://user:pass@host:port/dbname` |
| `LLM_PROVIDER` | No | `gemini` | LLM provider: `gemini`, `ollama`, `openai`, or `anthropic` |
| `LLM_MODEL` | No | `gemini-2.0-flash` | Model name (varies by provider) |
| `LLM_API_KEY` | Yes* | None | API key for LLM provider (*required for AI summary features) |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Base URL for Ollama (if using local LLM) |
| `USE_GCS` | No | `false` | Set to `true` to use Google Cloud Storage for file uploads |
| `GCS_BUCKET_NAME` | Yes** | None | GCS bucket name (**required if `USE_GCS=true`) |
| `GCS_PROJECT_ID` | Yes** | None | GCP project ID (**required if `USE_GCS=true`) |
| `FLASK_DEBUG` | No | `False` | Enable Flask debug mode (set to `True` for development) |

#### Local Development (Minimal Setup)

For basic local development, you don't need a `.env` file. The app will:
- Use SQLite database (`instance/site.db`)
- Use local filesystem for uploads (`src/static/uploads/`)
- Work without AI features (summary generation will be disabled)

#### Production Setup

For production deployment (GCP, Heroku, etc.), set these in your platform's environment variables:
- `SECRET_KEY`: Generate a secure random key
- `DATABASE_URL`: PostgreSQL connection string
- `LLM_API_KEY`: Your LLM provider API key (if using AI features)
- `USE_GCS`: Set to `true` for cloud storage
- `GCS_BUCKET_NAME` and `GCS_PROJECT_ID`: If using GCS

### File Uploads

**Local Development:**
- Upload folder: `src/static/uploads/`
- Files stored on local filesystem

**Production (with GCS):**
- Files stored in Google Cloud Storage bucket
- Public URLs generated automatically
- Set `USE_GCS=true` and configure `GCS_BUCKET_NAME` and `GCS_PROJECT_ID`

**Settings:**
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

### Model Context Protocol (MCP) Integration

The application includes an **MCP server** (`mcp_server.py`) that enables AI agents to safely query and inspect the database in read-only mode. This enables features such as:

- **Intelligent Search**: AI-powered resource discovery based on database content
- **Auto-summaries**: Generate summaries of resources, bookings, and user activity
- **Context-aware Assistance**: AI help based on actual application state
- **Data Analysis**: Generate reports and insights from database content

#### MCP Server Features

- **Read-only access**: Only SELECT queries allowed (no modifications)
- **SQL injection protection**: Parameterized queries required
- **Security**: Dangerous SQL keywords blocked
- **Structured tools**: Pre-built tools for common queries

#### Available MCP Tools

1. `query_database` - Execute custom SELECT queries
2. `get_table_schema` - Get schema information for tables
3. `list_tables` - List all database tables
4. `get_resource_summary` - Get comprehensive resource summaries
5. `search_resources` - Search resources by keyword, category, or location

#### Setting Up MCP

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If the `mcp` package is not available on PyPI, install from the official repository:
   ```bash
   pip install git+https://github.com/modelcontextprotocol/python-sdk.git
   ```

2. **Configure MCP client** (example for Claude Desktop):
   ```json
   {
     "mcpServers": {
       "campus-resource-hub": {
         "command": "python",
         "args": ["/absolute/path/to/Campus_Resource_Hub/mcp_server.py"]
       }
     }
   }
   ```

3. **Use with AI agents:**
   - The MCP server communicates via stdio
   - Compatible with MCP-compatible AI clients
   - See `.prompt/dev_notes.md` for detailed usage examples

#### Security

- All database queries are **read-only** (SELECT only)
- SQL injection protection via parameterized queries
- Dangerous SQL keywords (DROP, DELETE, UPDATE, etc.) are blocked
- Database connection uses SQLite URI mode with read-only flag

For detailed MCP documentation, see `.prompt/dev_notes.md`.

## 📝 Database Migration

The database is automatically created on first run. To reset:

1. Delete `site.db` file
2. Restart the application
3. Tables will be recreated automatically

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
- Change port in `application.py`: `application.run(debug=True, port=5001)`

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

## 🤖 AI Features Configuration

### Auto-Summary Reporter

The application includes an AI-powered summary generator that creates weekly reports based on actual database data.

#### LLM Configuration

The application uses **Google Gemini** by default for AI-powered summaries. Configure via environment variables:

**For Google Gemini (Default):**
```bash
export LLM_PROVIDER=gemini
export LLM_MODEL=gemini-2.0-flash
export LLM_API_KEY=your-api-key-here
```

**For Ollama (Local LLM):**
```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

**For OpenAI:**
```bash
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4
export LLM_API_KEY=your-api-key-here
```

**For Anthropic Claude:**
```bash
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-sonnet-20240229
export LLM_API_KEY=your-api-key-here
```

**Important:** Do not hardcode API keys. Set `LLM_API_KEY` via environment variables or a local `.env` file. See `env.example` for a template. In production (Railway/Render/Heroku), set it in the platform’s environment settings.

#### Using the Summary Generator

1. **Access from Admin Dashboard:**
   - Log in as admin or staff
   - Navigate to Admin Dashboard
   - Click "Generate Summary" button

2. **Features:**
   - Top 5 most reserved resources
   - Booking statistics (approved, pending, rejected)
   - User activity metrics
   - Category breakdown
   - AI-generated insights and recommendations

3. **Data Integrity:**
   - All summaries are based on actual database queries
   - No fabricated or hallucinated data
   - Real-time statistics from the past 7 days

#### Setting Up Ollama (Local LLM)

1. **Install Ollama:**
   ```bash
   # Visit https://ollama.ai for installation instructions
   # Or use: curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull a Model:**
   ```bash
   ollama pull llama3.2
   # Or: ollama pull mistral
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **Configure Environment:**
   ```bash
   export LLM_PROVIDER=ollama
   export LLM_MODEL=llama3.2
   ```

## 🎯 Next Steps for Development

1. Implement advanced search with embeddings
2. Add calendar UI for booking visualization
3. Enhance notification system
4. Add sorting options to search
5. Implement waitlist UI and notifications
6. Add resource editing functionality
7. Enhance admin moderation tools
8. Add scheduled summary generation (cron jobs)

## 📄 License

This project is part of the AiDD 2025 Capstone Project.

## 🙏 Acknowledgments

Built following AI-First Development practices with context-aware AI collaboration.
