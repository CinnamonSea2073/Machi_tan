from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Request
from pydantic import BaseModel
from datetime import datetime
from app.db import get_connection
import uuid


class CourseBody(BaseModel):
    id: str | None = None
    content: str | None = None

router = APIRouter()


class CourseIn(BaseModel):
    course_id: str | None = None


@router.post("/courses")
async def create_course(request: Request, file: UploadFile = File(None), course_id: str | None = None):
    """
    Create or replace a course. Accepts either JSON body {id, content} or multipart upload (file).
    """
    # Try to read JSON body first
    json_body = None
    try:
        json_body = await request.json()
    except Exception:
        json_body = None

    if json_body and isinstance(json_body, dict) and json_body.get("content"):
        cid = json_body.get("id") or course_id or str(uuid.uuid4())
        text = json_body.get("content")
    elif file is not None:
        content = await file.read()
        text = content.decode("utf-8")
        cid = course_id or str(uuid.uuid4())
    else:
        raise HTTPException(status_code=422, detail="no course content provided")

    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("REPLACE INTO courses (course_id, gpx_content, created_at) VALUES (?, ?, ?)", (cid, text, now))
    conn.commit()
    conn.close()
    return {"course_id": cid, "created_at": now}


@router.get("/courses")
def list_courses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id, created_at FROM courses ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/courses/{course_id}")
def get_course(course_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_id, gpx_content, created_at FROM courses WHERE course_id = ?", (course_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="course not found")
    return {"course_id": row["course_id"], "gpx": row["gpx_content"], "created_at": row["created_at"]}


@router.delete("/courses/{course_id}")
def delete_course(course_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
    conn.commit()
    conn.close()
    return {"deleted": True}
