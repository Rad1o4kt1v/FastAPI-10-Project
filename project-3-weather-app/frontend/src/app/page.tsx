// frontend/src/app/page.tsx
'use client';

import { useEffect, useState, FormEvent } from 'react';
import axios from 'axios';
import Image from 'next/image';

interface WeatherData {
  city_name: string;
  temperature: number;
  description: string;
  icon: string;
}

interface ForecastItem {
  date: string;
  temperature: number;
  icon: string;
}

const BASE_URL = 'http://localhost:8000/api';

export default function Home() {
  const [city, setCity] = useState('Almaty');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchAllWeather = async (cityName: string) => {
    setLoading(true);
    setError('');
    try {
      const [weatherRes, forecastRes] = await Promise.all([
        axios.get(`${BASE_URL}/weather/${cityName}`),
        axios.get(`${BASE_URL}/forecast/${cityName}`),
      ]);
      setWeather(weatherRes.data);
      setForecast(forecastRes.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
      setWeather(null);
      setForecast([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchByCoords = async (lat: number, lon: number) => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get(`${BASE_URL}/weather/coords`, {
        params: { lat, lon }
      });
      setWeather(res.data);
      setCity(res.data.city_name);
      fetchForecast(res.data.city_name);
    } catch (err: any) {
      setError('Ошибка по геолокации');
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async (cityName: string) => {
    try {
      const res = await axios.get(`${BASE_URL}/forecast/${cityName}`);
      setForecast(res.data);
    } catch {
      setForecast([]);
    }
  };

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          fetchByCoords(pos.coords.latitude, pos.coords.longitude);
        },
        () => fetchAllWeather(city),
        { timeout: 5000 }
      );
    } else {
      fetchAllWeather(city);
    }
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (city.trim()) {
      fetchAllWeather(city.trim());
    }
  };

  return (
    <main className="flex flex-col items-center min-h-screen bg-gradient-to-br from-blue-100 to-blue-300 p-4">
      <div className="w-full max-w-md bg-white/70 backdrop-blur-md p-6 rounded-2xl shadow-lg">
        <h1 className="text-2xl font-bold text-center mb-4">Погода</h1>

        <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Введите город"
            className="flex-grow p-2 rounded-lg border border-gray-300 text-black"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 text-white p-2 rounded-lg"
          >
            {loading ? '...' : '➔'}
          </button>
        </form>

        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        {weather && (
          <div className="text-center">
            <h2 className="text-3xl font-semibold mb-2">{weather.city_name}</h2>
            <div className="flex items-center justify-center">
              <p className="text-5xl font-light">{Math.round(weather.temperature)}°C</p>
              <Image
                src={`https://openweathermap.org/img/wn/${weather.icon}@2x.png`}
                alt={weather.description}
                width={80}
                height={80}
              />
            </div>
            <p className="text-lg capitalize">{weather.description}</p>
          </div>
        )}

        {forecast.length > 0 && (
          <div className="mt-6">
            <h3 className="text-xl font-semibold mb-2 text-center">Прогноз на 5 дней</h3>
            <div className="grid grid-cols-2 gap-4">
              {forecast.map((item, i) => (
                <div key={i} className="bg-white/90 p-2 rounded-lg text-center">
                  <p className="text-sm font-medium">{item.date}</p>
                  <Image
                    src={`https://openweathermap.org/img/wn/${item.icon}@2x.png`}
                    alt="icon"
                    width={60}
                    height={60}
                    className="mx-auto"
                  />
                  <p>{Math.round(item.temperature)}°C</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
