import pytest
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, Field, select
from typing import Optional, List
import jwt

# === БАЗА ===
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# === МОДЕЛИ ===
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

# === AUTH ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "SECRET"

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload.get("sub"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_session():
    with Session(engine) as session:
        yield session

# === APP ===
app = FastAPI()

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
def get_notes(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None),
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    query = select(Note).where(Note.owner_id == user_id)
    if search:
        query = query.where(Note.content.ilike(f"%{search}%"))
    notes = session.exec(query.offset(skip).limit(limit)).all()
    return notes

# === ТЕСТЫ ===
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session
    app.dependency_overrides[get_session] = override_get_session

    def override_current_user():
        return 1
    app.dependency_overrides[get_current_user] = override_current_user

    return TestClient(app)

def test_create_note(client):
    response = client.post("/notes", json={"title": "Test Note", "content": "This is a test."})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"

def test_read_notes(client):
    for i in range(3):
        client.post("/notes", json={"title": f"Note {i}", "content": "Test content"})
    response = client.get("/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 3

def test_search_notes(client):
    client.post("/notes", json={"title": "Find Me", "content": "needle"})
    client.post("/notes", json={"title": "Not Me", "content": "haystack"})
    response = client.get("/notes?search=needle")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["content"] == "needle"

def test_pagination_notes(client):
    for i in range(10):
        client.post("/notes", json={"title": f"Note {i}", "content": f"content {i}"})
    response = client.get("/notes?skip=0&limit=5")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 5

