'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import ReactMarkdown from 'react-markdown';

interface Post {
  slug: string;
  title: string;
  content: string;
  author: string;
  date: string;
  category: string;
}

const API_URL = 'http://localhost:8000/api/posts';

export default function PostPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await axios.get(`${API_URL}/${slug}`);
        setPost(response.data);
      } catch (error) {
        console.error(`Error fetching post ${slug}:`, error);
      } finally {
        setLoading(false);
      }
    };

    if (slug) fetchPost();
  }, [slug]);

  if (loading) return <div className="text-center p-10">Загрузка...</div>;
  if (!post) return <div className="text-center p-10">Пост не найден</div>;

  return (
    <article className="max-w-3xl mx-auto p-8">
      <Link href="/" className="text-blue-500 hover:underline mb-8 block">
        &larr; Назад ко всем постам
      </Link>
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">{post.title}</h1>
      <p className="text-sm text-gray-500 mb-4">
        Автор: {post.author} | {post.date}
      </p>
      <span className="inline-block mb-6 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
        {post.category}
      </span>

      <div className="prose lg:prose-xl text-gray-700">
        <ReactMarkdown>{post.content}</ReactMarkdown>
      </div>
    </article>
  );
}
  