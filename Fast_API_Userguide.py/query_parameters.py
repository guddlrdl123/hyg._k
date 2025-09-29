from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items(q: str = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}
