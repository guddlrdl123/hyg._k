from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: str = Query(None, min_length=3, max_length=50, regex="^fixedquery$")
):
    return {"q": q}
