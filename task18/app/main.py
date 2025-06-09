from fastapi import FastAPI
from app.logger import setup_logger
from app.database import init_db
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(title="FastAPI + Monitoring")

# Прометеус метрики
instrumentator = Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting application...")
    await init_db()
    logger.info("✅ Database initialized")

@app.get("/health")
async def health():
    logger.info("🔍 /health check called")
    return {"status": "ok"}

@app.get("/")
def root():
    logger.info("📥 Root endpoint accessed")
    return {"msg": "Monitoring enabled"}
