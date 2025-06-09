from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = "your-secret-key"  # Replace with secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "postgresql://dtc_clean:12345pass@localhost:5432/dtc_clean_db"

# FastAPI app
app = FastAPI()

# Database setup
engine = create_engine(DATABASE_URL)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str
    disabled: bool = False

class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    owner_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic schemas
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

# JWT functions
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == token_data.username)).first()
        if user is None or user.disabled:
            raise credentials_exception
        return user

# Create database tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Authentication endpoint
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or user.password != form_data.password:  # In production, verify hashed password
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

# CRUD endpoints
@app.post("/notes/", response_model=NoteOut)
async def create_note(note: NoteCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    db_note = Note(title=note.title, content=note.content, owner_id=current_user.id)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@app.get("/notes/", response_model=List[NoteOut])
async def read_notes(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    notes = session.exec(select(Note).where(Note.owner_id == current_user.id)).all()
    return notes

@app.get("/notes/{note_id}", response_model=NoteOut)
async def read_note(note_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")
    return note

@app.put("/notes/{note_id}", response_model=NoteOut)
async def update_note(note_id: int, note: NoteUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    db_note = session.get(Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if db_note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")
    note_data = note.dict(exclude_unset=True)
    for key, value in note_data.items():
        setattr(db_note, key, value)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
    session.delete(note)
    session.commit()
    return {"message": "Note deleted successfully"}
