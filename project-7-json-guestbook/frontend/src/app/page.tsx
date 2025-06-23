'use client';

import { useState, useEffect, FormEvent } from 'react';
import axios from 'axios';
import { FaTrash, FaEdit, FaSave, FaTimes } from 'react-icons/fa';

interface Entry {
  id: string;
  name: string;
  message: string;
  timestamp: string; // Дата придет как строка в формате ISO
}

const API_URL = 'http://localhost:8000/api/entries';

export default function Home() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editMessage, setEditMessage] = useState('');
  const [page, setPage] = useState(1);
  const [limit] = useState(5);
  const [hasMore, setHasMore] = useState(true);

  const fetchEntries = async (pageNum = page) => {
    try {
      const response = await axios.get(`${API_URL}?page=${pageNum}&limit=${limit}`);
      // Сортировка не нужна, backend уже возвращает нужную страницу
      setEntries(response.data);
      setHasMore(response.data.length === limit);
    } catch (err) {
      setError('Не удалось загрузить записи.');
    }
  };

  useEffect(() => {
    fetchEntries(page);
    // eslint-disable-next-line
  }, [page]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !message.trim()) {
      setError('Имя и сообщение не могут быть пустыми.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post(API_URL, { name, message });
      // Очищаем поля и перезагружаем записи
      setName('');
      setMessage('');
      fetchEntries();
    } catch (err) {
      setError('Ошибка при отправке сообщения.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Удалить эту запись?')) return;
    try {
      await axios.delete(`${API_URL}/${id}`);
      fetchEntries();
    } catch {
      setError('Ошибка при удалении записи.');
    }
  };

  const handleEdit = (entry: Entry) => {
    setEditingId(entry.id);
    setEditMessage(entry.message);
  };

  const handleEditCancel = () => {
    setEditingId(null);
    setEditMessage('');
  };

  const handleEditSave = async (id: string) => {
    if (!editMessage.trim()) {
      setError('Сообщение не может быть пустым.');
      return;
    }
    try {
      await axios.put(`${API_URL}/${id}`, { message: editMessage });
      setEditingId(null);
      setEditMessage('');
      fetchEntries();
    } catch {
      setError('Ошибка при редактировании записи.');
    }
  };

  return (
    <main className="bg-gray-100 min-h-screen p-4 sm:p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Гостевая Книга</h1>

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-2xl font-semibold mb-4">Оставить запись</h2>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <div className="mb-4">
            <label htmlFor="name" className="block text-gray-700 mb-1">Ваше имя</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="Аноним"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="message" className="block text-gray-700 mb-1">Сообщение</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              rows={3}
              placeholder="Всем привет!"
            ></textarea>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300">
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>

        <div className="space-y-4">
          {entries.map(entry => (
            <div key={entry.id} className="bg-white p-4 rounded-lg shadow relative">
              {editingId === entry.id ? (
                <>
                  <textarea
                    className="w-full px-3 py-2 border rounded-md mb-2"
                    value={editMessage}
                    onChange={e => setEditMessage(e.target.value)}
                    rows={3}
                  />
                  <div className="flex gap-2 justify-end">
                    <button onClick={() => handleEditSave(entry.id)} className="bg-green-500 text-white px-3 py-1 rounded flex items-center gap-1"><FaSave />Сохранить</button>
                    <button onClick={handleEditCancel} className="bg-gray-400 text-white px-3 py-1 rounded flex items-center gap-1"><FaTimes />Отмена</button>
                  </div>
                </>
              ) : (
                <>
                  <p className="text-gray-800">{entry.message}</p>
                  <div className="text-right text-sm text-gray-500 mt-2">
                    <strong>- {entry.name}</strong> в {new Date(entry.timestamp).toLocaleString()}
                  </div>
                  <div className="absolute top-2 right-2 flex gap-2">
                    <button onClick={() => handleEdit(entry)} className="text-blue-500 hover:text-blue-700" title="Редактировать"><FaEdit /></button>
                    <button onClick={() => handleDelete(entry.id)} className="text-red-500 hover:text-red-700" title="Удалить"><FaTrash /></button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Назад
          </button>
          <span>Страница {page}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={!hasMore}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Вперед
          </button>
        </div>
      </div>
    </main>
  );
}