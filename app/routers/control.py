from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db import get_connection

router = APIRouter()


class CourseOfDayIn(BaseModel):
    course_id: str


class StatusIn(BaseModel):
    status: str


@router.post("/control/course_of_day")
def set_course_of_day(payload: CourseOfDayIn):
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO class_course (id, course_id, set_at) VALUES (1, ?, ?)", (payload.course_id, now))
    conn.commit()
    conn.close()
    return {"course_of_day": payload.course_id, "set_at": now}


@router.get("/control/course_of_day")
def get_course_of_day():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id FROM class_course WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if not row or not row["course_id"]:
        raise HTTPException(status_code=404, detail="no course of day set")
    return {"course_of_day": row["course_id"]}


@router.post("/control/status")
def set_status(payload: StatusIn):
    # delegate to statuses table (no validation here)
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO statuses (status, created_at) VALUES (?, ?)", (payload.status, now))
    conn.commit()
    conn.close()
    return {"status": payload.status, "created_at": now}


@router.get("/control/status")
def get_status():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, created_at FROM statuses ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="no status set")
    return {"status": row["status"], "created_at": row["created_at"]}
