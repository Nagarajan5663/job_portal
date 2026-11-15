# 💼 Job Portal — Full-Stack Web Application

A full-stack Job Portal built with **HTML/CSS/JavaScript**, **Python FastAPI**, and **MySQL**, supporting three roles: **Job Seeker**, **Recruiter**, and **Admin**. Designed to be a clean, interview-ready reference project for a Junior Python Full-Stack Developer role.

---

## 1. Features

### Job Seeker
- Register / Login (JWT auth)
- Create & edit a profile (skills, experience, education, resume link)
- Search & filter jobs (keyword, location, job type, min salary)
- View full job details
- Apply for jobs (one application per job, with cover letter)
- Track application status (pending / accepted / rejected), withdraw pending applications

### Recruiter
- Register / Login
- Create & edit a company profile
- Post / edit / delete job listings
- View applicants per job
- Accept / reject applications

### Admin
- Login
- Dashboard with live statistics (users, jobs, applications breakdown)
- Manage users (view, enable/disable, delete — except other admins)
- Manage all jobs (view, delete)
- Manage all applications (view)

### Cross-cutting
- REST API between frontend and backend
- JWT-based authentication + role-based access control (RBAC) on every protected route
- Server-side & client-side form validation
- Centralized error handling (consistent JSON error responses, friendly banners in UI)
- Responsive, professional UI with no external CSS framework (hand-written CSS)

---

## 2. Tech Stack

| Layer      | Technology                                    |
|------------|------------------------------------------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript (fetch API)     |
| Backend    | Python 3.10+, FastAPI, SQLAlchemy ORM           |
| Database   | MySQL 8+                                        |
| Auth       | JWT (python-jose) + bcrypt password hashing     |
| API Docs   | Auto-generated via FastAPI (Swagger UI at `/docs`) |

---

## 3. Project Structure

```
job-portal/
├── backend/
│   ├── main.py                 # FastAPI app entrypoint, CORS, router registration
│   ├── database.py             # SQLAlchemy engine/session setup
│   ├── models.py                # ORM models (User, JobseekerProfile, Company, Job, Application)
│   ├── schemas.py               # Pydantic request/response schemas + validation
│   ├── auth.py                  # Password hashing, JWT creation/verification, RBAC dependency
│   ├── create_admin.py          # CLI helper to create/reset an admin account
│   ├── requirements.txt
│   ├── .env.example              # Environment variable template
│   └── routers/
│       ├── auth_routes.py       # /api/auth/register, /api/auth/login
│       ├── job_routes.py        # /api/jobs (public search/detail)
│       ├── jobseeker_routes.py  # /api/jobseeker/*  (profile, apply, applications)
│       ├── recruiter_routes.py  # /api/recruiter/*  (company, job CRUD, applicants)
│       └── admin_routes.py      # /api/admin/*      (dashboard, users, jobs, applications)
│
├── database/
│   └── schema.sql                # Full MySQL schema (tables, PKs, FKs, indexes, seed admin)
│
├── frontend/
│   ├── index.html                 # Landing page
│   ├── login.html
│   ├── register.html
│   ├── css/style.css              # Shared stylesheet
│   ├── js/
│   │   ├── api.js                 # Fetch wrapper + all API calls + auth/session helpers
│   │   └── nav.js                 # Dynamic role-based navbar
│   ├── jobseeker/
│   │   ├── jobs.html               # Search/filter/apply
│   │   ├── applications.html       # Track application status
│   │   └── profile.html
│   ├── recruiter/
│   │   ├── dashboard.html          # My jobs + view applicants + accept/reject
│   │   ├── post_job.html           # Create/edit job
│   │   └── company.html            # Company profile
│   └── admin/
│       └── dashboard.html          # Stats + manage users/jobs/applications
│
└── README.md
```

---

## 4. Database Schema (Entity-Relationship Summary)

```
users (id PK)
 ├─ 1:1 → jobseeker_profiles (user_id FK)
 ├─ 1:1 → companies           (recruiter_id FK)
 ├─ 1:N → jobs                (recruiter_id FK)
 └─ 1:N → applications        (jobseeker_id FK)

companies (id PK)
 └─ 1:N → jobs (company_id FK)

jobs (id PK)
 └─ 1:N → applications (job_id FK)

applications (id PK)
 └─ UNIQUE (job_id, jobseeker_id)   -- prevents duplicate applications
```

All foreign keys use `ON DELETE CASCADE` so deleting a user/company/job cleanly removes dependent rows. See `database/schema.sql` for the full DDL (column types, `ENUM`s, indexes).

---

## 5. Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL Server 8+ (running locally or remotely)
- A modern browser
- (Optional but recommended) [VS Code Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) or Python's built-in HTTP server, to serve the frontend

### Step 1 — Clone / unzip the project
```bash
cd job-portal
```

### Step 2 — Create the MySQL database
```bash
mysql -u root -p < database/schema.sql
```
This creates the `job_portal` database, all tables, and (attempts to) seed a default admin user. **If the seeded admin hash doesn't work on your machine's bcrypt build**, just create one via `create_admin.py` in Step 5 — this is the safer route.

