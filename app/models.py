"""SQLAlchemy models for the application.

This module defines ORM models that map to database tables. Only the
ApiRequest model is implemented here for now.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func, Enum as SAEnum
from app.database import Base
from enums import Category, Priority, Status


class ApiRequest(Base):
    """Represents a recorded API request.

    Fields:
    - id: primary key
    - method: HTTP method (GET/POST/...)
    - path: request path
    - response_code: HTTP response status code
    - response_time: float seconds (or milliseconds, choose and be consistent)
    - user_agent: optional client user agent string
    - ip_address: optional client IP (IPv4/IPv6)
    - created_at: timestamp when the request was recorded
    """

    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(10), nullable=False, index=True)
    path = Column(String(2048), nullable=False, index=True)
    response_code = Column(Integer, nullable=False, index=True)
    response_time = Column(Float, nullable=False, default=0.0)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<ApiRequest id={self.id} method={self.method} path={self.path} "
            f"code={self.response_code} time={self.response_time}>")


class Ticket(Base):
    """Represents a user-reported ticket/issue.

    Fields:
    - id: primary key
    - title: short title
    - description: detailed description
    - category: assigned category (bug, feature_request, support, billing, other)
    - priority: low/medium/high
    - status: open/resolved
    - reporter_email: optional contact
    - created_at, resolved_at
    """

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(4000), nullable=False)
    category = Column(SAEnum(Category), nullable=False, index=True, default=Category.other.value)
    priority = Column(SAEnum(Priority), nullable=False, index=True, default=Priority.medium.value)
    status = Column(SAEnum(Status), nullable=False, index=True, default=Status.open.value)
    reporter_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)

