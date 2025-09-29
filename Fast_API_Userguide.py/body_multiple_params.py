from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str

@app.post("/items/")
async def create_item(item: Item, user: User):
    return {"item": item, "user": user}
