import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Leaf, ScanLine, User, MessageSquare, Menu, X } from 'lucide-react'

const navLinks = [
  { href: '/scan', label: 'Scan', icon: ScanLine },
  { href: '/profile', label: 'Profile', icon: User },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const hasProfile = !!localStorage.getItem('user_id')

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  useEffect(() => setMenuOpen(false), [location.pathname])

  return (
    <>
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: scrolled ? 'rgba(255,255,255,0.95)' : 'transparent',
        backdropFilter: scrolled ? 'blur(12px)' : 'none',
        borderBottom: scrolled ? '1px solid #e5e7eb' : 'none',
        transition: 'all 0.3s ease',
        padding: '0 1rem',
      }}>
        <div style={{
          maxWidth: 1200, margin: '0 auto',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          height: 64,
        }}>
          {/* Logo */}
          <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 8 }}>
            <motion.div
              whileHover={{ rotate: 20 }}
              style={{
                width: 36, height: 36, borderRadius: 10,
                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Leaf size={20} color="white" />
            </motion.div>
            <span style={{ fontWeight: 700, fontSize: 18, color: '#111827' }}>
              Food<span style={{ color: '#22c55e' }}>Truth</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }} className="desktop-nav">
            {hasProfile ? (
              navLinks.map(({ href, label, icon: Icon }) => (
                <Link key={href} to={href} style={{ textDecoration: 'none' }}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      padding: '8px 14px', borderRadius: 8,
                      background: location.pathname === href ? '#f0fdf4' : 'transparent',
                      color: location.pathname === href ? '#16a34a' : '#374151',
                      fontWeight: location.pathname === href ? 600 : 500,
                      fontSize: 14, transition: 'all 0.2s',
                    }}
                  >
                    <Icon size={16} />
                    {label}
                  </motion.div>
                </Link>
              ))
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/profile-setup')}
                style={{
                  background: '#22c55e', color: 'white', border: 'none',
                  padding: '10px 20px', borderRadius: 8, fontWeight: 600,
                  fontSize: 14, cursor: 'pointer',
                }}
              >
                Get Started
              </motion.button>
            )}
          </div>

          {/* Mobile hamburger */}
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={() => setMenuOpen(v => !v)}
            style={{
              display: 'none', background: 'none', border: 'none',
              padding: 8, cursor: 'pointer', color: '#374151',
            }}
            className="hamburger"
          >
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </motion.button>
        </div>
      </nav>

      {/* Mobile menu drawer */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed', top: 64, left: 0, right: 0, zIndex: 99,
              background: 'white', borderBottom: '1px solid #e5e7eb',
              padding: '1rem',
              boxShadow: '0 8px 30px rgba(0,0,0,0.1)',
            }}
          >
            {hasProfile ? navLinks.map(({ href, label, icon: Icon }) => (
              <Link key={href} to={href} style={{ textDecoration: 'none' }}>
                <motion.div
                  whileTap={{ scale: 0.97 }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    padding: '14px 16px', borderRadius: 10, marginBottom: 4,
                    background: location.pathname === href ? '#f0fdf4' : 'transparent',
                    color: location.pathname === href ? '#16a34a' : '#374151',
                    fontWeight: location.pathname === href ? 600 : 500,
                    fontSize: 16,
                  }}
                >
                  <Icon size={20} />
                  {label}
                </motion.div>
              </Link>
            )) : (
              <Link to="/profile-setup" style={{ textDecoration: 'none' }}>
                <motion.div
                  whileTap={{ scale: 0.97 }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    padding: '14px', borderRadius: 10,
                    background: '#22c55e', color: 'white',
                    fontWeight: 600, fontSize: 16,
                  }}
                >
                  Get Started
                </motion.div>
              </Link>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @media (max-width: 640px) {
          .desktop-nav { display: none !important; }
          .hamburger { display: flex !important; }
        }
      `}</style>
    </>
  )
}
