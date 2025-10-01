from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from app.db import get_connection

router = APIRouter()


class CommentIn(BaseModel):
    user_id: str
    text: str
    reply_to: str | None = None
    genre: str | None = None


class CommentOut(BaseModel):
    comment_id: str
    user_id: str
    text: str
    reply_to: str | None = None
    genre: str | None = None
    created_at: str


@router.post("/comments", response_model=CommentOut)
def create_comment(payload: CommentIn):
    cid = str(uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (comment_id, user_id, text, reply_to, genre, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (cid, payload.user_id, payload.text, payload.reply_to, payload.genre, now),
    )
    conn.commit()
    conn.close()
    return {"comment_id": cid, "user_id": payload.user_id, "text": payload.text, "reply_to": payload.reply_to, "genre": payload.genre, "created_at": now}


@router.get("/comments")
def list_comments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT comment_id, user_id, text, reply_to, genre, created_at FROM comments ORDER BY created_at DESC LIMIT 500")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/comments_v2/")
def create_comment_v2(payload: CommentIn):
    return create_comment(payload)


@router.get("/comments_v2/{comment_id}")
def get_comment_v2(comment_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT comment_id, user_id, text, reply_to, genre, created_at FROM comments WHERE comment_id = ?", (comment_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="comment not found")
    return dict(row)
