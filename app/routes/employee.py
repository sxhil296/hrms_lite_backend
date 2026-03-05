from fastapi import APIRouter, HTTPException, status, Query
from app.database import employee_collection
from app.schemas.employee import EmployeeCreate
from app.database import attendance_collection
from app.schemas.employee import EmployeeCreate
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):

    # Check duplicate email
    existing = await employee_collection.find_one({
        "email": employee.email
    })

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with same email already exists"
        )
    # Generate unique employee ID
    count = await employee_collection.count_documents({})
    employee_id = f"EMP{count + 1:05d}"
    employee_data = employee.dict()
    employee_data["employee_id"] = employee_id

    result = await employee_collection.insert_one(employee_data)

    return {
        "success": True,
        "message": "Employee created successfully",
        "data": {
            "id": str(result.inserted_id),
            "employee_id": employee_id
        }
    }

@router.get("/")
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    search: str = Query("", min_length=0),
    department: str = Query("", min_length=0),
):
    skip = (page - 1) * limit

    query = {}

    filters = []

    # Search filter
    if search:
        filters.append({
            "$or": [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"employee_id": {"$regex": search, "$options": "i"}},
            ]
        })

    # Department filter
    if department:
        filters.append({"department": department})

    # Combine filters
    if filters:
        query = {"$and": filters}

    total = await employee_collection.count_documents(query)

    cursor = (
        employee_collection
        .find(query)
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )

    employees = []

    async for emp in cursor:
        emp["id"] = str(emp["_id"])
        del emp["_id"]
        employees.append(emp)

    total_pages = (total + limit - 1) // limit

    return {
        "success": True,
        "message": "Employees fetched successfully",
        "data": employees,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
            "hasNext": page < total_pages,
            "hasPrev": page > 1
        }
    }





# delete  employees by ids
class DeleteEmployeesRequest(BaseModel):
    employee_ids: List[str]


@router.delete("/")
async def delete_multiple_employees(payload: DeleteEmployeesRequest):

    result = await employee_collection.delete_many(
        {"employee_id": {"$in": payload.employee_ids}}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employees found for the provided IDs"
        )

    # Delete corresponding attendance records
    await attendance_collection.delete_many(
        {"employee_id": {"$in": payload.employee_ids}}
    )

    return {
        "success": True,
        "message": f"{result.deleted_count} employees deleted successfully",
        "data": {
            "deleted_count": result.deleted_count
        }
    }


# get employee by id with its attendance records + stats
@router.get("/{employee_id}")
async def get_employee(employee_id: str):

    # find employee
    employee = await employee_collection.find_one(
        {"employee_id": employee_id}
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # convert mongo _id
    employee["id"] = str(employee["_id"])
    del employee["_id"]

    # get attendance records
    attendance_cursor = attendance_collection.find(
        {"employee_id": employee_id}
    ).sort("date", -1)

    attendance_records = []

    total_present = 0
    total_absent = 0
    total_half_day = 0
    total_leaves = 0

    async for record in attendance_cursor:
        record["id"] = str(record["_id"])
        del record["_id"]

        status_value = record.get("status", "").lower()

        if status_value == "present":
            total_present += 1
        elif status_value == "absent":
            total_absent += 1
        elif status_value == "half_day":
            total_half_day += 1
        elif status_value == "leave":
            total_leaves += 1

        attendance_records.append(record)

    employee["attendance"] = attendance_records

    return {
        "success": True,
        "message": "Employee fetched successfully",
        "data": employee,
        "attendance_summary": {
            "total_present": total_present,
            "total_absent": total_absent,
            "total_half_day": total_half_day,
            "total_leaves": total_leaves
        }
    }