'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import type { FormEvent } from 'react';

const API_URL = 'http://localhost:8000/api';

export default function CreatePollPage() {
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState(['', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleOptionChange = (idx: number, value: string) => {
    setOptions((prev: string[]) => prev.map((opt: string, i: number) => (i === idx ? value : opt)));
  };

  const addOption = () => {
    setOptions((prev: string[]) => [...prev, '']);
  };

  const removeOption = (idx: number) => {
    if (options.length <= 2) return;
    setOptions((prev: string[]) => prev.filter((opt: string, i: number) => i !== idx));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    if (!question.trim() || options.some(opt => !opt.trim())) {
      setError('Заполните вопрос и все варианты ответа.');
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API_URL}/poll/create`, {
        question,
        options: options.map(opt => opt.trim()),
      });
      router.push('/');
    } catch (err) {
      setError('Ошибка при создании опроса.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-100 font-sans">
      <form onSubmit={handleSubmit} className="w-full max-w-xl p-8 space-y-6 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center text-gray-800">Создать новый опрос</h1>
        <div>
          <label className="block font-semibold mb-2">Вопрос</label>
          <input
            type="text"
            className="w-full border rounded-lg px-3 py-2"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block font-semibold mb-2">Варианты ответа</label>
          {options.map((opt, idx) => (
            <div key={idx} className="flex items-center mb-2">
              <input
                type="text"
                className="flex-1 border rounded-lg px-3 py-2"
                value={opt}
                onChange={e => handleOptionChange(idx, e.target.value)}
                required
              />
              {options.length > 2 && (
                <button type="button" onClick={() => removeOption(idx)} className="ml-2 text-red-500 font-bold text-xl">&times;</button>
              )}
            </div>
          ))}
          <button type="button" onClick={addOption} className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-lg">Добавить вариант</button>
        </div>
        {error && <div className="text-red-500 text-center">{error}</div>}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition-colors"
        >
          {loading ? 'Создание...' : 'Создать опрос'}
        </button>
      </form>
    </main>
  );
} 