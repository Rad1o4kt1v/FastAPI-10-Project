import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from threading import Lock

app = FastAPI()

# --- Настройка CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "polls.json"
polls: List[dict] = []
poll_id_counter = 1
lock = Lock()

def load_polls():
    global polls, poll_id_counter
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            polls_data = json.load(f)
            polls = polls_data if isinstance(polls_data, list) else []
            if polls:
                poll_id_counter = max(p["id"] for p in polls) + 1
    else:
        polls = []
        poll_id_counter = 1

def save_polls():
    with open("polls.json", "r", encoding="utf-8-sig") as f:
        polls_data = json.load(f)

# --- Pydantic модели ---
class PollCreate(BaseModel):
    question: str
    options: List[str]

class Poll(BaseModel):
    id: int
    question: str
    options: List[str]
    votes: List[int]

@app.on_event("startup")
def startup_event():
    load_polls()

@app.get("/api/poll/{poll_id}", response_model=Poll)
def get_poll(poll_id: int):
    for poll in polls:
        if poll["id"] == poll_id:
            return poll
    raise HTTPException(status_code=404, detail="Poll not found")

@app.get("/api/polls", response_model=List[Poll])
def get_all_polls():
    return polls

@app.post("/api/poll/create", response_model=Poll)
def create_poll(poll: PollCreate):
    global poll_id_counter
    with lock:
        new_poll = {
            "id": poll_id_counter,
            "question": poll.question,
            "options": poll.options,
            "votes": [0] * len(poll.options)
        }
        polls.append(new_poll)
        poll_id_counter += 1
        save_polls()
    return new_poll

@app.post("/api/poll/{poll_id}/vote/{option_idx}", response_model=Poll)
def vote_poll(poll_id: int, option_idx: int):
    with lock:
        for poll in polls:
            if poll["id"] == poll_id:
                if 0 <= option_idx < len(poll["votes"]):
                    poll["votes"][option_idx] += 1
                    save_polls()
                    return poll
                else:
                    raise HTTPException(status_code=400, detail="Invalid option index")
        raise HTTPException(status_code=404, detail="Poll not found")