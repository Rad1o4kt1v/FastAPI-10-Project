from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import uvicorn
# Конфигурация базы данных
DATABASE_URL = "postgresql://dtc_clean:12345pass@localhost:5432/dtc_clean_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Конфигурация Passlib для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модель SQLAlchemy для пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Pydantic модели
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функции хеширования
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Эндпоинт регистрации
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

# Эндпоинт логина
@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

# Скрипт миграции существующих паролей
@app.post("/migrate-passwords")
async def migrate_passwords(db: Session = Depends(get_db)):
    users = db.query(User).all()
    for user in users:
        # Предполагаем, что пароли в открытом виде имеют длину меньше 60 символов
        # (хеши bcrypt имеют фиксированную длину 60 символов)
        if len(user.hashed_password) < 60:
            hashed_password = get_password_hash(user.hashed_password)
            user.hashed_password = hashed_password
    db.commit()
    return {"message": "Password migration completed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)