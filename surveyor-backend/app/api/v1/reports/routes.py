"""Report download endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.services.report_service import ReportService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/financial/excel")
async def download_financial_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download financial report as Excel."""
    try:
        service = ReportService(db)
        excel_buffer = service.generate_financial_report(str(current_user.organization_id))
        return FileResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"reporte_financiero_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/invoices/excel")
async def download_invoices_report(
    start_date: str = Query(None),
    end_date: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download invoices report as Excel."""
    try:
        start = None
        end = None
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        service = ReportService(db)
        excel_buffer = service.generate_invoices_report(
            str(current_user.organization_id),
            start,
            end
        )
        return FileResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"reporte_facturas_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/quotes/excel")
async def download_quotes_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download quotes report as Excel."""
    try:
        service = ReportService(db)
        excel_buffer = service.generate_quotes_report(str(current_user.organization_id))
        return FileResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"reporte_cotizaciones_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/clients/excel")
async def download_clients_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download clients report as Excel."""
    try:
        service = ReportService(db)
        excel_buffer = service.generate_clients_report(str(current_user.organization_id))
        return FileResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"reporte_clientes_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
    except AppException as e:
        raise http_exception(e)
