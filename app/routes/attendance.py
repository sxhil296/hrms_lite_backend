from fastapi import APIRouter, HTTPException
from app.database import attendance_collection, employee_collection
from app.schemas.attendance import AttendanceCreate

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/")
async def mark_attendance(data: AttendanceCreate):

    if data.status not in ["Present", "Absent"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be Present or Absent"
        )

    employee = await employee_collection.find_one(
        {"employee_id": data.employee_id}
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    existing = await attendance_collection.find_one({
        "employee_id": data.employee_id,
        "date": data.date
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Attendance already marked for this date"
        )

    result = await attendance_collection.insert_one(data.dict())

    return {
        "message": "Attendance marked successfully",
        "id": str(result.inserted_id)
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