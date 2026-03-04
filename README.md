# HRMS Lite Backend

A lightweight **HR Management System (HRMS)** backend built with **FastAPI** and **MongoDB**.  
It provides APIs to manage employees and attendance records.

---

## Tech Stack

- **FastAPI** – High-performance Python web framework
- **MongoDB** – NoSQL database for storing employee and attendance data
- **Uvicorn** – ASGI server for running the FastAPI application
- **Python Virtual Environment** – Dependency isolation

---

## Features

- Employee management
- Attendance tracking
- Attendance summary (present, absent, half day, leave)
- RESTful API structure
- Async database operations

---

## Installation & Setup

Follow these steps to run the backend locally.

### 1. Clone the Repository

```bash
git clone git@github.com:sxhil296/hrms_lite_backend.git

```
### 2. Move into the repo folder
```bash
cd hrms_lite_backend
```

### 3. Create Virtual Environment
```bash
python3 -m venv .venv
```

### 4. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Server
```bash
uvicorn app.main:app --reload
```
### The server will start at: http://127.0.0.1:8000
