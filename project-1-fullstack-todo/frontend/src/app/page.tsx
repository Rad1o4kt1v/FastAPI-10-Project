'use client'; // This directive is necessary for using React hooks

import { useState, useEffect, FormEvent } from 'react';
import axios from 'axios';

// Define the type for a single To-Do item to match the backend
interface Todo {
  id: string;
  task: string;
  completed: boolean;
}

// The base URL of our FastAPI backend
const API_URL = 'http://localhost:8000/api/todos';

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTask, setNewTask] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
const handleClearAll = async () => {
  try {
    await axios.delete(API_URL); // DELETE http://localhost:8000/api/todos
    setTodos([]); // очистить локальный список
  } catch (error) {
    console.error('Error clearing all tasks:', error);
  }
};

  // 1. Fetch all todos from the backend when the component mounts
  useEffect(() => {
    const fetchTodos = async () => {
      try {
        const response = await axios.get(API_URL);
        setTodos(response.data);
      } catch (error) {
        console.error('Error fetching todos:', error);
      }
    };
    fetchTodos();
  }, []); // Empty dependency array means this runs once on mount

  // 2. Handle form submission to add a new task
  const handleAddTask = async (e: FormEvent) => {
    e.preventDefault(); // Prevent page reload
    if (!newTask.trim()) return; // Don't add empty tasks

    try {
      const response = await axios.post(API_URL, { task: newTask });
      setTodos([...todos, response.data]); // Add new task to the list
      setNewTask(''); // Clear the input field
    } catch (error) {
      console.error('Error adding task:', error);
    }
  };

  // 3. Handle toggling the completed status of a task
  const handleToggleComplete = async (id: string) => {
  try {
    const response = await axios.patch(`${API_URL}/${id}`);
    setTodos(todos.map(todo => (todo.id === id ? response.data : todo)));
  } catch (error) {
    console.error('Error updating task:', error);
  }
};
const handleEditSave = async (id: string) => {
  try {
    await axios.put(`${API_URL}/${id}`, { task: editText });
    setTodos(todos.map(todo => todo.id === id ? { ...todo, task: editText } : todo));
    setEditingId(null);
    setEditText('');
  } catch (error) {
    console.error('Error updating task:', error);
  }
};


  // 4. Handle deleting a task
  const handleDeleteTask = async (id: string) => {
    try {
      await axios.delete(`${API_URL}/${id}`)
      setTodos(todos.filter(todo => todo.id !== id)); // Remove task from the list
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  return (
      <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800 text-white p-8 transition-all duration-500">
      <div className="w-full max-w-md bg-gray-800 p-6 rounded-lg shadow-lg">
        <h1 className="text-4xl font-extrabold mb-6 text-center text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 drop-shadow-lg">
  ⚡ Full-Stack To-Do List
</h1>

<button
  onClick={handleClearAll}
  className="mb-4 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition-colors"
>
  🗑️ Clear All Tasks
</button>

        {/* Form to add a new task */}
        <form onSubmit={handleAddTask} className="flex gap-2 mb-6">
          <input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Add a new task..."
            className="flex-grow p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
          <button
            type="submit"
            className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors"
          >
            Add
          </button>
        </form>

        {/* List of tasks */}
<ul className="space-y-3 transition-all duration-500 ease-in-out">
          {todos.map((todo) => (
            <li
              key={todo.id}
              className="flex items-center justify-between p-3 bg-gray-700 rounded-md"
            >
              {editingId === todo.id ? (
  <input
    value={editText}
    onChange={(e) => setEditText(e.target.value)}
    onKeyDown={(e) => e.key === 'Enter' && handleEditSave(todo.id)}
    className="flex-grow p-1 mr-2 bg-gray-600 rounded text-white"
    autoFocus
  />
) : (
  <span
    onClick={() => handleToggleComplete(todo.id)}
    className={`cursor-pointer flex-grow ${todo.completed ? 'line-through text-gray-500' : ''}`}
  >
    {todo.task}
  </span>
)}

{editingId === todo.id ? (
  <button
    onClick={() => handleEditSave(todo.id)}
    className="bg-green-600 hover:bg-green-700 text-white text-xs font-bold py-1 px-2 rounded ml-2"
  >
    Save
  </button>
) : (
  <>
    <button
      onClick={() => {
        setEditingId(todo.id);
        setEditText(todo.task);
      }}
      className="bg-yellow-500 hover:bg-yellow-600 text-white text-xs font-bold py-1 px-2 rounded mr-1"
    >
      Edit
    </button>
  </>
)}

              <button
                onClick={() => handleDeleteTask(todo.id)}
                className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold py-1 px-2 rounded-full transition-colors"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}