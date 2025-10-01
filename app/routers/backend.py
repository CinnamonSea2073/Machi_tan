from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Item(BaseModel):
    id: int
    name: str


@router.get("/items")
async def list_items():
    return [{"id": 1, "name": "example"}]


@router.post("/items")
async def create_item(item: Item):
    if item.id <= 0:
        raise HTTPException(status_code=400, detail="invalid id")
    return item
