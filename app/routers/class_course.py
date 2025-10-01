from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from app.db import get_connection

router = APIRouter()


class CourseSetRequest(BaseModel):
    course_id: str


@router.post("/class_course/set")
def set_class_course_json(payload: CourseSetRequest):
    course_id = payload.course_id
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    # ensure row exists with id=1
    cur.execute("INSERT OR REPLACE INTO class_course (id, course_id, set_at) VALUES (1, ?, ?)", (course_id, now))
    conn.commit()
    conn.close()
    return {"course_id": course_id, "set_at": now}


@router.post("/class_course/{course_id}")
def set_class_course_path(course_id: str):
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    # ensure row exists with id=1
    cur.execute("INSERT OR REPLACE INTO class_course (id, course_id, set_at) VALUES (1, ?, ?)", (course_id, now))
    conn.commit()
    conn.close()
    return {"course_id": course_id, "set_at": now}


@router.get("/class_course")
def get_class_course():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id, set_at FROM class_course WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if not row or not row["course_id"]:
        raise HTTPException(status_code=404, detail="no class course set")
    return {"course_id": row["course_id"], "set_at": row["set_at"]}
