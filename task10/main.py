import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
import jwt

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/notes_db"
SECRET_KEY = os.environ.get("SECRET_KEY", "SECRET")

engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    owner_id: int

class NoteCreate(SQLModel):
    title: str
    content: str

class NoteRead(SQLModel):
    id: int
    title: str
    content: str

def get_session():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/notes", response_model=NoteRead)
def create_note(note: NoteCreate, user_id: int = Depends(get_current_user), session: Session = Depends(get_session)):
    db_note = Note(**note.dict(), owner_id=user_id)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@app.get("/notes", response_model=List[NoteRead])
def get_notes(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)):
    stmt = select(Note).where(Note.owner_id == user_id)
    return session.exec(stmt).all()

import time
from sqlalchemy.exc import OperationalError

def wait_for_db():
    retries = 10
    for i in range(retries):
        try:
            with engine.connect() as conn:
                print("✅ Database is ready.")
                return
        except OperationalError:
            print(f"⏳ Waiting for database... ({i+1}/{retries})")
            time.sleep(2)
    raise RuntimeError("❌ Could not connect to the database.")

@app.on_event("startup")
def on_startup():
    wait_for_db()
    SQLModel.metadata.create_all(engine)
