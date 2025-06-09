import json
import asyncio
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
import uvicorn
import redis.asyncio as redis
redis_client: redis.Redis = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ---------------------- Настройки ----------------------
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
REDIS_URL = "redis://localhost:6379"
CACHE_TTL = 30  # секунд

# ---------------------- Модели -------------------------
class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

class NoteCreate(SQLModel):
    title: str
    content: str

class NoteRead(SQLModel):
    id: int
    title: str
    content: str

# ---------------------- Инициализация ------------------
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    global redis
    redis = redis_client
    SQLModel.metadata.create_all(engine)

@app.on_event("shutdown")
async def on_shutdown():
    await redis.close()

def get_session():
    with Session(engine) as session:
        yield session

# ---------------------- CRUD с кешем -------------------

@app.get("/notes", response_model=List[NoteRead])
async def get_notes(session: Session = Depends(get_session)):
    cache_key = "notes:all"
    cached = await redis.get(cache_key)
    if cached:
        print("📦 From cache")
        return json.loads(cached)

    print("💾 From DB")
    notes = session.exec(select(Note)).all()
    notes_data = [note.dict() for note in notes]
    await redis.set(cache_key, json.dumps(notes_data), ex=CACHE_TTL)
    return notes_data

@app.post("/notes", response_model=NoteRead)
async def create_note(note: NoteCreate, session: Session = Depends(get_session)):
    db_note = Note(**note.dict())
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    await redis.delete("notes:all")  # инвалидируем кеш
    return db_note

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    await redis.delete("notes:all")  # инвалидируем кеш

# ---------------------- Запуск -------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
