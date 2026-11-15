"""
Pydantic schemas used for request validation and response serialization.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ---------- Enums ----------
class RoleEnum(str, Enum):
    jobseeker = "jobseeker"
    recruiter = "recruiter"
    admin = "admin"


class JobTypeEnum(str, Enum):
    full_time = "Full-time"
    part_time = "Part-time"
    internship = "Internship"
    contract = "Contract"
    remote = "Remote"


class JobStatusEnum(str, Enum):
    open = "open"
    closed = "closed"


class AppStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# ---------- Auth ----------
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    role: RoleEnum = RoleEnum.jobseeker

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Jobseeker profile ----------
class JobseekerProfileIn(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None


class JobseekerProfileOut(JobseekerProfileIn):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ---------- Company ----------
class CompanyIn(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyOut(CompanyIn):
    id: int
    recruiter_id: int

    class Config:
        from_attributes = True


# ---------- Jobs ----------
class JobIn(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    location: Optional[str] = None
    job_type: JobTypeEnum = JobTypeEnum.full_time
    category: Optional[str] = None
    salary_min: int = 0
    salary_max: int = 0

    @field_validator("salary_max")
    @classmethod
    def salary_range_valid(cls, v, info):
        salary_min = info.data.get("salary_min", 0)
        if v and salary_min and v < salary_min:
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return v


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobTypeEnum] = None
    category: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: Optional[JobStatusEnum] = None


class JobOut(BaseModel):
    id: int
    recruiter_id: int
    company_id: int
    title: str
    description: str
    requirements: Optional[str]
    location: Optional[str]
    job_type: JobTypeEnum
    category: Optional[str]
    salary_min: int
    salary_max: int
    status: JobStatusEnum
    created_at: datetime
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Applications ----------
class ApplicationIn(BaseModel):
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: AppStatusEnum


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    jobseeker_id: int
    cover_letter: Optional[str]
    resume_url: Optional[str]
    status: AppStatusEnum
    applied_at: datetime
    job_title: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Admin dashboard ----------
class DashboardStats(BaseModel):
    total_users: int
    total_jobseekers: int
    total_recruiters: int
    total_jobs: int
    open_jobs: int
    total_applications: int
    pending_applications: int
    accepted_applications: int
    rejected_applications: int
