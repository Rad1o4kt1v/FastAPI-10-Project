from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated, Dict, Optional
import uuid
from datetime import datetime, timedelta

app = FastAPI()

# --- CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Фейковые данные ---
FAKE_USERS = {
    "user": {"username": "user", "password": "password", "role": "user"},
    "admin": {"username": "admin", "password": "adminpass", "role": "admin"},
}
TOKENS: Dict[str, Dict[str, str | datetime]] = {}  # token: {"username": str, "role": str, "created": datetime}
TOKEN_LIFETIME = timedelta(hours=1)

# --- Модель ответа для токена ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Зависимость для проверки токена и роли ---
async def get_current_user(authorization: Annotated[Optional[str], Header()] = None, required_role: Optional[str] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    token = authorization.split(" ", 1)[1]
    token_data = TOKENS.get(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # Проверка времени жизни токена
    if datetime.utcnow() - token_data["created"] > TOKEN_LIFETIME:
        del TOKENS[token]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    if required_role and token_data["role"] != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return token_data

# --- Эндпоинты API ---

@app.post("/api/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    for user in FAKE_USERS.values():
        if form_data.username == user["username"] and form_data.password == user["password"]:
            token = str(uuid.uuid4())
            TOKENS[token] = {"username": user["username"], "role": user["role"], "created": datetime.utcnow()}
            return {"access_token": token, "token_type": "bearer", "role": user["role"]}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/api/logout")
async def logout(authorization: Annotated[Optional[str], Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    token = authorization.split(" ", 1)[1]
    if token in TOKENS:
        del TOKENS[token]
    return {"detail": "Logged out"}

@app.get("/api/secret-data")
async def get_secret_data(user=Depends(get_current_user)):
    return {"message": f"Привет, {user['username']}! Секретное сообщение: 42."}

@app.get("/api/admin-data")
async def get_admin_data(user=Depends(lambda authorization: get_current_user(authorization, required_role="admin"))):
    return {"message": f"Привет, {user['username']}! Это админ-панель."}