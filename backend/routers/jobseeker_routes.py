"""
Job Seeker routes: profile management, applying for jobs, tracking applications.
Protected: role must be 'jobseeker'.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import get_current_user, require_roles

router = APIRouter(prefix="/api/jobseeker", tags=["Job Seeker"])
jobseeker_only = require_roles(["jobseeker"])


@router.get("/profile", response_model=schemas.JobseekerProfileOut)
def get_profile(db: Session = Depends(get_db), current_user: models.User = Depends(jobseeker_only)):
    profile = db.query(models.JobseekerProfile).filter(
        models.JobseekerProfile.user_id == current_user.id
    ).first()
    if not profile:
        profile = models.JobseekerProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile", response_model=schemas.JobseekerProfileOut)
def update_profile(
    profile_in: schemas.JobseekerProfileIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(jobseeker_only),
):
    profile = db.query(models.JobseekerProfile).filter(
        models.JobseekerProfile.user_id == current_user.id
    ).first()
    if not profile:
        profile = models.JobseekerProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/apply/{job_id}", response_model=schemas.ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    application_in: schemas.ApplicationIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(jobseeker_only),
):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != models.JobStatusEnum.open:
        raise HTTPException(status_code=400, detail="This job is no longer accepting applications")

    existing = db.query(models.Application).filter(
        models.Application.job_id == job_id,
        models.Application.jobseeker_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this job")

    application = models.Application(
        job_id=job_id,
        jobseeker_id=current_user.id,
        cover_letter=application_in.cover_letter,
        resume_url=application_in.resume_url,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    out = schemas.ApplicationOut.model_validate(application)
    out.job_title = job.title
    return out


@router.get("/applications", response_model=List[schemas.ApplicationOut])
def my_applications(db: Session = Depends(get_db), current_user: models.User = Depends(jobseeker_only)):
    apps = db.query(models.Application).filter(
        models.Application.jobseeker_id == current_user.id
    ).order_by(models.Application.applied_at.desc()).all()

    results = []
    for a in apps:
        out = schemas.ApplicationOut.model_validate(a)
        out.job_title = a.job.title if a.job else None
        results.append(out)
    return results


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(jobseeker_only),
):
    app_obj = db.query(models.Application).filter(
        models.Application.id == application_id,
        models.Application.jobseeker_id == current_user.id,
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_obj)
    db.commit()
