"""
Database configuration and ORM models for job application tracking.

This module handles database connection, table definitions, and basic operations
using SQLAlchemy with PostgreSQL support for Render deployment.
"""

import os
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean, 
    Enum as SQLEnum, create_engine, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from enum import Enum

from models import ApplicationStatus, JobType, RemoteType, Priority

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost/jobtracker"
)

# Handle Heroku/Render PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine with different settings for SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass


# Database Models
class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    applications = relationship("Application", back_populates="owner")


class Application(Base):
    """Job application model."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for now
    
    # Basic job information
    company_name = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False, index=True)
    job_url = Column(Text)
    job_description = Column(Text)
    location = Column(String(200))
    
    # Salary information
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(3), default="USD")
    
    # Job details
    job_type = Column(SQLEnum(JobType), nullable=True)
    remote_type = Column(SQLEnum(RemoteType), nullable=True)
    
    # Application tracking
    application_date = Column(Date)
    deadline = Column(Date)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, index=True)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM, index=True)
    
    # Additional information
    notes = Column(Text)
    referral_name = Column(String(100))
    contact_email = Column(String(255))
    contact_person = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="applications")

    @property
    def days_since_applied(self) -> Optional[int]:
        """Calculate days since application was submitted."""
        if self.application_date:
            delta = date.today() - self.application_date
            return delta.days
        return None


# Database dependency
def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
async def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


# Database operations
class DatabaseOperations:
    """Database operations for job applications."""
    
    @staticmethod
    def create_application(db: Session, application_data: dict, user_id: Optional[int] = None) -> Application:
        """Create a new job application."""
        db_application = Application(**application_data, user_id=user_id)
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application
    
    @staticmethod
    def get_application(db: Session, application_id: int, user_id: Optional[int] = None) -> Optional[Application]:
        """Get a specific job application by ID."""
        query = db.query(Application).filter(Application.id == application_id)
        if user_id:
            query = query.filter(Application.user_id == user_id)
        return query.first()
    
    @staticmethod
    def get_applications(
        db: Session, 
        user_id: Optional[int] = None, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ApplicationStatus] = None,
        company_name: Optional[str] = None
    ) -> list[Application]:
        """Get job applications with optional filtering."""
        query = db.query(Application)
        
        if user_id:
            query = query.filter(Application.user_id == user_id)
        
        if status:
            query = query.filter(Application.status == status)
        
        if company_name:
            query = query.filter(Application.company_name.ilike(f"%{company_name}%"))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_application(
        db: Session, 
        application_id: int, 
        update_data: dict,
        user_id: Optional[int] = None
    ) -> Optional[Application]:
        """Update a job application."""
        query = db.query(Application).filter(Application.id == application_id)
        if user_id:
            query = query.filter(Application.user_id == user_id)
        
        db_application = query.first()
        if not db_application:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(db_application, key, value)
        
        db.commit()
        db.refresh(db_application)
        return db_application
    
    @staticmethod
    def delete_application(db: Session, application_id: int, user_id: Optional[int] = None) -> bool:
        """Delete a job application."""
        query = db.query(Application).filter(Application.id == application_id)
        if user_id:
            query = query.filter(Application.user_id == user_id)
        
        db_application = query.first()
        if not db_application:
            return False
        
        db.delete(db_application)
        db.commit()
        return True
    
    @staticmethod
    def get_application_count(db: Session, user_id: Optional[int] = None) -> int:
        """Get total count of applications."""
        query = db.query(Application)
        if user_id:
            query = query.filter(Application.user_id == user_id)
        return query.count()


# User operations
class UserOperations:
    """Database operations for users."""
    
    @staticmethod
    def create_user(db: Session, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        db_user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
