"""
Pydantic models for job application tracking API.

This module contains all the data models used throughout the API for
request/response validation, database schemas, and data transfer objects.
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import re


# Enums for job application status and types
class ApplicationStatus(str, Enum):
    """Job application status options."""
    APPLIED = "applied"
    REVIEWING = "reviewing"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_INTERVIEW = "technical_interview"
    ONSITE_INTERVIEW = "onsite_interview"
    FINAL_ROUND = "final_round"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"


class JobType(str, Enum):
    """Job type options."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


class RemoteType(str, Enum):
    """Remote work options."""
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"


class Priority(str, Enum):
    """Application priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Base models
class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApplicationBase(BaseModel):
    """Base model for job applications with core fields."""
    company_name: str = Field(..., min_length=1, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=200)
    job_url: Optional[HttpUrl] = None
    job_description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    job_type: Optional[JobType] = None
    remote_type: Optional[RemoteType] = None
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    notes: Optional[str] = Field(None, max_length=2000)
    referral_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_person: Optional[str] = Field(None, max_length=100)

    @field_validator('company_name', 'job_title')
    @classmethod
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or just whitespace')
        return v.strip()

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Currency must be a 3-letter code (e.g., USD, EUR)')
        return v.upper()

    @model_validator(mode='after')
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_max <= self.salary_min:
            raise ValueError('Maximum salary must be greater than minimum salary')
        return self


class ApplicationCreate(ApplicationBase):
    """Model for creating new job applications."""
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)


class ApplicationUpdate(BaseModel):
    """Model for updating job applications with optional fields."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    job_url: Optional[HttpUrl] = None
    job_description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    job_type: Optional[JobType] = None
    remote_type: Optional[RemoteType] = None
    application_date: Optional[date] = None
    deadline: Optional[date] = None
    status: Optional[ApplicationStatus] = None
    priority: Optional[Priority] = None
    notes: Optional[str] = Field(None, max_length=2000)
    referral_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_person: Optional[str] = Field(None, max_length=100)

    @field_validator('company_name', 'job_title')
    @classmethod
    def validate_required_fields(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or just whitespace')
        return v.strip() if v else v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if v is not None and not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Currency must be a 3-letter code (e.g., USD, EUR)')
        return v.upper() if v else v


class ApplicationResponse(ApplicationBase, TimestampMixin):
    """Model for job application API responses with ID and timestamps."""
    id: int
    status: ApplicationStatus
    days_since_applied: Optional[int] = None

    class Config:
        from_attributes = True


# Generic API response models
class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    message: str
    errors: List[str]
    error_code: Optional[str] = None
    timestamp: datetime


# Pagination models
class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List[Any]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


# User models for authentication
class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Model for user API responses."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model."""
    email: Optional[str] = None
