export interface UserProfile {
  id: number
  name: string
  age?: number
  gender?: string
  weight?: number
  diseases: string[]
  allergies: string[]
  diet_type: 'vegetarian' | 'non-vegetarian' | 'vegan'
  created_at?: string
}

export interface Product {
  id?: number
  barcode: string
  product_name: string
  brand?: string
  ingredients?: string
  category?: string
  is_vegetarian?: number
  is_vegan?: number
  per_100g_sugar?: number
  per_100g_sodium?: number
  image_url?: string
}

export type Rating = 'safe' | 'caution' | 'avoid'

export interface AnalysisResult {
  rating: Rating
  confidence: number
  probabilities: {
    safe: number
    caution: number
    avoid: number
  }
  reasons: string[]
  product: Product
  user_name: string
  ml_used: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'bot'
  content: string
  timestamp: string
}

export const DISEASES_OPTIONS = [
  { value: 'diabetes', label: 'Diabetes' },
  { value: 'bp', label: 'High Blood Pressure' },
  { value: 'celiac', label: 'Celiac Disease' },
  { value: 'lactose intolerance', label: 'Lactose Intolerance' },
  { value: 'heart disease', label: 'Heart Issues' },
  { value: 'kidney disease', label: 'Kidney Issues' },
]

export const ALLERGIES_OPTIONS = [
  { value: 'nuts', label: 'Nuts / Peanuts' },
  { value: 'gluten', label: 'Gluten' },
  { value: 'dairy', label: 'Dairy' },
  { value: 'eggs', label: 'Eggs' },
  { value: 'soy', label: 'Soy' },
]

export const DIET_OPTIONS = [
  { value: 'non-vegetarian', label: 'Non-Vegetarian' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
]
