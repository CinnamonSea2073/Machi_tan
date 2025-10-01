from fastapi import FastAPI
from app.routers import frontend, backend
from app.routers import users, courses, class_course, status, comments_new as comments, groq
from app.db import init_db

app = FastAPI(title="Machi_tan", version="0.1.0")

app.include_router(frontend.router, prefix="", tags=["frontend"])
app.include_router(backend.router, prefix="/api", tags=["backend"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(courses.router, prefix="/api", tags=["courses"])
app.include_router(class_course.router, prefix="/api", tags=["class_course"])
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(groq.router, prefix="/api", tags=["groq"])
app.include_router(__import__("app.routers.control", fromlist=["router"]).router, prefix="/api", tags=["control"])


@app.on_event("startup")
def on_startup():
    # ensure database/tables exist
    init_db()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
