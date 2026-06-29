// Shared TypeScript types for the Food Truth Teller app

export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface UserProfile {
  user_id: number;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  weight_kg?: number;
  height_cm?: number;
  bmi?: number;
  health_conditions: string[];
  allergies: string[];
  diet_preference?: string;
  goals: string[];
  updated_at?: string;
}

export interface NutritionPer100g {
  energy_kcal?: number;
  proteins_g?: number;
  carbohydrates_g?: number;
  sugars_g?: number;
  fat_g?: number;
  saturated_fat_g?: number;
  fiber_g?: number;
  sodium_mg?: number;
  salt_g?: number;
}

export interface Product {
  id: number;
  barcode: string;
  name: string;
  brand?: string;
  category?: string;
  ingredients_text?: string;
  ingredients_parsed: Array<{ text: string; id: string }>;
  nutrition_per_100g: NutritionPer100g;
  image_url?: string;
  is_vegetarian: boolean;
  is_vegan: boolean;
  nutriscore_grade?: 'a' | 'b' | 'c' | 'd' | 'e';
  nova_group?: 1 | 2 | 3 | 4;
  allergens: string[];
  additives: string[];
  labels: string[];
  source: string;
  created_at: string;
}

export interface AnalysisIssue {
  ingredient: string;
  reason: string;
}

export interface AnalysisResult {
  prediction: 'Safe' | 'Caution' | 'Avoid';
  confidence: number;
  issues: AnalysisIssue[];
  all_flags: Array<{
    category: string;
    detected_ingredients: string[];
    risk_reasons: string[];
    severity: 'high' | 'medium' | 'low';
  }>;
  nutriscore?: string;
  nova_group?: number;
  is_vegetarian: boolean;
  is_vegan: boolean;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  product_barcode?: string;
  message_count: number;
  created_at: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface ProfileState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

export interface ProductState {
  currentProduct: Product | null;
  analysis: AnalysisResult | null;
  recommendations: Product[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatState {
  conversations: Conversation[];
  currentConversationId: number | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
}

export type RootStackParamList = {
  Auth: undefined;
  Login: undefined;
  Register: undefined;
  Main: undefined;
  Profile: undefined;
  Scanner: undefined;
  ProductDetail: { barcode: string };
  Chat: { barcode?: string; conversationId?: number };
  History: undefined;
  Recommendations: undefined;
};
