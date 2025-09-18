"""
Analytics and statistics endpoints with role-based access control.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.db.db import (
    get_db, Business, AnalyticsCRUD, UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    BusinessAnalytics, DateRangeStats, User as UserSchema
)
from app.api.v1.auth import get_current_user
from app.services_directory.cache_service import cached, cache_utils

router = APIRouter()

def check_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify business."""
    if required_roles is None:
        required_roles = [UserBusinessRole.OWNER, UserBusinessRole.MANAGER]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, business_id, required_roles)

def require_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access business."""
    if not check_business_permission(business_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this business"
        )

# ========================================
# ANALYTICS ENDPOINTS
# ========================================

@router.get("/business/{business_id}", response_model=BusinessAnalytics)
@cached(ttl=300, key_prefix="analytics")  # Cache for 5 minutes
async def get_business_analytics(
    business_id: UUID,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get analytics for a specific business (business owners/managers only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    # Try to get from cache first
    cached_analytics = await cache_utils.get_cached_analytics(business_id, "business")
    if cached_analytics:
        return cached_analytics
    
    analytics = AnalyticsCRUD.get_business_analytics(db, business_id)
    
    # Cache the result
    await cache_utils.cache_analytics_data(business_id, "business", analytics)
    
    return analytics

@router.get("/business/{business_id}/date-range", response_model=DateRangeStats)
def get_date_range_analytics(
    business_id: UUID,
    start_date: datetime = Query(..., description="Start date for analytics range"),
    end_date: datetime = Query(..., description="End date for analytics range"),
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get analytics for a specific date range (business owners/managers only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    # Validate date range
    if start_date >= end_date:
        raise HTTPException(
            status_code=400, 
            detail="Start date must be before end date"
        )
    
    # Limit to reasonable date ranges (max 1 year)
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=400, 
            detail="Date range cannot exceed 365 days"
        )
    
    stats = AnalyticsCRUD.get_date_range_stats(db, business_id, start_date, end_date)
    return stats

@router.get("/business/{business_id}/daily-sales")
def get_daily_sales(
    business_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze (1-365)"),
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get daily sales data for the last N days (business owners/managers only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    daily_sales = AnalyticsCRUD.get_daily_sales(db, business_id, days)
    return {
        "business_id": business_id,
        "days_analyzed": days,
        "daily_sales": daily_sales
    }

@router.get("/business/{business_id}/summary")
def get_business_summary(
    business_id: UUID,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get comprehensive business summary with key metrics."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    # Get various analytics
    business_analytics = AnalyticsCRUD.get_business_analytics(db, business_id)
    daily_sales_30 = AnalyticsCRUD.get_daily_sales(db, business_id, 30)
    daily_sales_7 = AnalyticsCRUD.get_daily_sales(db, business_id, 7)
    
    # Calculate trends
    current_week_revenue = sum(day["revenue"] for day in daily_sales_7)
    last_week_start = datetime.now() - timedelta(days=14)
    last_week_end = datetime.now() - timedelta(days=7)
    last_week_stats = AnalyticsCRUD.get_date_range_stats(db, business_id, last_week_start, last_week_end)
    
    revenue_trend = 0
    if last_week_stats["total_revenue"] > 0:
        revenue_trend = ((current_week_revenue - last_week_stats["total_revenue"]) / last_week_stats["total_revenue"]) * 100
    
    return {
        "business_id": business_id,
        "business_name": business.name,
        "summary": business_analytics,
        "trends": {
            "revenue_change_percent": round(revenue_trend, 2),
            "current_week_revenue": current_week_revenue,
            "last_week_revenue": last_week_stats["total_revenue"]
        },
        "recent_activity": {
            "last_7_days": daily_sales_7,
            "last_30_days": daily_sales_30
        }
    }
