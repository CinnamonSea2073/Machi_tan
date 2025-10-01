from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_items():
    r = client.get("/api/items")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_comments_post_get():
    # create a user first
    r_user = client.post("/api/users", json={"name": "tester"})
    assert r_user.status_code == 200
    user = r_user.json()
    assert "user_id" in user

    # create a comment using user_id
    payload = {"user_id": user["user_id"], "text": "hello", "genre": "general"}
    r = client.post("/api/comments", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == user["user_id"]
    assert data["text"] == "hello"

    # list comments
    r2 = client.get("/api/comments")
    assert r2.status_code == 200
    arr = r2.json()
    assert any(c["comment_id"] == data["comment_id"] for c in arr)
