"""
Public job browsing routes (available to any authenticated user,
mainly used by job seekers, but recruiters/admin can view too).
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["Jobs (Public/Search)"])


def _to_job_out(job: models.Job) -> schemas.JobOut:
    data = schemas.JobOut.model_validate(job)
    data.company_name = job.company.company_name if job.company else None
    return data


@router.get("", response_model=List[schemas.JobOut])
def list_jobs(
    keyword: Optional[str] = Query(None, description="Search in title/description"),
    location: Optional[str] = None,
    category: Optional[str] = None,
    job_type: Optional[str] = None,
    min_salary: Optional[int] = None,
    status_filter: Optional[str] = Query("open", alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Job)

    if status_filter:
        query = query.filter(models.Job.status == status_filter)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(models.Job.title.ilike(like), models.Job.description.ilike(like)))
    if location:
        query = query.filter(models.Job.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(models.Job.category.ilike(f"%{category}%"))
    if job_type:
        query = query.filter(models.Job.job_type == job_type)
    if min_salary:
        query = query.filter(models.Job.salary_max >= min_salary)

    jobs = query.order_by(models.Job.created_at.desc()).all()
    return [_to_job_out(j) for j in jobs]


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_job_out(job)
