export type SensitivityLevel = 'low' | 'medium' | 'high'

export interface UserProfile {
  id: number
  name: string
  age?: number
  gender?: string
  weight?: number
  diseases: string[]
  allergies: string[]
  diet_type: 'vegetarian' | 'non-vegetarian' | 'vegan'
  sensitivity: SensitivityLevel
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

export type NutriGrade = 'A' | 'B' | 'C' | 'D' | 'E'

export interface NutriScore {
  grade: NutriGrade
  score: number
  negative_points: number
  positive_points: number
  breakdown: {
    energy_points: number
    sugars_points: number
    saturated_fat_points: number
    sodium_points: number
    fiber_points: number
    protein_points: number
    fruits_veg_points: number
  }
  is_beverage: boolean
  data_completeness: 'full' | 'partial' | 'minimal'
  insufficient_data?: boolean
}

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
  nutri_score?: NutriScore
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

export const SENSITIVITY_OPTIONS: { value: SensitivityLevel; label: string; description: string }[] = [
  {
    value: 'low',
    label: 'Low',
    description: 'Only warns when a product clearly goes well past the health limit. Good if you just want general awareness, not frequent alerts.',
  },
  {
    value: 'medium',
    label: 'Medium',
    description: 'Warns right at the official health limit. Balanced for most people. (Recommended default)',
  },
  {
    value: 'high',
    label: 'High',
    description: 'Warns earlier, before the official limit is reached — extra safety margin for serious or hard-to-control conditions.',
  },
]
