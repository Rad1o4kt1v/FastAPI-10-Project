import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
print("🔑 API_KEY:", API_KEY)

app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

@app.get("/api/weather/{city}")
async def get_weather(city: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_BASE_URL, params=params)

    if response.status_code != 200:
        detail = response.json().get("message", "Error fetching weather data")
        raise HTTPException(status_code=response.status_code, detail=detail)

    data = response.json()

    return {
        "city_name": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }

@app.get("/api/forecast/{city}")
async def get_forecast(city: str):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_BASE_URL, params=params)

    if response.status_code != 200:
        detail = response.json().get("message", "Error fetching forecast")
        raise HTTPException(status_code=response.status_code, detail=detail)

    data = response.json()
    forecast_data = [
        {
            "datetime": item["dt_txt"],
            "temperature": item["main"]["temp"],
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        }
        for item in data["list"] if "12:00:00" in item["dt_txt"]  # Только дневной прогноз
    ]

    return forecast_data

@app.get("/api/weather/coords")
async def get_weather_by_coords(lat: float = Query(...), lon: float = Query(...)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_BASE_URL, params=params)

    if response.status_code != 200:
        detail = response.json().get("message", "Error fetching weather data")
        raise HTTPException(status_code=response.status_code, detail=detail)

    data = response.json()

    return {
        "city_name": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }
