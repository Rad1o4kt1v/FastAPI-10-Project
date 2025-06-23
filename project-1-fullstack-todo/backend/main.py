import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# --- App Configuration ---
app = FastAPI()

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class TodoItem(BaseModel):
    id: str
    task: str
    completed: bool = False

class TodoCreate(BaseModel):
    task: str

class TodoUpdate(BaseModel):
    task: str

# --- In-Memory Database ---
fake_todo_db: List[TodoItem] = []

# --- API Endpoints ---

@app.get("/api/todos", response_model=List[TodoItem])
async def get_all_todos():
    return fake_todo_db

@app.post("/api/todos", response_model=TodoItem, status_code=201)
async def create_todo(todo_data: TodoCreate):
    new_todo = TodoItem(
        id=str(uuid.uuid4()),
        task=todo_data.task,
        completed=False
    )
    fake_todo_db.append(new_todo)
    return new_todo

@app.patch("/api/todos/{todo_id}", response_model=TodoItem)
async def update_todo_status(todo_id: str):
    for todo in fake_todo_db:
        if todo.id == todo_id:
            todo.completed = not todo.completed
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/api/todos/{todo_id}", response_model=TodoItem)
async def update_todo_text(todo_id: str, updated_data: TodoUpdate):
    for todo in fake_todo_db:
        if todo.id == todo_id:
            todo.task = updated_data.task
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str):
    todo_to_delete = next((t for t in fake_todo_db if t.id == todo_id), None)
    if not todo_to_delete:
        raise HTTPException(status_code=404, detail="Todo not found")
    fake_todo_db.remove(todo_to_delete)
    return

@app.delete("/api/todos/completed", status_code=204)
async def delete_completed():
    fake_todo_db[:] = [todo for todo in fake_todo_db if not todo.completed]
    return
@app.delete("/api/todos", status_code=204)
async def delete_all_todos():
    fake_todo_db.clear()
    return

@app.get("/")
async def root():
    return {"message": "FastAPI To-Do Backend is running!"}
