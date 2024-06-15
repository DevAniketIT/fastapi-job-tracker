"""
Job applications REST API router with CRUD operations.

This module provides comprehensive REST endpoints for managing job applications,
including pagination, filtering, and proper error handling.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import math

from database import get_db, DatabaseOperations, Application
from models import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStatus,
    APIResponse,
    PaginatedResponse
)

router = APIRouter()

# Helper functions
def calculate_pagination(total: int, page: int, limit: int) -> dict:
    """Calculate pagination metadata."""
    pages = math.ceil(total / limit) if total > 0 else 0
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
        "has_next": page < pages,
        "has_previous": page > 1
    }


def create_success_response(message: str, data=None) -> dict:
    """Create standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow()
    }


def application_to_response(app: Application) -> dict:
    """Convert database application to response format."""
    return {
        "id": app.id,
        "company_name": app.company_name,
        "job_title": app.job_title,
        "job_url": str(app.job_url) if app.job_url else None,
        "job_description": app.job_description,
        "location": app.location,
        "salary_min": app.salary_min,
        "salary_max": app.salary_max,
        "currency": app.currency,
        "job_type": app.job_type.value if app.job_type else None,
        "remote_type": app.remote_type.value if app.remote_type else None,
        "application_date": app.application_date.isoformat() if app.application_date else None,
        "deadline": app.deadline.isoformat() if app.deadline else None,
        "status": app.status.value,
        "priority": app.priority.value,
        "notes": app.notes,
        "referral_name": app.referral_name,
        "contact_email": app.contact_email,
        "contact_person": app.contact_person,
        "days_since_applied": app.days_since_applied,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None
    }


# API Endpoints
@router.get("/", summary="List all job applications")
async def list_applications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ApplicationStatus] = Query(None, description="Filter by status"),
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of job applications with optional filtering.
    
    **Features:**
    - Pagination support
    - Filter by application status
    - Filter by company name (partial match)
    - Returns calculated fields like days_since_applied
    """
    try:
        # Get total count for pagination
        total = DatabaseOperations.get_application_count(db)
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get applications with filtering
        applications = DatabaseOperations.get_applications(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            company_name=company_name
        )
        
        # Convert to response format
        items = [application_to_response(app) for app in applications]
        
        # Calculate pagination metadata
        pagination = calculate_pagination(total, page, limit)
        
        return {
            "items": items,
            **pagination
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving applications: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new job application")
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job application.
    
    **Required fields:**
    - company_name: Name of the company
    - job_title: Job position title
    
    **Optional fields:**
    - All other fields from the ApplicationCreate model
    """
    try:
        # Convert Pydantic model to dict, excluding None values for optional fields
        application_data = application.dict(exclude_unset=True)
        
        # Create application in database
        db_application = DatabaseOperations.create_application(
            db=db, 
            application_data=application_data
        )
        
        return create_success_response(
            message="Application created successfully",
            data=application_to_response(db_application)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating application: {str(e)}"
        )


@router.get("/{application_id}", summary="Get a specific job application")
async def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific job application by ID.
    """
    try:
        db_application = DatabaseOperations.get_application(db=db, application_id=application_id)
        
        if not db_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return create_success_response(
            message="Application retrieved successfully",
            data=application_to_response(db_application)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving application: {str(e)}"
        )


@router.put("/{application_id}", summary="Update a job application")
async def update_application(
    application_id: int,
    application: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing job application.
    
    Only provided fields will be updated. Omitted fields will remain unchanged.
    """
    try:
        # Convert to dict, excluding None values
        update_data = application.dict(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update application
        db_application = DatabaseOperations.update_application(
            db=db,
            application_id=application_id,
            update_data=update_data
        )
        
        if not db_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return create_success_response(
            message="Application updated successfully",
            data=application_to_response(db_application)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating application: {str(e)}"
        )


@router.delete("/{application_id}", summary="Delete a job application")
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job application by ID.
    """
    try:
        success = DatabaseOperations.delete_application(db=db, application_id=application_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return create_success_response(
            message="Application deleted successfully",
            data={"deleted_id": application_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting application: {str(e)}"
        )


@router.get("/stats/summary", summary="Get application statistics")
async def get_application_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics for job applications.
    """
    try:
        total_applications = DatabaseOperations.get_application_count(db)
        
        # Get applications by status
        stats = {
            "total_applications": total_applications,
            "applications_by_status": {},
            "message": "Statistics retrieved successfully"
        }
        
        # Count applications by each status
        from models import ApplicationStatus
        for status_enum in ApplicationStatus:
            count = len(DatabaseOperations.get_applications(
                db=db, 
                status=status_enum, 
                limit=1000  # Get all for counting
            ))
            stats["applications_by_status"][status_enum.value] = count
        
        return create_success_response(
            message="Statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )
