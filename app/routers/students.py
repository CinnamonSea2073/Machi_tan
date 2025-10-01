from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from app.db import get_connection

router = APIRouter()


class StudentIn(BaseModel):
    name: str


class StudentOut(BaseModel):
    student_id: str
    name: str
    created_at: str


@router.post("/students", response_model=StudentOut)
def create_student(payload: StudentIn):
    student_id = str(uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (student_id, name, created_at) VALUES (?, ?, ?)",
        (student_id, payload.name, now),
    )
    conn.commit()
    conn.close()
    return {"student_id": student_id, "name": payload.name, "created_at": now}


@router.get("/students")
def list_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id, name, created_at FROM students ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/students/{student_id}")
def get_student(student_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id, name, created_at FROM students WHERE student_id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="student not found")
    return dict(row)
