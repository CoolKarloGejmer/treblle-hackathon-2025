"""Application entrypoint.

Creates database tables on startup and exposes a FastAPI app
with OpenAPI documentation.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.database import engine, Base
from app.api.endpoints import router as api_router


app = FastAPI(
    title="Ticket & API Request Management API",
    description="""
## Ticket & API Request Management System

This API provides comprehensive ticket management and API request tracking capabilities.

### Features

#### Tickets Module
* **Create tickets** with automatic categorization and prioritization
* **Search and filter** tickets by various criteria
* **Update and delete** tickets
* **Resolve** tickets with timestamp tracking
* **Full-text search** in title and description

#### API Requests Module
* **Record API requests** for monitoring and analysis
* **Filter and sort** by method, response code, response time, and path
* **List and search** with pagination support
* Supports **time-based filtering** for performance analysis
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Tickets",
            "description": "Operations for managing tickets. Tickets represent user-reported issues or requests that are automatically categorized and prioritized.",
        },
        {
            "name": "API Requests",
            "description": "Operations for tracking and analyzing API requests. Use these endpoints to monitor API performance and usage patterns.",
        },
    ],
)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)


@app.get("/", tags=["Health"])
def root():
    """Root endpoint with API information."""
    return {
        "message": "Ticket & API Request Management API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "ok"}


def custom_openapi():
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    # Add example servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
