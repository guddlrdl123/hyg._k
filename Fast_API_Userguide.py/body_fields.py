from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., title="Name of the item", max_length=50)
    price: float = Field(..., gt=0)

@app.post("/items/")
async def create_item(item: Item):
    return item
