"""
One-off helper script to create (or reset) an admin account.
Run:  python create_admin.py
"""
from getpass import getpass
from database import SessionLocal, engine, Base
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    try:
        name = input("Admin name: ").strip() or "Super Admin"
        email = input("Admin email: ").strip()
        password = getpass("Admin password: ").strip()

        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            existing.password_hash = hash_password(password)
            existing.role = models.RoleEnum.admin
            existing.is_active = True
            db.commit()
            print(f"Existing user updated to admin: {email}")
        else:
            admin = models.User(
                name=name, email=email, password_hash=hash_password(password), role=models.RoleEnum.admin
            )
            db.add(admin)
            db.commit()
            print(f"Admin account created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
