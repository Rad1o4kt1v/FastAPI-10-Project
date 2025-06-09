# app/main.py
from fastapi import FastAPI
from app.rate_limiter import RateLimiterMiddleware
from app.logger import setup_logger
from app.database import init_db

setup_logger()

app = FastAPI(title="FastAPI Rate Limit")

# Настраиваемые лимиты
app.add_middleware(
    RateLimiterMiddleware,
    redis_url="redis://localhost:6379",
    limit=5,
    window_sec=60
)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"msg": "Rate limited API"}
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    rate_limit: int = 5
    rate_window: int = 60

    model_config = {
        "env_file": ".env"
    }

settings = Settings()
