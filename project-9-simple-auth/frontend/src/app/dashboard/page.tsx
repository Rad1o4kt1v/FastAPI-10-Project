'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const API_URL = 'http://localhost:8000/api';

export default function DashboardPage() {
  const [secretMessage, setSecretMessage] = useState('');
  const [adminMessage, setAdminMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userRole = localStorage.getItem('user_role');
    
    if (!token) {
      router.push('/login');
      return;
    }

    setIsAdmin(userRole === 'admin');

    const fetchData = async () => {
      try {
        // Получаем обычные данные
        const secretResponse = await axios.get(`${API_URL}/secret-data`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSecretMessage(secretResponse.data.message);

        // Если админ, получаем админ-данные
        if (userRole === 'admin') {
          const adminResponse = await axios.get(`${API_URL}/admin-data`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          setAdminMessage(adminResponse.data.message);
        }
      } catch (error) {
        // Если токен невалидный, разлогиниваем
        handleLogout();
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const handleLogout = async () => {
    const token = localStorage.getItem('auth_token');
    try {
      // Вызываем logout на сервере
      await axios.post(`${API_URL}/logout`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (error) {
      console.error('Ошибка при выходе:', error);
    }
    // Очищаем локальное хранилище
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_role');
    router.push('/login');
  };

  if (loading) {
    return <p className="text-center mt-10">Загрузка...</p>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">Защищенная Панель</h1>
      <p className="mt-4 text-xl p-4 bg-green-100 border border-green-400 rounded-md">{secretMessage}</p>
      
      {isAdmin && (
        <div className="mt-4">
          <h2 className="text-2xl font-bold text-black">Админ-панель</h2>
          <p className="mt-2 text-xl p-4 bg-yellow-300 text-black border-2 border-yellow-600 rounded-md">
            {adminMessage}
          </p>
        </div>
      )}

      <button onClick={handleLogout} className="mt-6 bg-red-500 text-white p-2 rounded hover:bg-red-600">
        Выйти
      </button>
    </div>
  );
}