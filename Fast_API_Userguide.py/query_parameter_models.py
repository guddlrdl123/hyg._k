from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

@app.get("/items/")
async def read_items(q: List[str] = Query([])):
    return {"q": q}
