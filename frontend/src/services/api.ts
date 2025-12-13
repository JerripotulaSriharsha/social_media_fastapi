import axios from 'axios';
import type { AuthResponse, LoginRequest, RegisterRequest, Post } from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  register: async (data: RegisterRequest) => {
    const response = await api.post<{ id: string; email: string }>('/auth/register', data);
    return response.data;
  },

  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<AuthResponse>('/auth/login', formData);
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

export const postService = {
  uploadPost: async (file: File, caption: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', caption);

    const response = await api.post<Post>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getFeed: async () => {
    const response = await api.get<{ posts: Post[] }>('/feed');
    return response.data.posts;
  },

  updatePost: async (postId: string, caption?: string, file?: File) => {
    const formData = new FormData();
    if (caption !== undefined) {
      formData.append('caption', caption);
    }
    if (file) {
      formData.append('file', file);
    }

    const response = await api.put<Post>(`/posts/${postId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deletePost: async (postId: string) => {
    const response = await api.delete<{ success: boolean; message: string }>(`/posts/${postId}`);
    return response.data;
  },
};

export default api;