### Step 3 — Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env with your MySQL credentials:
#   DB_HOST=localhost
#   DB_PORT=3306
#   DB_USER=root
#   DB_PASSWORD=your_mysql_password
#   DB_NAME=job_portal
#   SECRET_KEY=some_long_random_string
```

### Step 4 — Run the backend
```bash
uvicorn main:app --reload --port 8001
```
- API base URL: `http://127.0.0.1:8001`
- Interactive API docs (Swagger UI): `http://127.0.0.1:8001/docs`
- Tables are also auto-created on startup via SQLAlchemy (`Base.metadata.create_all`) if you skipped Step 2, but running `schema.sql` first is recommended so you can inspect the actual DDL.

### Step 5 — Create an admin account (recommended over the seed row)
```bash
python create_admin.py
# Enter name / email / password when prompted
```

### Step 6 — Run the frontend
The frontend is plain static HTML/CSS/JS — no build step required. Serve it with any static server, for example:
```bash
cd ../frontend
python -m http.server 5500
```
Then open `http://localhost:5500/index.html` in your browser.

> If your frontend runs on a different port/host, update `API_BASE_URL` in `frontend/js/api.js` to match your backend URL.

### Step 7 — Try it out
1. Register a **Recruiter** account → set up a company profile → post a job.
2. Register a **Job Seeker** account → search for the job → apply.
3. Log in as the recruiter → view applicants → accept/reject.
4. Log in as **Admin** (`create_admin.py` account) → view dashboard stats, manage users/jobs/applications.

---

## 6. Key REST API Endpoints

| Method | Endpoint                                    | Role       | Description                     |
|--------|----------------------------------------------|------------|----------------------------------|
| POST   | `/api/auth/register`                          | Public     | Register a new user              |
| POST   | `/api/auth/login`                              | Public     | Login, returns JWT                |
| GET    | `/api/jobs`                                    | Any (auth) | Search/filter jobs                |
| GET    | `/api/jobs/{id}`                               | Any (auth) | Job details                       |
| GET/PUT| `/api/jobseeker/profile`                       | Job Seeker | View/update profile               |
| POST   | `/api/jobseeker/apply/{job_id}`                | Job Seeker | Apply to a job                    |
| GET    | `/api/jobseeker/applications`                  | Job Seeker | Track my applications             |
| DELETE | `/api/jobseeker/applications/{id}`             | Job Seeker | Withdraw a pending application    |
| GET/PUT| `/api/recruiter/company`                       | Recruiter  | View/update company profile       |
| POST   | `/api/recruiter/jobs`                          | Recruiter  | Post a job                        |
| GET    | `/api/recruiter/jobs`                          | Recruiter  | List my posted jobs               |
| PUT/DELETE | `/api/recruiter/jobs/{id}`                 | Recruiter  | Edit / delete a job                |
| GET    | `/api/recruiter/jobs/{id}/applicants`          | Recruiter  | View applicants for a job         |
| PUT    | `/api/recruiter/applications/{id}/status`      | Recruiter  | Accept / reject an application    |
| GET    | `/api/admin/dashboard`                         | Admin      | Platform statistics               |
| GET    | `/api/admin/users`                             | Admin      | List/filter all users             |
| PUT    | `/api/admin/users/{id}/toggle-active`          | Admin      | Enable/disable a user             |
| DELETE | `/api/admin/users/{id}`                        | Admin      | Delete a user                     |
| GET/DELETE | `/api/admin/jobs`, `/api/admin/jobs/{id}`  | Admin      | View/delete any job                |
| GET    | `/api/admin/applications`                      | Admin      | View all applications              |

Full interactive documentation with request/response schemas is available at `/docs` once the backend is running.

---

## 7. Authentication & Security Notes
- Passwords are hashed with **bcrypt** (never stored in plain text).
- Login issues a **JWT** (`sub` = user id, `role` = user role), expiring after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 120).
- Every protected route uses a FastAPI dependency (`require_roles([...])`) to enforce **role-based access control** — e.g. only recruiters can post jobs, only the owning recruiter can edit/delete their own jobs, only admins can hit `/api/admin/*`.
- The frontend stores the JWT in `localStorage` and attaches it as a `Bearer` token on every request; a 401 response auto-redirects to the login page.
- Ownership checks (e.g. a recruiter can only edit *their own* jobs, view applicants for *their own* jobs) are enforced server-side, not just hidden in the UI.

---

## 8. Notes for Interview / Extension Ideas
This project intentionally keeps things simple and readable, which is ideal for explaining design decisions in an interview:
- **Why FastAPI + SQLAlchemy?** Type-safe request/response models via Pydantic, automatic OpenAPI docs, and a familiar ORM.
- **Why JWT instead of sessions?** Stateless auth that scales well and works cleanly with a separate static frontend.
- **Possible extensions:** file upload for resumes/logos (currently URL-based), pagination on job search, email notifications on status change, refresh tokens, Docker Compose for one-command setup, unit tests with `pytest` + `TestClient`.

---

## 9. Quick Command Reference

```bash
# Database
mysql -u root -p < database/schema.sql

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit with your DB credentials
python create_admin.py
uvicorn main:app --reload --port 8001

# Frontend
cd frontend
python -m http.server 5500
```
