"""Quote endpoints."""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.quotes import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListResponse,
    QuoteDetailResponse,
    QuoteStatusUpdate,
)
from app.services.quote_service import QuoteService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/quotes", tags=["Quotes"])

@router.post("", response_model=QuoteDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    request: QuoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new quote."""
    try:
        service = QuoteService(db)
        quote = service.create(
            str(current_user.organization_id),
            str(current_user.id),
            request
        )
        return quote
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[QuoteListResponse])
async def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List quotes in organization."""
    try:
        service = QuoteService(db)
        quotes = service.list_by_organization(
            str(current_user.organization_id),
            skip=skip,
            limit=limit,
            status=status,
            search=search
        )
        return quotes
    except AppException as e:
        raise http_exception(e)

@router.get("/summary")
async def get_quotes_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quotes summary by status."""
    try:
        service = QuoteService(db)
        summary = service.get_quote_summary(str(current_user.organization_id))
        return summary
    except AppException as e:
        raise http_exception(e)

@router.get("/{quote_id}", response_model=QuoteDetailResponse)
async def get_quote(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quote details."""
    try:
        service = QuoteService(db)
        quote = service.get_quote_with_details(quote_id, str(current_user.organization_id))
        return quote
    except AppException as e:
        raise http_exception(e)

@router.patch("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: str,
    request: QuoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update quote."""
    try:
        service = QuoteService(db)
        quote = service.update(
            quote_id,
            str(current_user.organization_id),
            request
        )
        return quote
    except AppException as e:
        raise http_exception(e)

@router.post("/{quote_id}/status/{new_status}", response_model=QuoteResponse)
async def change_quote_status(
    quote_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change quote status."""
    try:
        service = QuoteService(db)
        quote = service.update_status(
            quote_id,
            str(current_user.organization_id),
            new_status
        )
        return quote
    except AppException as e:
        raise http_exception(e)

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete quote."""
    try:
        service = QuoteService(db)
        service.delete(quote_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.get("/client/{client_id}")
async def get_client_quotes(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get quotes for a specific client."""
    try:
        service = QuoteService(db)
        quotes = service.list_by_client(
            str(current_user.organization_id),
            client_id,
            skip=skip,
            limit=limit
        )
        return quotes
    except AppException as e:
        raise http_exception(e)
