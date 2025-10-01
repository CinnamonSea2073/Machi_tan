from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from app.db import get_connection

router = APIRouter()


class UserIn(BaseModel):
    name: str


class UserOut(BaseModel):
    user_id: str
    name: str
    created_at: str


@router.post("/users", response_model=UserOut)
def create_user(payload: UserIn):
    user_id = str(uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, name, created_at) VALUES (?, ?, ?)", (user_id, payload.name, now))
    conn.commit()
    conn.close()
    return {"user_id": user_id, "name": payload.name, "created_at": now}


@router.post("/users/register", response_model=UserOut)
def register_user(payload: UserIn):
    # compatibility alias
    return create_user(payload)


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, created_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    return dict(row)
