from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# --- CORS ---
origins = ["http://localhost:3000", "http://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class PostBase(BaseModel):
    slug: str
    title: str

class PostFull(BaseModel):
    title: str
    slug: str
    content: str
    author: str
    date: str
    category: str

# --- In-memory DB ---
fake_posts_db = [
    {
        "title": "Первый пост",
        "slug": "first-post",
        "content": "# Привет, мир!\n\nЭто мой первый пост на блоге.",
        "author": "Айгерим",
        "date": "2025-06-23",
        "category": "Общее"
    },
    {
        "title": "Второй пост",
        "slug": "second-post",
        "content": "## Второй пост\n\nКонтент второго поста в Markdown.",
        "author": "Жанна",
        "date": "2025-06-24",
        "category": "Технологии"
    }
]
@app.get("/api/posts", response_model=List[PostFull])  # 🟢 обновили тут
async def get_all_posts():
    return fake_posts_db


@app.get("/api/posts/{slug}", response_model=PostFull)
async def get_post_by_slug(slug: str):
    for post in fake_posts_db:
        if post["slug"] == slug:
            return post
    raise HTTPException(status_code=404, detail="Пост не найден")

@app.get("/")
async def root():
    return {"message": "Blog API is running"}
