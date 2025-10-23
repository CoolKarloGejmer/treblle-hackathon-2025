"""CRUD operations and simple rule-based classifier for Tickets."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from api import schemas
from enums import Category, Priority, Status


def classify_text(title: str, description: str) -> Tuple[str, str]:
    """Simple rule-based classifier returning (category, priority)."""
    text = (title + " " + description).lower()

    # category rules
    if any(k in text for k in ("error", "exception", "traceback", "stacktrace")):
        category = Category.bug.value
    elif any(k in text for k in ("feature", "enhancement", "add", "support")):
        category = Category.feature_request.value
    elif any(k in text for k in ("bill", "invoice", "payment", "charge")):
        category = Category.billing.value
    else:
        category = Category.support.value

    # priority rules
    if any(k in text for k in ("urgent", "asap", "critical", "down")):
        priority = Priority.high.value
    else:
        priority = Priority.medium.value

    return category, priority


def create_ticket(db: Session, ticket_in: schemas.TicketCreate) -> models.Ticket:
    category, priority = classify_text(ticket_in.title, ticket_in.description)
    db_obj = models.Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        reporter_email=ticket_in.reporter_email,
        category=category,
        priority=priority,
        status=Status.open.value,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()


def list_tickets(db: Session, category: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[models.Ticket]:
    q = db.query(models.Ticket)
    if category:
        # allow passing either enum value or raw string
        cat_val = category if isinstance(category, str) else category.value
        q = q.filter(models.Ticket.category == cat_val)
    if status:
        st_val = status if isinstance(status, str) else status.value
        q = q.filter(models.Ticket.status == st_val)
    return q.order_by(models.Ticket.created_at.desc()).limit(limit).all()


def resolve_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None
    ticket.status = Status.resolved.value
    ticket.resolved_at = func.now()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(db: Session, ticket_id: int, ticket_update: schemas.TicketUpdate) -> Optional[models.Ticket]:
    """Update a ticket with the provided fields."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None

    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: int) -> bool:
    """Delete a ticket by ID. Returns True if deleted, False if not found."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True


def search_and_filter_tickets(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[models.Ticket], int]:
    """Search and filter tickets with sorting and pagination."""
    q = db.query(models.Ticket)

    # Search in title and description
    if search:
        search_filter = f"%{search}%"
        q = q.filter(
            (models.Ticket.title.ilike(search_filter)) |
            (models.Ticket.description.ilike(search_filter))
        )

    # Filter by category
    if category:
        q = q.filter(models.Ticket.category == category)

    # Filter by status
    if status:
        q = q.filter(models.Ticket.status == status)

    # Filter by priority
    if priority:
        q = q.filter(models.Ticket.priority == priority)

    # Get total count before pagination
    total = q.count()

    # Apply sorting
    if sort_by == "created_at":
        sort_col = models.Ticket.created_at
    elif sort_by == "priority":
        sort_col = models.Ticket.priority
    else:
        sort_col = models.Ticket.created_at

    if sort_order == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    # Apply pagination
    items = q.offset(skip).limit(limit).all()

    return items, total


# API Request CRUD operations
def create_api_request(db: Session, api_request: schemas.ApiRequestCreate) -> models.ApiRequest:
    """Create a new API request record."""
    db_obj = models.ApiRequest(
        method=api_request.method,
        path=api_request.path,
        response_code=api_request.response_code,
        response_time=api_request.response_time,
        user_agent=api_request.user_agent,
        ip_address=api_request.ip_address,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_api_request(db: Session, request_id: int) -> Optional[models.ApiRequest]:
    """Get a single API request by ID."""
    return db.query(models.ApiRequest).filter(models.ApiRequest.id == request_id).first()


def list_and_filter_api_requests(
    db: Session,
    method: Optional[str] = None,
    response_code: Optional[int] = None,
    min_response_time: Optional[float] = None,
    max_response_time: Optional[float] = None,
    path_contains: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[models.ApiRequest], int]:
    """List and filter API requests with sorting and pagination."""
    q = db.query(models.ApiRequest)

    # Filter by method
    if method:
        q = q.filter(models.ApiRequest.method == method.upper())

    # Filter by response code
    if response_code:
        q = q.filter(models.ApiRequest.response_code == response_code)

    # Filter by response time range
    if min_response_time is not None:
        q = q.filter(models.ApiRequest.response_time >= min_response_time)
    if max_response_time is not None:
        q = q.filter(models.ApiRequest.response_time <= max_response_time)

    # Filter by path
    if path_contains:
        q = q.filter(models.ApiRequest.path.ilike(f"%{path_contains}%"))

    # Get total count
    total = q.count()

    # Apply sorting
    if sort_by == "response_time":
        sort_col = models.ApiRequest.response_time
    elif sort_by == "created_at":
        sort_col = models.ApiRequest.created_at
    else:
        sort_col = models.ApiRequest.created_at

    if sort_order == "asc":
        q = q.order_by(sort_col.asc())
    else:
        q = q.order_by(sort_col.desc())

    # Apply pagination
    items = q.offset(skip).limit(limit).all()

    return items, total
