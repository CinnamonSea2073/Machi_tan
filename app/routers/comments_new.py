from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from app.db import get_connection

router = APIRouter()


def fix_mojibake(s: str) -> str:
    """Attempt to repair common mojibake where UTF-8 bytes were
    interpreted as single-byte chars (latin1/cp1252). If repair yields
    plausible CJK characters, return repaired string; otherwise return
    original."""
    if not s or not isinstance(s, str):
        return s
    # quick heuristic: if string looks ok (contains Japanese), skip
    import re
    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', s):
        return s
    try:
        # re-encode as latin1 bytes, then decode as utf-8
        b = s.encode('latin1', errors='replace')
        decoded = b.decode('utf-8', errors='replace')
        if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', decoded):
            return decoded
    except Exception:
        pass
    return s


class CommentIn(BaseModel):
    user_id: str
    text: str
    reply_to: str | None = None
    genre: str | None = None
    student_id: str | None = None
    lat: float | None = None
    lon: float | None = None


class CommentOut(BaseModel):
    comment_id: str
    user_id: str
    text: str
    reply_to: str | None = None
    genre: str | None = None
    student_id: str | None = None
    created_at: str
    lat: float | None = None
    lon: float | None = None


@router.post("/comments", response_model=CommentOut)
def create_comment(payload: CommentIn):
    cid = str(uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    # try to repair mojibake in incoming text before storing
    safe_text = fix_mojibake(payload.text)
    cur.execute(
        "INSERT INTO comments (comment_id, user_id, text, reply_to, genre, student_id, created_at, lat, lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (cid, payload.user_id, safe_text, payload.reply_to, payload.genre, payload.student_id, now, payload.lat, payload.lon),
    )
    conn.commit()
    # fetch the inserted row to return canonical stored values
    cur.execute("SELECT comment_id, user_id, text, reply_to, genre, student_id, created_at, lat, lon FROM comments WHERE comment_id = ?", (cid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"comment_id": cid, "user_id": payload.user_id, "text": safe_text, "reply_to": payload.reply_to, "genre": payload.genre, "student_id": payload.student_id, "created_at": now, "lat": payload.lat, "lon": payload.lon}


@router.get("/comments")
def list_comments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT comment_id, user_id, text, reply_to, genre, student_id, created_at, lat, lon FROM comments ORDER BY created_at DESC LIMIT 500")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["text"] = fix_mojibake(d.get("text"))
        # lat/lon will be present from SELECT
        out.append(d)
    return out


@router.post("/comments_v2/")
def create_comment_v2(payload: CommentIn):
    return create_comment(payload)


@router.get("/comments_v2/{comment_id}")
def get_comment_v2(comment_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT comment_id, user_id, text, reply_to, genre, student_id, created_at, lat, lon FROM comments WHERE comment_id = ?", (comment_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="comment not found")
    return dict(row)


@router.get("/comments/with_students")
def list_comments_with_students():
    """List comments with student names joined"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            c.comment_id, 
            c.user_id, 
            c.text, 
            c.reply_to, 
            c.genre, 
            c.student_id, 
            c.created_at,
            c.lat,
            c.lon,
            s.name as student_name
        FROM comments c
        LEFT JOIN students s ON c.student_id = s.student_id
        ORDER BY c.created_at DESC 
        LIMIT 500
    """)
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["text"] = fix_mojibake(d.get("text"))
        # also try to fix student_name if present
        if "student_name" in d and d["student_name"]:
            d["student_name"] = fix_mojibake(d["student_name"]) or d["student_name"]
        out.append(d)
    return out
