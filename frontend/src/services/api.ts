import axios from 'axios'
import type { UserProfile, Product, AnalysisResult, ChatMessage, IntakeSummary } from '../types'

const API_BASE = (import.meta as any).env?.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export const profileApi = {
  create: async (data: Omit<UserProfile, 'id'>): Promise<UserProfile> => {
    const res = await api.post('/user/profile', data)
    return res.data.user
  },

  update: async (data: UserProfile): Promise<UserProfile> => {
    const res = await api.post('/user/profile', { ...data, user_id: data.id })
    return res.data.user
  },

  get: async (id: number): Promise<UserProfile> => {
    const res = await api.get(`/user/${id}`)
    return res.data.user
  },
}

export const productApi = {
  getByBarcode: async (barcode: string): Promise<{ product: Product; source: string }> => {
    const res = await api.get(`/product/${barcode}`)
    return res.data
  },

  list: async (): Promise<Product[]> => {
    const res = await api.get('/products')
    return res.data.products
  },
}

export const analyzeApi = {
  analyze: async (userId: number, barcode: string): Promise<AnalysisResult> => {
    const res = await api.post('/analyze', { user_id: userId, barcode })
    return res.data
  },
}

export const chatApi = {
  send: async (userId: number, message: string, productBarcode?: string): Promise<string> => {
    const res = await api.post('/chat', {
      user_id: userId,
      message,
      barcode: productBarcode,
      product_barcode: productBarcode, // backward-compatible key
    })
    return res.data.reply ?? res.data.response
  },

  history: async (userId: number, productBarcode?: string): Promise<ChatMessage[]> => {
    const res = await api.get('/chat/history', {
      params: { user_id: userId, barcode: productBarcode || 'general' },
    })
    return (res.data.messages || []).map((m: any) => ({
      id: String(m.id),
      role: m.role === 'bot' ? 'bot' : 'user',
      content: m.content,
      timestamp: m.timestamp,
    })) as ChatMessage[]
  },

  clear: async (userId: number, productBarcode?: string): Promise<void> => {
    await api.post('/chat/clear', {
      user_id: userId,
      barcode: productBarcode || 'general',
    })
  },
}

export const intakeApi = {
  log: async (userId: number, barcode: string, product?: Product): Promise<IntakeSummary> => {
    const res = await api.post('/intake/log', { user_id: userId, barcode, product })
    return res.data
  },

  today: async (userId: number): Promise<IntakeSummary> => {
    const res = await api.get('/intake/today', { params: { user_id: userId } })
    return res.data
  },

  deleteLog: async (userId: number, logId: number): Promise<IntakeSummary> => {
    const res = await api.delete(`/intake/log/${logId}`, { data: { user_id: userId } })
    return res.data
  },
}

export default api
