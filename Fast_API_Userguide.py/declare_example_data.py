from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., example="Foo")
    description: str = Field(None, example="A very nice item")

@app.post("/items/")
async def create_item(item: Item):
    return item
