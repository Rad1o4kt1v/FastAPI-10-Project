'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Poll {
  id: number;
  question: string;
  options: string[];
  votes: number[];
}

const API_URL = 'http://localhost:8000/api';

export default function Home() {
  const [polls, setPolls] = useState<Poll[]>([]);
  const [selectedPollId, setSelectedPollId] = useState<number | null>(null);
  const [pollData, setPollData] = useState<Poll | null>(null);
  const [votedOption, setVotedOption] = useState<number | null>(null);

  // Получить список опросов
  const fetchPolls = async () => {
    try {
      const response = await axios.get(`${API_URL}/polls`);
      setPolls(response.data);
      if (response.data.length > 0 && selectedPollId === null) {
        setSelectedPollId(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch polls:', error);
    }
  };

  // Получить данные выбранного опроса
  const fetchPollData = async (pollId: number) => {
    try {
      const response = await axios.get(`${API_URL}/poll/${pollId}`);
      setPollData(response.data);
    } catch (error) {
      setPollData(null);
      console.error('Failed to fetch poll data:', error);
    }
  };

  // Polling для списка опросов
  useEffect(() => {
    fetchPolls();
    const intervalId = setInterval(fetchPolls, 3000);
    return () => clearInterval(intervalId);
  }, []);

  // Polling для выбранного опроса
  useEffect(() => {
    if (selectedPollId !== null) {
      fetchPollData(selectedPollId);
      const intervalId = setInterval(() => fetchPollData(selectedPollId), 3000);
      return () => clearInterval(intervalId);
    }
  }, [selectedPollId]);

  // Проверка localStorage для защиты от повторного голосования
  useEffect(() => {
    if (selectedPollId !== null) {
      const voted = localStorage.getItem(`poll_voted_${selectedPollId}`);
      setVotedOption(voted ? parseInt(voted) : null);
    }
  }, [selectedPollId, pollData]);

  const handleVote = async (optionIdx: number) => {
    if (votedOption !== null || !pollData) return;
    try {
      const response = await axios.post(`${API_URL}/poll/${pollData.id}/vote/${optionIdx}`);
      setPollData(response.data);
      setVotedOption(optionIdx);
      localStorage.setItem(`poll_voted_${pollData.id}`, optionIdx.toString());
    } catch (error) {
      console.error('Failed to cast vote:', error);
    }
  };

  return (
    <main className="flex flex-col items-center min-h-screen bg-gray-100 font-sans p-4">
      <div className="w-full max-w-2xl p-8 space-y-6 bg-white rounded-xl shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-800">Опросы</h1>
          <a href="/create" className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">Создать опрос</a>
        </div>
        {polls.length === 0 ? (
          <p className="text-center text-gray-500">Нет доступных опросов.</p>
        ) : (
          <div className="mb-6">
            <label className="block font-semibold mb-2">Выберите опрос:</label>
            <select
              className="w-full border rounded-lg px-3 py-2"
              value={selectedPollId ?? ''}
              onChange={e => setSelectedPollId(Number(e.target.value))}
            >
              {polls.map(poll => (
                <option key={poll.id} value={poll.id}>{poll.question}</option>
              ))}
            </select>
          </div>
        )}
        {pollData ? (
          <>
            <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">{pollData.question}</h2>
            <div className="space-y-4">
              {pollData.options.map((option, idx) => {
                const totalVotes = pollData.votes.reduce((sum, v) => sum + v, 0);
                const percentage = totalVotes > 0 ? (pollData.votes[idx] / totalVotes) * 100 : 0;
                return (
                  <div key={idx}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold text-gray-700">{option}</span>
                      <span className="text-sm font-medium text-gray-500">{pollData.votes[idx]} голосов ({percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-8">
                      <div
                        className="bg-blue-500 h-8 rounded-full transition-all duration-500 ease-in-out text-white flex items-center px-2"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <button
                      onClick={() => handleVote(idx)}
                      disabled={votedOption !== null}
                      className={`w-full mt-2 py-2 text-white font-semibold rounded-lg transition-colors ${
                        votedOption !== null ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'
                      } ${votedOption === idx ? '!bg-blue-700' : ''}`}
                    >
                      {votedOption === idx ? 'Ваш голос' : 'Голосовать'}
                    </button>
                  </div>
                );
              })}
            </div>
            <div className="text-center text-gray-600 font-bold pt-4 border-t">
              Всего голосов: {pollData.votes.reduce((sum, v) => sum + v, 0)}
            </div>
          </>
        ) : selectedPollId !== null ? (
          <p className="text-center text-gray-500">Загрузка данных опроса...</p>
        ) : null}
      </div>
    </main>
  );
}