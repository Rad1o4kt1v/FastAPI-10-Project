'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface Post {
  slug: string;
  title: string;
  author: string;
  date: string;
  category: string;
}

const API_URL = 'http://localhost:8000/api/posts';

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string | null>(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await axios.get(API_URL);
        setPosts(response.data);
      } catch (error) {
        console.error('Ошибка при получении постов:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchPosts();
  }, []);

  const categories = Array.from(new Set(posts.map((p) => p.category)));
  const filteredPosts = filter ? posts.filter((p) => p.category === filter) : posts;

  return (
    <main className="flex flex-col items-center min-h-screen bg-gray-100 p-8">
      <div className="w-full max-w-2xl">
        <h1 className="text-5xl font-bold mb-8 text-center text-gray-800">
          Минималистичный Блог
        </h1>

        {/* Категории */}
        {/* Категории */}
<div className="flex flex-wrap gap-2 mb-6 justify-center">
  {categories.map((cat) => (
    <button
      key={cat}
      onClick={() => setFilter(cat)}
      className={`px-3 py-1 rounded-full border ${
        filter === cat
          ? 'bg-blue-700 text-white border-blue-700'
          : 'bg-white text-blue-700 border-blue-300'
      } hover:bg-blue-100 transition`}
    >
      {cat}
    </button>
  ))}

  {filter && (
    <button
      onClick={() => setFilter(null)}
      className="px-3 py-1 rounded-full border border-gray-400 bg-gray-200 text-gray-800 hover:bg-gray-300 transition"
    >
      Показать все
    </button>
  )}
</div>

        {loading ? (
          <p>Загрузка постов...</p>
        ) : (
          <div className="space-y-4">
            {filteredPosts.map((post) => (
              <Link
                key={post.slug}
                href={`/posts/${post.slug}`}
                className="block p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow"
              >
                <h2 className="text-2xl font-semibold text-blue-600">{post.title}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Автор: {post.author} | {post.date}
                </p>
                <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                  {post.category}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
