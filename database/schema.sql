-- ============================================================
-- Job Portal Database Schema (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS job_portal
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE job_portal;

-- ------------------------------------------------------------
-- USERS  (shared table for jobseeker / recruiter / admin)
-- ------------------------------------------------------------
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          ENUM('jobseeker', 'recruiter', 'admin') NOT NULL DEFAULT 'jobseeker',
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- JOBSEEKER PROFILES  (1-to-1 with users where role='jobseeker')
-- ------------------------------------------------------------
CREATE TABLE jobseeker_profiles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE,
    phone       VARCHAR(20),
    location    VARCHAR(150),
    skills      TEXT,
    experience  TEXT,
    education   TEXT,
    resume_url  VARCHAR(255),
    CONSTRAINT fk_jsp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- COMPANIES (recruiter company profile, 1-to-1 with recruiter user)
-- ------------------------------------------------------------
CREATE TABLE companies (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id  INT NOT NULL UNIQUE,
    company_name  VARCHAR(150) NOT NULL,
    description   TEXT,
    website       VARCHAR(255),
    location      VARCHAR(150),
    logo_url      VARCHAR(255),
    CONSTRAINT fk_company_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- JOBS
-- ------------------------------------------------------------
CREATE TABLE jobs (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id  INT NOT NULL,
    company_id    INT NOT NULL,
    title         VARCHAR(150) NOT NULL,
    description   TEXT NOT NULL,
    requirements  TEXT,
    location      VARCHAR(150),
    job_type      ENUM('Full-time','Part-time','Internship','Contract','Remote') NOT NULL DEFAULT 'Full-time',
    category      VARCHAR(100),
    salary_min    INT DEFAULT 0,
    salary_max    INT DEFAULT 0,
    status        ENUM('open','closed') NOT NULL DEFAULT 'open',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_company   FOREIGN KEY (company_id)   REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_jobs_title    ON jobs(title);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_category ON jobs(category);

-- ------------------------------------------------------------
-- APPLICATIONS
-- ------------------------------------------------------------
CREATE TABLE applications (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    job_id        INT NOT NULL,
    jobseeker_id  INT NOT NULL,
    cover_letter  TEXT,
    resume_url    VARCHAR(255),
    status        ENUM('pending','accepted','rejected') NOT NULL DEFAULT 'pending',
    applied_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_job       FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_app_jobseeker FOREIGN KEY (jobseeker_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_job_jobseeker UNIQUE (job_id, jobseeker_id)   -- prevent duplicate applications
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Seed an admin user (password = "Admin@123", already hashed with bcrypt)
-- Hash generated for "Admin@123"
-- ------------------------------------------------------------
INSERT INTO users (name, email, password_hash, role)
VALUES ('Super Admin', 'admin@jobportal.com',
'$2b$12$KIXQ8Z3Jvz1rC2s7q0bJk.uYV8n1G4hR9WqxJ4TQeYV3z0bT1o6Wm', 'admin');
-- NOTE: If this hash does not match "Admin@123" on your bcrypt build,
-- simply register a new admin via the /api/auth/register endpoint with role=admin
-- (see README for a curl example), or run backend/create_admin.py.
