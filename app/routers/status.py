from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db import get_connection

router = APIRouter()

ALLOWED = {"デバッグ", "チュートリアル", "実行中", "終了", "結果"}


class StatusIn(BaseModel):
    status: str


@router.post("/status")
def set_status(payload: StatusIn):
    if payload.status not in ALLOWED:
        raise HTTPException(status_code=400, detail="invalid status")
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO statuses (status, created_at) VALUES (?, ?)", (payload.status, now))
    conn.commit()
    conn.close()
    return {"status": payload.status, "created_at": now}


@router.get("/status")
def get_latest_status():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, created_at FROM statuses ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="no status set")
    return {"status": row["status"], "created_at": row["created_at"]}
