from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional, List
import uvicorn
import jwt

# ========== DATABASE SETUP ========== #
DATABASE_URL = "postgresql://dtc_clean:12345pass@localhost:5432/dtc_clean_db"
engine = create_engine(DATABASE_URL, echo=True)

# ========== MODELS ========== #
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

# ========== AUTH MOCK ========== #
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "SECRET"

# Предположим, что в токене закодирован user_id
def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ========== INIT ========== #
app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ========== ROUTES ========== #
@app.get("/notes", response_model=List[NoteRead])
def read_notes(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, description="Search in content"),
    current_user: int = Depends(get_current_user),
):
    with Session(engine) as session:
        stmt = select(Note).where(Note.owner_id == current_user)

        if search:
            stmt = stmt.where(Note.content.ilike(f"%{search}%"))

        stmt = stmt.offset(skip).limit(limit)
        notes = session.exec(stmt).all()
        return notes

@app.post("/notes", response_model=NoteRead)
def create_note(note: NoteCreate, current_user: int = Depends(get_current_user)):
    new_note = Note(**note.dict(), owner_id=current_user)
    with Session(engine) as session:
        session.add(new_note)
        session.commit()
        session.refresh(new_note)
        return new_note

# ========== DEV RUNNER ========== #
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
