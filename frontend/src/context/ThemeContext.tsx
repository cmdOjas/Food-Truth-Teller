import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export interface Theme {
  pageBg: string
  cardBg: string
  cardBorder: string
  text: string
  textMuted: string
  textSubtle: string
  green: string
  greenDark: string
  greenBg: string
  greenBgStrong: string
  navBg: string
  navBorder: string
  inputBg: string
  inputBorder: string
  btnSecBg: string
  btnSecBorder: string
  btnSecText: string
  heroGradient: string
  featuresGradient: string
  pillBg: string
  pillText: string
  stepNumBg: string
  stepNumText: string
  isDark: boolean
}

const lightTheme: Theme = {
  pageBg: '#f9fafb',
  cardBg: '#ffffff',
  cardBorder: '#e5e7eb',
  text: '#111827',
  textMuted: '#6b7280',
  textSubtle: '#9ca3af',
  green: '#22c55e',
  greenDark: '#16a34a',
  greenBg: '#f0fdf4',
  greenBgStrong: '#dcfce7',
  navBg: 'rgba(255,255,255,0.95)',
  navBorder: '#e5e7eb',
  inputBg: '#ffffff',
  inputBorder: '#e5e7eb',
  btnSecBg: '#ffffff',
  btnSecBorder: '#e5e7eb',
  btnSecText: '#374151',
  heroGradient: 'linear-gradient(160deg, #f0fdf4 0%, #ffffff 50%, #f0fdf4 100%)',
  featuresGradient: 'linear-gradient(160deg, #f0fdf4 0%, #dcfce7 100%)',
  pillBg: '#f3f4f6',
  pillText: '#6b7280',
  stepNumBg: '#f3f4f6',
  stepNumText: '#6b7280',
  isDark: false,
}

const darkTheme: Theme = {
  pageBg: '#0f172a',
  cardBg: '#1e293b',
  cardBorder: '#334155',
  text: '#f1f5f9',
  textMuted: '#94a3b8',
  textSubtle: '#64748b',
  green: '#4ade80',
  greenDark: '#22c55e',
  greenBg: '#0d2318',
  greenBgStrong: '#122d1c',
  navBg: 'rgba(15,23,42,0.97)',
  navBorder: '#1e293b',
  inputBg: '#1e293b',
  inputBorder: '#334155',
  btnSecBg: '#1e293b',
  btnSecBorder: '#334155',
  btnSecText: '#e2e8f0',
  heroGradient: 'linear-gradient(160deg, #0d1f0f 0%, #0f172a 50%, #0d1f0f 100%)',
  featuresGradient: 'linear-gradient(160deg, #0d1f0f 0%, #0a1a10 100%)',
  pillBg: '#1e293b',
  pillText: '#94a3b8',
  stepNumBg: '#1e293b',
  stepNumText: '#94a3b8',
  isDark: true,
}

interface ThemeContextType {
  theme: Theme
  mode: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType>({
  theme: lightTheme,
  mode: 'light',
  toggleTheme: () => {},
})

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<'light' | 'dark'>(() => {
    return (localStorage.getItem('theme') as 'light' | 'dark') || 'light'
  })

  const theme = mode === 'dark' ? darkTheme : lightTheme

  useEffect(() => {
    document.body.style.background = theme.pageBg
    document.body.style.color = theme.text
    localStorage.setItem('theme', mode)
  }, [mode, theme])

  const toggleTheme = () => setMode(m => (m === 'light' ? 'dark' : 'light'))

  return (
    <ThemeContext.Provider value={{ theme, mode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
