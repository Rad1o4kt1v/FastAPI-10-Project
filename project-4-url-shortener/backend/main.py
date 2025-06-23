import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Структура: {short_code: {"long_url": str, "clicks": int, "created_at": datetime}}
url_db = {}

class URLCreate(BaseModel):
    long_url: HttpUrl
    custom_code: str | None = None  # необязательный кастомный код

@app.post("/api/shorten")
def create_short_url(url_data: URLCreate, request: Request):
    long_url = str(url_data.long_url)
    custom_code = url_data.custom_code

    # если указан кастомный код
    if custom_code:
        if custom_code in url_db:
            raise HTTPException(status_code=400, detail="Этот короткий код уже занят.")
        short_code = custom_code
    else:
        short_code = secrets.token_urlsafe(5)
        while short_code in url_db:
            short_code = secrets.token_urlsafe(5)

    url_db[short_code] = {
        "long_url": long_url,
        "clicks": 0,
        "created_at": datetime.utcnow()
    }

    short_url = f"{request.base_url}{short_code}"
    return {
        "short_url": short_url,
        "clicks": 0
    }

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    item = url_db.get(short_code)
    if not item:
        raise HTTPException(status_code=404, detail="Ссылка не найдена.")

    # Проверка срока действия (30 дней)
    ttl = timedelta(days=30)
    if datetime.utcnow() - item["created_at"] > ttl:
        raise HTTPException(status_code=404, detail="Срок действия ссылки истёк.")

    item["clicks"] += 1
    return RedirectResponse(url=item["long_url"])

@app.get("/api/info/{short_code}")
def get_click_info(short_code: str):
    item = url_db.get(short_code)
    if not item:
        raise HTTPException(status_code=404, detail="Ссылка не найдена.")
    return {
        "long_url": item["long_url"],
        "clicks": item["clicks"],
        "created_at": item["created_at"]
    }
