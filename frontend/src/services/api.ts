/**
 * Centralized Axios API client with JWT injection and error handling.
 */
import axios, {AxiosInstance, InternalAxiosRequestConfig} from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = process.env.REACT_NATIVE_API_URL ?? 'http://localhost:5000/api';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {'Content-Type': 'application/json'},
});

api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = await AsyncStorage.getItem('jwt_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      AsyncStorage.removeItem('jwt_token');
    }
    return Promise.reject(error);
  },
);

// ── Auth ──────────────────────────────────────────
export const authApi = {
  register: (email: string, password: string, name: string) =>
    api.post('/auth/register', {email, password, name}),
  login: (email: string, password: string) =>
    api.post('/auth/login', {email, password}),
  me: () => api.get('/auth/me'),
};

// ── Profile ───────────────────────────────────────
export const profileApi = {
  get: () => api.get('/profile'),
  save: (data: Record<string, unknown>) => api.post('/profile', data),
};

// ── Product ───────────────────────────────────────
export const productApi = {
  getByBarcode: (barcode: string) => api.get(`/product/${barcode}`),
  scan: (barcode: string) => api.post('/scan', {barcode}),
  analyze: (barcode: string) => api.post('/analyze', {barcode}),
  recommendations: (category?: string) =>
    api.get('/recommendations', {params: category ? {category} : {}}),
};

// ── Chat ──────────────────────────────────────────
export const chatApi = {
  getHistory: () => api.get('/history'),
  getConversation: (id: number) => api.get(`/history/${id}`),
  deleteConversation: (id: number) => api.delete(`/history/${id}`),
  deleteAllHistory: () => api.delete('/history'),
};

/**
 * Streams a chat response using the Fetch API (Axios does not support streaming).
 * Returns an async generator yielding text chunks.
 */
export async function* streamChat(
  message: string,
  conversationId: number | null,
  barcode: string | null,
  token: string,
): AsyncGenerator<string> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      barcode,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat failed: ${response.status}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder('utf-8');

  while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    yield decoder.decode(value, {stream: true});
  }
}

export default api;
