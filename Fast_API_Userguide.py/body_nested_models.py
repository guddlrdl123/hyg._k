from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SubItem(BaseModel):
    description: str

class Item(BaseModel):
    name: str
    sub_item: SubItem

@app.post("/items/")
async def create_item(item: Item):
    return item
