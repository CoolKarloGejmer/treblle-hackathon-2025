from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/api")


# ==================== TICKET ENDPOINTS ====================

@router.post("/tickets", response_model=schemas.TicketOut, tags=["Tickets"])
def create_ticket(ticket_in: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Create a new ticket.

    The ticket will be automatically categorized and prioritized based on its content.
    """
    ticket = crud.create_ticket(db, ticket_in)
    return ticket


@router.get("/tickets/search", response_model=schemas.PaginatedTickets, tags=["Tickets"])
def search_tickets(
    search: Optional[str] = Query(None, description="Search in title and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    sort_by: str = Query("created_at", description="Sort by field (created_at, priority)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Search and filter tickets with pagination.

    Supports:
    - Full-text search in title and description
    - Filtering by category, status, priority
    - Sorting by created_at or priority
    - Pagination with skip and limit
    """
    items, total = crud.search_and_filter_tickets(
        db=db,
        search=search,
        category=category,
        status=status,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return schemas.PaginatedTickets(total=total, items=items)


@router.get("/tickets", response_model=List[schemas.TicketOut], tags=["Tickets"])
def list_tickets(category: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List tickets with optional filtering by category and status.

    For advanced filtering and search, use /tickets/search endpoint.
    """
    return crud.list_tickets(db, category=category, status=status)


@router.get("/tickets/{ticket_id}", response_model=schemas.TicketOut, tags=["Tickets"])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get a single ticket by ID."""
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=schemas.TicketOut, tags=["Tickets"])
def update_ticket(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    """
    Update a ticket.

    You can update any combination of fields: title, description, category, priority, status, reporter_email.
    """
    ticket = crud.update_ticket(db, ticket_id, ticket_update)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/tickets/{ticket_id}", tags=["Tickets"])
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Delete a ticket by ID."""
    success = crud.delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket deleted successfully"}


@router.post("/tickets/{ticket_id}/resolve", response_model=schemas.TicketOut, tags=["Tickets"])
def resolve_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Mark a ticket as resolved."""
    ticket = crud.resolve_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# ==================== API REQUEST ENDPOINTS ====================

@router.post("/requests", response_model=schemas.ApiRequestOut, tags=["API Requests"])
def create_api_request(request_in: schemas.ApiRequestCreate, db: Session = Depends(get_db)):
    """
    Record a new API request.

    Use this endpoint to log API requests for monitoring and analysis.
    """
    return crud.create_api_request(db, request_in)


@router.get("/requests", response_model=schemas.PaginatedApiRequests, tags=["API Requests"])
def list_api_requests(
    method: Optional[str] = Query(None, description="Filter by HTTP method (GET, POST, etc.)"),
    response_code: Optional[int] = Query(None, description="Filter by response code"),
    min_response_time: Optional[float] = Query(None, description="Minimum response time in seconds"),
    max_response_time: Optional[float] = Query(None, description="Maximum response time in seconds"),
    path_contains: Optional[str] = Query(None, description="Filter by path containing string"),
    sort_by: str = Query("created_at", description="Sort by field (created_at, response_time)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List and filter API requests.

    Supports:
    - Filtering by method, response code, response time range, path
    - Sorting by created_at or response_time
    - Pagination with skip and limit
    """
    items, total = crud.list_and_filter_api_requests(
        db=db,
        method=method,
        response_code=response_code,
        min_response_time=min_response_time,
        max_response_time=max_response_time,
        path_contains=path_contains,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    return schemas.PaginatedApiRequests(total=total, items=items)


@router.get("/requests/{request_id}", response_model=schemas.ApiRequestOut, tags=["API Requests"])
def get_api_request(request_id: int, db: Session = Depends(get_db)):
    """Get a single API request by ID."""
    request = crud.get_api_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="API request not found")
    return request
