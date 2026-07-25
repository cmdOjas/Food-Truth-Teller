import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ScanLine, ChevronDown, ChevronUp, MessageSquare, ArrowLeft, Package, AlertTriangle, CheckCircle } from 'lucide-react'
import Navbar from '../components/Navbar'
import NutriScore from '../components/NutriScore'
import { analyzeApi, productApi, intakeApi } from '../services/api'
import { useTheme } from '../context/ThemeContext'
import type { AnalysisResult, Product, Rating } from '../types'

const RATING_CONFIG: Record<Rating, { color: string; bg: string; light: string; dark: string; emoji: string; label: string }> = {
  safe: { color: '#16a34a', bg: 'linear-gradient(135deg, #22c55e, #16a34a)', light: '#f0fdf4', dark: '#0d2318', emoji: '✅', label: 'SAFE' },
  caution: { color: '#d97706', bg: 'linear-gradient(135deg, #f59e0b, #d97706)', light: '#fffbeb', dark: '#1f1a08', emoji: '⚠️', label: 'CAUTION' },
  avoid: { color: '#dc2626', bg: 'linear-gradient(135deg, #ef4444, #dc2626)', light: '#fee2e2', dark: '#1f0a0a', emoji: '🚫', label: 'AVOID' },
}

function ProductBrowse() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    productApi.list().then(setProducts).finally(() => setLoading(false))
  }, [])

  return (
    <div style={{ minHeight: '100vh', background: theme.pageBg }}>
      <Navbar />
      <div style={{ paddingTop: 80, maxWidth: 700, margin: '0 auto', padding: '80px 1rem 2rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <button
            onClick={() => navigate('/scan')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, color: theme.textMuted, marginBottom: 20, padding: '4px 0' }}
          >
            <ArrowLeft size={18} /> Back to Scan
          </button>

          <h1 style={{ fontSize: 24, fontWeight: 800, color: theme.text, marginBottom: 6 }}>
            Sample Products
          </h1>
          <p style={{ color: theme.textMuted, marginBottom: 24 }}>Click any product to get your personalized health analysis.</p>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: theme.textSubtle }}>Loading products...</div>
          ) : (
            <div style={{ display: 'grid', gap: 12 }}>
              {products.map((p, i) => (
                <motion.button
                  key={p.barcode}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigate(`/results/${p.barcode}`)}
                  style={{
                    padding: '16px', borderRadius: 14,
                    border: `1px solid ${theme.cardBorder}`,
                    background: theme.cardBg, cursor: 'pointer', textAlign: 'left',
                    display: 'flex', alignItems: 'center', gap: 14,
                    boxShadow: theme.isDark ? '0 2px 8px rgba(0,0,0,0.25)' : '0 2px 8px rgba(0,0,0,0.04)',
                  }}
                >
                  {p.image_url ? (
                    <img src={p.image_url} alt={p.product_name}
                      style={{ width: 52, height: 52, objectFit: 'cover', borderRadius: 10, flexShrink: 0 }}
                      onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
                    />
                  ) : (
                    <div style={{ width: 52, height: 52, borderRadius: 10, background: theme.pageBg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Package size={24} color={theme.textSubtle} />
                    </div>
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: 15, color: theme.text, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {p.product_name}
                    </div>
                    <div style={{ fontSize: 13, color: theme.textMuted }}>{p.brand} · {p.category}</div>
                  </div>
                  <div style={{ fontSize: 13, color: theme.green, fontWeight: 600, flexShrink: 0 }}>Analyze →</div>
                </motion.button>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default function ResultsPage() {
  const { barcode } = useParams<{ barcode: string }>()
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showIngredients, setShowIngredients] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [alreadyLogged, setAlreadyLogged] = useState(false)
  const [logging, setLogging] = useState(false)

  if (barcode === 'browse') return <ProductBrowse />

  useEffect(() => {
    if (!barcode) return
    const userId = localStorage.getItem('user_id')
    if (!userId) { navigate('/profile-setup'); return }

    setLoading(true)
    setError('')
    analyzeApi
      .analyze(parseInt(userId), barcode)
      .then(setResult)
      .catch(err => {
        if (err?.response?.data?.error) {
          setError(err.response.data.error)
        } else if (err?.code === 'ECONNABORTED' || err?.message?.includes('timeout')) {
          setError('Request timed out. The product lookup is taking too long — please try again.')
        } else if (!err?.response) {
          setError('Cannot reach the server. Make sure the backend is running and try again.')
        } else {
          setError('Something went wrong analyzing this product. Please try again.')
        }
      })
      .finally(() => setLoading(false))

    // Check whether this exact product was already logged today, so the
    // "Going to eat this?" prompt can show the "✓ Logged" state immediately.
    intakeApi.today(parseInt(userId))
      .then(summary => {
        setAlreadyLogged(summary.logged_products.some(p => p.barcode === barcode))
      })
      .catch(() => { /* non-critical — leave the prompt in its default state */ })
  }, [barcode])

  const handleLogIntake = async () => {
    if (!barcode || !result) return
    const userId = localStorage.getItem('user_id')
    if (!userId) return
    setLogging(true)
    try {
      await intakeApi.log(parseInt(userId), barcode, result.product)
      setAlreadyLogged(true)
    } catch {
      setError('Could not log this product. Please try again.')
    } finally {
      setLogging(false)
    }
  }

  useEffect(() => {
    return () => { window.speechSynthesis?.cancel() }
  }, [])

  const toggleSpeak = (reasons: string[]) => {
    if (speaking) {
      window.speechSynthesis?.cancel()
      setSpeaking(false)
      return
    }
    if (!window.speechSynthesis) return
    const text = reasons
      .map(r => r.replace(/[^\x00-\x7F]/g, '').trim())
      .filter(Boolean)
      .join('. ')
    const utter = new SpeechSynthesisUtterance(text)
    utter.onend = () => setSpeaking(false)
    utter.onerror = () => setSpeaking(false)
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utter)
    setSpeaking(true)
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: theme.pageBg }}>
        <Navbar />
        <div style={{ paddingTop: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: 'center' }}>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              style={{
                width: 60, height: 60, borderRadius: '50%', margin: '0 auto 16px',
                border: `4px solid ${theme.cardBorder}`,
                borderTop: `4px solid ${theme.green}`,
              }}
            />
            <p style={{ color: theme.textMuted, fontSize: 16, fontWeight: 500 }}>Analyzing product...</p>
            <p style={{ color: theme.textSubtle, fontSize: 14, marginTop: 4 }}>Checking against your health profile</p>
          </motion.div>
        </div>
      </div>
    )
  }

  if (error) {
    const isServerDown = error.includes('Cannot reach') || error.includes('timed out')
    return (
      <div style={{ minHeight: '100vh', background: theme.pageBg }}>
        <Navbar />
        <div style={{ paddingTop: 80, maxWidth: 500, margin: '0 auto', padding: '80px 1rem 2rem', textAlign: 'center' }}>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
            <AlertTriangle size={56} color={isServerDown ? '#dc2626' : '#f59e0b'} style={{ marginBottom: 16 }} />
            <h2 style={{ fontSize: 22, fontWeight: 700, color: theme.text, marginBottom: 8 }}>
              {isServerDown ? 'Connection Error' : 'Product Not Found'}
            </h2>
            <p style={{ color: theme.textMuted, marginBottom: 24, lineHeight: 1.6 }}>{error}</p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={() => navigate('/scan')}
                style={{
                  padding: '12px 28px', borderRadius: 10, border: 'none',
                  background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                  color: 'white', fontWeight: 700, fontSize: 15, cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(34,197,94,0.3)',
                }}
              >
                Try Another Barcode
              </button>
              <button
                onClick={() => navigate('/results/browse')}
                style={{
                  padding: '12px 28px', borderRadius: 10,
                  border: `2px solid ${theme.cardBorder}`,
                  background: theme.cardBg,
                  color: theme.text, fontWeight: 600, fontSize: 15, cursor: 'pointer',
                }}
              >
                Browse Sample Products
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    )
  }

  if (!result) return null

  const { rating, product, reasons, confidence, probabilities } = result
  const cfg = RATING_CONFIG[rating]

  return (
    <div style={{ minHeight: '100vh', background: theme.pageBg }}>
      <Navbar />
      <div style={{ paddingTop: 80, maxWidth: 640, margin: '0 auto', padding: '80px 1rem 3rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Back button */}
          <button
            onClick={() => navigate('/scan')}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 6,
              color: theme.textMuted, marginBottom: 20, padding: '4px 0', fontSize: 15,
            }}
          >
            <ArrowLeft size={18} /> Scan Another
          </button>

          {/* Product Header */}
          <div style={{
            background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
            boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
            border: `1px solid ${theme.cardBorder}`,
            marginBottom: 16, display: 'flex', gap: 16, alignItems: 'flex-start',
          }}>
            {product.image_url ? (
              <img src={product.image_url} alt={product.product_name}
                style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 14, flexShrink: 0 }}
                onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
            ) : (
              <div style={{ width: 80, height: 80, borderRadius: 14, background: theme.pageBg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Package size={36} color={theme.textSubtle} />
              </div>
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <h1 style={{ fontSize: 19, fontWeight: 800, color: theme.text, lineHeight: 1.3, marginBottom: 4 }}>
                {product.product_name}
              </h1>
              <p style={{ color: theme.textMuted, fontSize: 14, marginBottom: 6 }}>
                {product.brand} · {product.category}
              </p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {product.per_100g_sugar != null && (
                  <span style={{ background: theme.pageBg, color: theme.textMuted, padding: '2px 8px', borderRadius: 999, fontSize: 12, border: `1px solid ${theme.cardBorder}` }}>
                    Sugar: {product.per_100g_sugar}g/100g
                  </span>
                )}
                {product.per_100g_sodium != null && (
                  <span style={{ background: theme.pageBg, color: theme.textMuted, padding: '2px 8px', borderRadius: 999, fontSize: 12, border: `1px solid ${theme.cardBorder}` }}>
                    Sodium: {product.per_100g_sodium}mg/100g
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Rating Badge */}
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15, delay: 0.15 }}
            style={{
              background: cfg.bg, borderRadius: 20, padding: '2rem 1.5rem',
              marginBottom: 16, textAlign: 'center', position: 'relative', overflow: 'hidden',
            }}
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 300, delay: 0.3 }}
              style={{ fontSize: 68, marginBottom: 8, filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.25))' }}
            >
              {cfg.emoji}
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              style={{ color: 'white', fontSize: 34, fontWeight: 900, letterSpacing: '0.06em', textShadow: '0 2px 8px rgba(0,0,0,0.2)' }}
            >
              {cfg.label}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14, marginTop: 6, fontWeight: 500 }}
            >
              for {result.user_name} · {Math.round(confidence * 100)}% confidence
            </motion.p>

            {/* Probability bars */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              style={{ display: 'flex', gap: 8, marginTop: 16, justifyContent: 'center' }}
            >
              {(['safe', 'caution', 'avoid'] as Rating[]).map((r) => (
                <div key={r} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)', marginBottom: 4, textTransform: 'uppercase', fontWeight: 600 }}>
                    {r}
                  </div>
                  <div style={{ width: 60, height: 4, background: 'rgba(255,255,255,0.3)', borderRadius: 2, overflow: 'hidden' }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${probabilities[r] * 100}%` }}
                      transition={{ delay: 0.7, duration: 0.6 }}
                      style={{ height: '100%', background: 'white', borderRadius: 2 }}
                    />
                  </div>
                  <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.9)', marginTop: 3, fontWeight: 700 }}>
                    {Math.round(probabilities[r] * 100)}%
                  </div>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Reasons */}
          <div style={{
            background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
            boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
            border: `1px solid ${theme.cardBorder}`,
            marginBottom: 16,
          }}>
            <p style={{ fontSize: 13, color: theme.textSubtle, marginBottom: 10, fontStyle: 'italic' }}>
              According to your health profile, this is your result
            </p>
            <h3 style={{ fontWeight: 700, fontSize: 17, color: theme.text, marginBottom: 14 }}>
              Why this rating?
            </h3>
            <div>
              {reasons.map((reason, i) => {
                const borderColor = reason.startsWith('🚫') ? '#ef4444'
                  : reason.startsWith('⚠️') ? '#f59e0b'
                  : reason.startsWith('✅') ? '#22c55e'
                  : theme.cardBorder
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -15 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.1 }}
                    style={{
                      padding: '10px 12px',
                      marginBottom: i < reasons.length - 1 ? 8 : 0,
                      borderRadius: 8,
                      borderLeft: `3px solid ${borderColor}`,
                      background: theme.isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
                    }}
                  >
                    <p style={{ fontSize: 14, color: theme.text, lineHeight: 1.6, margin: 0 }}>{reason}</p>
                  </motion.div>
                )
              })}
            </div>
            {/* Voice button */}
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => toggleSpeak(reasons)}
              style={{
                marginTop: 14, padding: '9px 18px', borderRadius: 8, border: `1.5px solid ${theme.cardBorder}`,
                background: speaking ? (theme.isDark ? '#1a4a28' : '#dcfce7') : theme.cardBg,
                color: speaking ? theme.green : theme.textMuted,
                fontWeight: 600, fontSize: 14, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
              }}
            >
              {speaking ? '⏹ Stop' : '🔊 Hear Reason'}
            </motion.button>
          </div>

          {/* Nutri-Score (universal nutritional quality — separate from the
              personalized Safe/Caution/Avoid analysis above) */}
          {result.nutri_score && <NutriScore data={result.nutri_score} />}

          {/* Going to eat this? — logs nutrients to today's running total */}
          <div style={{
            background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
            boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
            border: `1px solid ${theme.cardBorder}`,
            marginBottom: 16, textAlign: 'center',
          }}>
            {alreadyLogged ? (
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                color: theme.green, fontWeight: 700, fontSize: 15,
              }}>
                <CheckCircle size={20} /> Logged
              </div>
            ) : (
              <>
                <p style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>
                  Going to eat this?
                </p>
                <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={handleLogIntake}
                    disabled={logging}
                    style={{
                      padding: '12px 24px', borderRadius: 12, border: 'none',
                      background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                      color: 'white', fontWeight: 700, fontSize: 15,
                      cursor: logging ? 'default' : 'pointer',
                      opacity: logging ? 0.7 : 1,
                      boxShadow: '0 4px 15px rgba(34,197,94,0.3)',
                    }}
                  >
                    {logging ? 'Logging...' : 'Yes, log it'}
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.97 }}
                    disabled={logging}
                    style={{
                      padding: '12px 24px', borderRadius: 12,
                      border: `2px solid ${theme.cardBorder}`,
                      background: 'transparent', color: theme.textMuted,
                      fontWeight: 700, fontSize: 15, cursor: 'pointer',
                    }}
                  >
                    Not now
                  </motion.button>
                </div>
              </>
            )}
          </div>

          {/* Ingredients accordion */}
          {product.ingredients && (
            <motion.div
              style={{
                background: theme.cardBg, borderRadius: 20,
                boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
                border: `1px solid ${theme.cardBorder}`,
                marginBottom: 16, overflow: 'hidden',
              }}
            >
              <button
                onClick={() => setShowIngredients(v => !v)}
                style={{
                  width: '100%', padding: '1.25rem 1.5rem', background: 'none', border: 'none',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}
              >
                <span style={{ fontWeight: 700, fontSize: 16, color: theme.text }}>
                  Full Ingredient List
                </span>
                {showIngredients ? <ChevronUp size={20} color={theme.textMuted} /> : <ChevronDown size={20} color={theme.textMuted} />}
              </button>
              <AnimatePresence>
                {showIngredients && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div style={{ padding: '0 1.5rem 1.5rem' }}>
                      <p style={{ fontSize: 14, color: theme.textMuted, lineHeight: 1.8 }}>
                        {product.ingredients}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: 10 }}>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/scan')}
              style={{
                flex: 1, padding: '14px', borderRadius: 12,
                border: `2px solid ${theme.cardBorder}`,
                background: theme.cardBg, color: theme.text,
                fontWeight: 700, fontSize: 15, cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              }}
            >
              <ScanLine size={18} /> Scan Another
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate(`/chat?barcode=${barcode}`)}
              style={{
                flex: 1, padding: '14px', borderRadius: 12, border: 'none',
                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                color: 'white', fontWeight: 700, fontSize: 15, cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                boxShadow: '0 4px 15px rgba(34,197,94,0.3)',
              }}
            >
              <MessageSquare size={18} /> Ask AI About This Product
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
