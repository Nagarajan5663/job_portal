"""
Recruiter routes: company profile, job CRUD, applicant management.
Protected: role must be 'recruiter'.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import require_roles

router = APIRouter(prefix="/api/recruiter", tags=["Recruiter"])
recruiter_only = require_roles(["recruiter"])


def _get_or_create_company(db: Session, recruiter_id: int) -> models.Company:
    company = db.query(models.Company).filter(models.Company.recruiter_id == recruiter_id).first()
    if not company:
        company = models.Company(recruiter_id=recruiter_id, company_name="My Company")
        db.add(company)
        db.commit()
        db.refresh(company)
    return company


# ---------- Company profile ----------
@router.get("/company", response_model=schemas.CompanyOut)
def get_company(db: Session = Depends(get_db), current_user: models.User = Depends(recruiter_only)):
    return _get_or_create_company(db, current_user.id)


@router.put("/company", response_model=schemas.CompanyOut)
def update_company(
    company_in: schemas.CompanyIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    company = _get_or_create_company(db, current_user.id)
    for field, value in company_in.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


# ---------- Job CRUD ----------
@router.post("/jobs", response_model=schemas.JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: schemas.JobIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    company = _get_or_create_company(db, current_user.id)
    job = models.Job(recruiter_id=current_user.id, company_id=company.id, **job_in.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    out = schemas.JobOut.model_validate(job)
    out.company_name = company.company_name
    return out


@router.get("/jobs", response_model=List[schemas.JobOut])
def my_jobs(db: Session = Depends(get_db), current_user: models.User = Depends(recruiter_only)):
    jobs = db.query(models.Job).filter(
        models.Job.recruiter_id == current_user.id
    ).order_by(models.Job.created_at.desc()).all()
    results = []
    for j in jobs:
        out = schemas.JobOut.model_validate(j)
        out.company_name = j.company.company_name if j.company else None
        results.append(out)
    return results


def _get_own_job(db: Session, job_id: int, recruiter_id: int) -> models.Job:
    job = db.query(models.Job).filter(
        models.Job.id == job_id, models.Job.recruiter_id == recruiter_id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or you do not own this job")
    return job


@router.put("/jobs/{job_id}", response_model=schemas.JobOut)
def update_job(
    job_id: int,
    job_in: schemas.JobUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    job = _get_own_job(db, job_id, current_user.id)
    for field, value in job_in.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    out = schemas.JobOut.model_validate(job)
    out.company_name = job.company.company_name if job.company else None
    return out


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    job = _get_own_job(db, job_id, current_user.id)
    db.delete(job)
    db.commit()


# ---------- Applicants ----------
@router.get("/jobs/{job_id}/applicants", response_model=List[schemas.ApplicationOut])
def view_applicants(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    _get_own_job(db, job_id, current_user.id)  # ownership check
    apps = db.query(models.Application).filter(models.Application.job_id == job_id).all()

    results = []
    for a in apps:
        out = schemas.ApplicationOut.model_validate(a)
        out.applicant_name = a.jobseeker.name if a.jobseeker else None
        out.applicant_email = a.jobseeker.email if a.jobseeker else None
        results.append(out)
    return results


@router.put("/applications/{application_id}/status", response_model=schemas.ApplicationOut)
def update_application_status(
    application_id: int,
    status_in: schemas.ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(recruiter_only),
):
    application = db.query(models.Application).join(models.Job).filter(
        models.Application.id == application_id,
        models.Job.recruiter_id == current_user.id,
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status_in.status
    db.commit()
    db.refresh(application)
    out = schemas.ApplicationOut.model_validate(application)
    out.applicant_name = application.jobseeker.name
    out.job_title = application.job.title
    return out
