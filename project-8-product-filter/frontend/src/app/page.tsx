'use client';

import { useState, useEffect, ChangeEvent, useRef } from 'react';
import axios from 'axios';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
}

const API_URL = 'http://localhost:8000/api';

export default function Home() {
  // Состояния для данных
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);

  // Состояния для фильтров
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sort, setSort] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState(searchTerm);

  // Состояние загрузки
  const [loading, setLoading] = useState(true);

  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  // Загрузка категорий один раз при монтировании компонента
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${API_URL}/categories`);
        setCategories(['All', ...response.data]);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
    fetchCategories();
  }, []);

  // Основной эффект для загрузки продуктов при изменении фильтров
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (debouncedSearch) params.append('search', debouncedSearch);
        if (selectedCategory && selectedCategory !== 'All') params.append('category', selectedCategory);
        if (sort) params.append('sort', sort);
        if (minPrice) params.append('min_price', minPrice);
        if (maxPrice) params.append('max_price', maxPrice);
        const response = await axios.get(`${API_URL}/products?${params.toString()}`);
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [debouncedSearch, selectedCategory, sort, minPrice, maxPrice]);

  // Debouncing для поиска
  useEffect(() => {
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    debounceTimeout.current = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 400);
    return () => {
      if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    };
  }, [searchTerm]);

  return (
    <div className="bg-gray-50 min-h-screen">
      <header className="bg-white shadow-sm p-4">
        <div className="container mx-auto">
          <h1 className="text-3xl font-bold text-gray-800">Каталог товаров</h1>
        </div>
      </header>

      <main className="container mx-auto p-4">
        {/* Панель фильтров */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 bg-white p-4 rounded-lg shadow">
          <input
            type="text"
            placeholder="Поиск по названию..."
            value={searchTerm}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
            className="p-2 border rounded-md w-full"
          />
          <select
            value={selectedCategory}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => setSelectedCategory(e.target.value)}
            className="p-2 border rounded-md w-full"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <input
              type="number"
              min="0"
              value={minPrice}
              onChange={e => setMinPrice(e.target.value)}
              placeholder="Мин. цена"
              className="p-2 border rounded-md w-full"
            />
            <input
              type="number"
              min="0"
              value={maxPrice}
              onChange={e => setMaxPrice(e.target.value)}
              placeholder="Макс. цена"
              className="p-2 border rounded-md w-full"
            />
          </div>
          <select
            value={sort}
            onChange={e => setSort(e.target.value)}
            className="p-2 border rounded-md w-full"
          >
            <option value="">Без сортировки</option>
            <option value="price_asc">По цене: сначала дешевые</option>
            <option value="price_desc">По цене: сначала дорогие</option>
          </select>
        </div>

        {/* Сетка товаров */}
        {loading ? (
          <p className="text-center">Загрузка товаров...</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.length > 0 ? products.map(product => (
              <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden transform hover:-translate-y-1 transition-transform duration-300">
                <div className="p-6">
                  <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded-full">{product.category}</span>
                  <h2 className="text-xl font-bold text-gray-800 mt-2 h-16">{product.name}</h2>
                  <p className="text-2xl font-light text-blue-600 mt-4">${product.price}</p>
                </div>
              </div>
            )) : (
              <p className="col-span-full text-center">Товары не найдены.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}