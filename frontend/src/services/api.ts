import axios from 'axios'
import type { UserProfile, Product, AnalysisResult } from '../types'

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
      product_barcode: productBarcode,
    })
    return res.data.response
  },
}

export default api
