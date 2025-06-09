import json
import os
import asyncio
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
import uvicorn
from app.main import SQLModel  # если SQLModel.metadata — твой target_metadata

target_metadata = SQLModel.metadata

# ---------------------- Настройки ----------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://dtc_clean:12345pass@localhost:5432/dtc_clean_db")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = 60

# ---------------------- Инициализация БД ----------------------
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# ---------------------- Модель ----------------------
class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

# ---------------------- Приложение ----------------------
app = FastAPI()
redis_client: redis.Redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@app.on_event("shutdown")
async def on_shutdown():
    await redis_client.close()

# ---------------------- CRUD + Кеш ----------------------
@app.get("/notes", response_model=List[Note])
async def read_notes(session: AsyncSession = Depends(get_session)):
    cached = await redis_client.get("notes:all")
    if cached:
        print("📦 From Redis cache")
        return json.loads(cached)

    print("💾 From DB")
    result = await session.execute(select(Note))
    notes = result.scalars().all()
    notes_data = [note.dict() for note in notes]
    await redis_client.set("notes:all", json.dumps(notes_data), ex=CACHE_TTL)
    return notes_data

@app.post("/notes", response_model=Note)
async def create_note(note: Note, session: AsyncSession = Depends(get_session)):
    session.add(note)
    await session.commit()
    await session.refresh(note)
    await redis_client.delete("notes:all")  # Инвалидация кеша
    return note

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, session: AsyncSession = Depends(get_session)):
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(note)
    await session.commit()
    await redis_client.delete("notes:all")  # Инвалидация кеша

# ---------------------- Запуск ----------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
