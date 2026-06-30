import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import LandingPage from './pages/LandingPage'
import ProfileSetupPage from './pages/ProfileSetupPage'
import ScanPage from './pages/ScanPage'
import ResultsPage from './pages/ResultsPage'
import ProfileEditPage from './pages/ProfileEditPage'
import ChatPage from './pages/ChatPage'

function RequireProfile({ children }: { children: React.ReactNode }) {
  const userId = localStorage.getItem('user_id')
  if (!userId) return <Navigate to="/profile-setup" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/profile-setup" element={<ProfileSetupPage />} />
          <Route path="/scan" element={
            <RequireProfile><ScanPage /></RequireProfile>
          } />
          <Route path="/results/:barcode" element={
            <RequireProfile><ResultsPage /></RequireProfile>
          } />
          <Route path="/profile" element={
            <RequireProfile><ProfileEditPage /></RequireProfile>
          } />
          <Route path="/chat" element={
            <RequireProfile><ChatPage /></RequireProfile>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}
