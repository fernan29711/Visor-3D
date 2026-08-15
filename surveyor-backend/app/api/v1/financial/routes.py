"""Financial analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.services.financial_service import FinancialService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/financial", tags=["Financial"])

@router.get("/summary")
async def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get overall financial summary."""
    try:
        service = FinancialService(db)
        summary = service.get_financial_summary(str(current_user.organization_id))
        return summary
    except AppException as e:
        raise http_exception(e)

@router.get("/revenue-by-month")
async def get_revenue_by_month(
    months: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get revenue data grouped by month."""
    try:
        service = FinancialService(db)
        data = service.get_revenue_by_month(str(current_user.organization_id), months)
        return data
    except AppException as e:
        raise http_exception(e)

@router.get("/payment-status-distribution")
async def get_payment_status_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get distribution of invoices by payment status."""
    try:
        service = FinancialService(db)
        distribution = service.get_payment_status_distribution(str(current_user.organization_id))
        return distribution
    except AppException as e:
        raise http_exception(e)

@router.get("/top-clients")
async def get_top_clients_by_revenue(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top clients by revenue."""
    try:
        service = FinancialService(db)
        clients = service.get_top_clients_by_revenue(str(current_user.organization_id), limit)
        return clients
    except AppException as e:
        raise http_exception(e)

@router.get("/quote-conversion")
async def get_quote_conversion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quote to invoice conversion metrics."""
    try:
        service = FinancialService(db)
        conversion = service.get_quote_conversion(str(current_user.organization_id))
        return conversion
    except AppException as e:
        raise http_exception(e)

@router.get("/project-profitability")
async def get_project_profitability(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get profitability analysis by project."""
    try:
        service = FinancialService(db)
        profitability = service.get_project_profitability(str(current_user.organization_id))
        return profitability
    except AppException as e:
        raise http_exception(e)

@router.get("/collection-forecast")
async def get_collection_forecast(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get forecast of expected collections in next N days."""
    try:
        service = FinancialService(db)
        forecast = service.get_collection_forecast(str(current_user.organization_id), days)
        return forecast
    except AppException as e:
        raise http_exception(e)
