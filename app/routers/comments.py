from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db import get_connection, init_db

router = APIRouter()


class CommentIn(BaseModel):
    author: str
    text: str


class CommentOut(BaseModel):
    id: int
    author: str
    text: str
    created_at: str



@router.get("/comments")
def list_comments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, author, text, created_at FROM comments ORDER BY id DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/comments", response_model=CommentOut)
def create_comment(payload: CommentIn):
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (author, text, created_at) VALUES (?, ?, ?)",
        (payload.author, payload.text, now),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "author": payload.author, "text": payload.text, "created_at": now}
