<a id="readme-top"></a>

## Table of Contents  
- [About The Project](#about-the-project)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Technology Stack](#technology-stack)  
- [Ticket Categorization Logic](#ticket-categorization-logic)  

---

## About The Project  
This project implements a RESTful API for managing support tickets and tracking API requests. It is built using FastAPI, SQLAlchemy, and SQLite, and follows best practices in API design, documentation, and testing.

---

## Getting Started  

### Prerequisites  
- Python 3.8 or higher  
- pip package manager  

### Installation  
```bash
git clone https://github.com/CoolKarloGejmer/treblle-hackathon-2025.git
cd treblle-hackathon-2025/backend
pip install -r requirements.txt
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

---

## Usage  
Use the API to create, read, update, and delete tickets and API request logs. It supports filtering, sorting, and searching on key fields. For detailed API endpoint information, refer to the generated OpenAPI documentation at the links above.

---

## Project Structure  
```
treblle-hackathon-2025/
│
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py
│   ├── crud.py
│   ├── database.py
│   ├── dependencies.py
│   ├── enums.py
│   ├── models.py
│   └── schemas.py
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_main.py
│   └── test_tickets.py
│
├── docs/
│   └── Treblle_Hackathon_2025.txt
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Technology Stack  
| Component    | Technology |
|--------------|-----------|
| Framework    | FastAPI    |
| ORM          | SQLAlchemy |
| Database     | SQLite     |
| Validation   | Pydantic   |
| Testing      | pytest     |
| Server       | Uvicorn    |

---

## Ticket Categorization Logic  
Tickets are automatically assigned a category and priority according to defined keyword rules.

**Categories**  
- Bug: keywords such as "error", "exception", "traceback"  
- Feature Request: keywords such as "feature", "enhancement", "add", "support"  
- Billing: keywords such as "bill", "invoice", "payment"  
- Support: default category  

**Priority**  
- High: tickets containing keywords like "urgent", "asap", "critical"  
- Medium: all other tickets by default  

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
