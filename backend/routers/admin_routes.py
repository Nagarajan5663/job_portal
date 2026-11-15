"""
Admin routes: manage users, recruiters, jobs, applications + dashboard stats.
Protected: role must be 'admin'.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin"])
admin_only = require_roles(["admin"])


# ---------- Dashboard ----------
@router.get("/dashboard", response_model=schemas.DashboardStats)
def dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    total_users = db.query(models.User).count()
    total_jobseekers = db.query(models.User).filter(models.User.role == "jobseeker").count()
    total_recruiters = db.query(models.User).filter(models.User.role == "recruiter").count()
    total_jobs = db.query(models.Job).count()
    open_jobs = db.query(models.Job).filter(models.Job.status == "open").count()
    total_applications = db.query(models.Application).count()
    pending = db.query(models.Application).filter(models.Application.status == "pending").count()
    accepted = db.query(models.Application).filter(models.Application.status == "accepted").count()
    rejected = db.query(models.Application).filter(models.Application.status == "rejected").count()

    return schemas.DashboardStats(
        total_users=total_users,
        total_jobseekers=total_jobseekers,
        total_recruiters=total_recruiters,
        total_jobs=total_jobs,
        open_jobs=open_jobs,
        total_applications=total_applications,
        pending_applications=pending,
        accepted_applications=accepted,
        rejected_applications=rejected,
    )


# ---------- User management ----------
@router.get("/users", response_model=List[schemas.UserOut])
def list_users(role: str | None = None, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.order_by(models.User.created_at.desc()).all()


@router.put("/users/{user_id}/toggle-active", response_model=schemas.UserOut)
def toggle_user_active(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail="Cannot deactivate an admin account")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail="Cannot delete an admin account")
    db.delete(user)
    db.commit()


# ---------- Job management ----------
@router.get("/jobs", response_model=List[schemas.JobOut])
def list_all_jobs(db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    jobs = db.query(models.Job).order_by(models.Job.created_at.desc()).all()
    results = []
    for j in jobs:
        out = schemas.JobOut.model_validate(j)
        out.company_name = j.company.company_name if j.company else None
        results.append(out)
    return results


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_job(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()


# ---------- Application management ----------
@router.get("/applications", response_model=List[schemas.ApplicationOut])
def list_all_applications(db: Session = Depends(get_db), current_user: models.User = Depends(admin_only)):
    apps = db.query(models.Application).order_by(models.Application.applied_at.desc()).all()
    results = []
    for a in apps:
        out = schemas.ApplicationOut.model_validate(a)
        out.job_title = a.job.title if a.job else None
        out.applicant_name = a.jobseeker.name if a.jobseeker else None
        out.applicant_email = a.jobseeker.email if a.jobseeker else None
        results.append(out)
    return results
