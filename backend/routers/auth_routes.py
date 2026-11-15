"""
Authentication routes: register & login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-create empty related profile rows so later PUT calls just update them
    if user.role == models.RoleEnum.jobseeker:
        db.add(models.JobseekerProfile(user_id=user.id))
        db.commit()
    elif user.role == models.RoleEnum.recruiter:
        db.add(models.Company(recruiter_id=user.id, company_name=f"{user.name}'s Company"))
        db.commit()

    return user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account has been deactivated by admin")

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return schemas.Token(
        access_token=token, role=user.role.value, user_id=user.id, name=user.name
    )
