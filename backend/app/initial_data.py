import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Initialize the database with initial data."""
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    
    # Create first superuser if it doesn't exist
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user_in = {
            "email": settings.FIRST_SUPERUSER,
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_superuser": True,
            "is_active": True,
        }
        user = User(
            email=user_in["email"],
            username=user_in["username"],
            hashed_password=get_password_hash(user_in["password"]),
            is_superuser=user_in["is_superuser"],
            is_active=user_in["is_active"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created first superuser: {user.email}")
    else:
        logger.info(f"Superuser already exists: {user.email}")

def init() -> None:
    """Initialize the database."""
    logger.info("Creating initial data")
    db = SessionLocal()
    init_db(db)
    logger.info("Initial data created")

if __name__ == "__main__":
    init()
