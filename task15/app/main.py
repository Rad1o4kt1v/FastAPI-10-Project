from fastapi import FastAPI
from app.database import init_db
from app.config import settings

app = FastAPI(title=settings.project_name)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def read_root():
    return {"message": "FastAPI project with Pydantic Settings"}
