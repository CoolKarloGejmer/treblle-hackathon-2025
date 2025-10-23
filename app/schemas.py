"""Pydantic schemas for the Ticket API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.enums import Category, Priority, Status


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=4000)
    reporter_email: Optional[EmailStr] = None


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: Category
    priority: Priority
    status: Status
    reporter_email: Optional[EmailStr]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    name: str
    count: int


class TicketUpdate(BaseModel):
    """Fields allowed when updating a ticket."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    reporter_email: Optional[EmailStr] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None


class PaginatedTickets(BaseModel):
    total: int
    items: list[TicketOut]


class ApiRequestCreate(BaseModel):
    """Schema for creating an API request record."""
    method: str = Field(..., max_length=10)
    path: str = Field(..., max_length=2048)
    response_code: int = Field(..., ge=100, le=599)
    response_time: float = Field(..., ge=0.0)
    user_agent: Optional[str] = Field(None, max_length=512)
    ip_address: Optional[str] = Field(None, max_length=45)


class ApiRequestOut(BaseModel):
    """Schema for API request output."""
    id: int
    method: str
    path: str
    response_code: int
    response_time: float
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class PaginatedApiRequests(BaseModel):
    """Schema for paginated API requests."""
    total: int
    items: list[ApiRequestOut]

