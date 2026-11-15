"""
SQLAlchemy ORM models -> mirror database/schema.sql
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP,
    Enum, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class RoleEnum(str, enum.Enum):
    jobseeker = "jobseeker"
    recruiter = "recruiter"
    admin = "admin"


class JobTypeEnum(str, enum.Enum):
    full_time = "Full-time"
    part_time = "Part-time"
    internship = "Internship"
    contract = "Contract"
    remote = "Remote"


class JobStatusEnum(str, enum.Enum):
    open = "open"
    closed = "closed"


class AppStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.jobseeker)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    jobseeker_profile = relationship(
        "JobseekerProfile", back_populates="user", uselist=False, cascade="all,delete"
    )
    company = relationship(
        "Company", back_populates="recruiter", uselist=False, cascade="all,delete"
    )
    jobs_posted = relationship("Job", back_populates="recruiter", cascade="all,delete")
    applications = relationship(
        "Application", back_populates="jobseeker", cascade="all,delete"
    )


class JobseekerProfile(Base):
    __tablename__ = "jobseeker_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone = Column(String(20))
    location = Column(String(150))
    skills = Column(Text)
    experience = Column(Text)
    education = Column(Text)
    resume_url = Column(String(255))

    user = relationship("User", back_populates="jobseeker_profile")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(150), nullable=False)
    description = Column(Text)
    website = Column(String(255))
    location = Column(String(150))
    logo_url = Column(String(255))

    recruiter = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company", cascade="all,delete")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    location = Column(String(150), index=True)
    job_type = Column(
        Enum(JobTypeEnum, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=JobTypeEnum.full_time,
    )
    category = Column(String(100), index=True)
    salary_min = Column(Integer, default=0)
    salary_max = Column(Integer, default=0)
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.open)
    created_at = Column(TIMESTAMP, server_default=func.now())

    recruiter = relationship("User", back_populates="jobs_posted")
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all,delete")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "jobseeker_id", name="uq_job_jobseeker"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    jobseeker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cover_letter = Column(Text)
    resume_url = Column(String(255))
    status = Column(Enum(AppStatusEnum), default=AppStatusEnum.pending)
    applied_at = Column(TIMESTAMP, server_default=func.now())

    job = relationship("Job", back_populates="applications")
    jobseeker = relationship("User", back_populates="applications")
