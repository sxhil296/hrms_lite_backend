from fastapi import APIRouter, HTTPException, Query
from app.database import attendance_collection, employee_collection
from app.schemas.attendance import AttendanceCreate
from datetime import datetime, timedelta

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", status_code=201)
async def mark_attendance(data: AttendanceCreate):

    if data.status not in ["present", "absent", "leave", "half_day"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be present, absent, leave, or half-day"
        )

    employee = await employee_collection.find_one(
        {"employee_id": data.employee_id}
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Convert date -> datetime
    attendance_date = datetime.combine(data.date, datetime.min.time())

    existing = await attendance_collection.find_one({
        "employee_id": data.employee_id,
        "date": attendance_date
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance already marked for this date"
        )

    attendance_data = data.dict()
    attendance_data["date"] = attendance_date

    result = await attendance_collection.insert_one(attendance_data)

    return {
        "success": True,
        "message": "Attendance marked successfully",
        "data": {
            "id": str(result.inserted_id)
        }
    }

@router.get("/{employee_id}")
async def get_attendance(employee_id: str):

    records = []

    async for rec in attendance_collection.find(
        {"employee_id": employee_id}
    ):
        rec["id"] = str(rec["_id"])
        del rec["_id"]
        records.append(rec)

    return records

# get all attendace records
@router.get("/")
async def get_all_attendance(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    date: str = Query("", min_length=0),
    search: str = Query("", min_length=0),
    status: str = Query("", min_length=0)
):
    skip = (page - 1) * limit

    filters = []

 

    if date:
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)

        filters.append({
        "date": {
            "$gte": start,
            "$lt": end
        }
        })

    if search:
        filters.append({
            "employee_id": {"$regex": search, "$options": "i"}
        })

    if status:
        filters.append({"status": status})

    match_stage = {"$match": {"$and": filters}} if filters else {"$match": {}}

    pipeline = [
        match_stage,

        # join employee collection
        {
            "$lookup": {
                "from": "employees",
                "localField": "employee_id",
                "foreignField": "employee_id",
                "as": "employee"
            }
        },

        # flatten employee array
        {
            "$unwind": {
                "path": "$employee",
                "preserveNullAndEmptyArrays": True
            }
        },

        {
            "$project": {
                "_id": 1,
                "employee_id": 1,
                "date": 1,
                "status": 1,
                "employee.full_name": 1,
                "employee.email": 1,
                "employee.department": 1
            }
        },

        {"$skip": skip},
        {"$limit": limit}
    ]

    cursor = attendance_collection.aggregate(pipeline)

    records = []
    async for rec in cursor:
        rec["id"] = str(rec["_id"])
        del rec["_id"]
        records.append(rec)

    total = await attendance_collection.count_documents(match_stage["$match"])

    return {
        "success": True,
        "message": "Attendance records fetched successfully",
        "data": records,
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit
        }
    }