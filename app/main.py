from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.routes import employee, attendance
from app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

app = FastAPI(
    title="HRMS Lite API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(employee.router)
app.include_router(attendance.router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "HRMS Lite API running successfully",
        "data": None,
        "meta": None,
    }