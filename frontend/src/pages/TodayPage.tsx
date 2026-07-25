import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Package, X, ScanLine } from 'lucide-react'
import Navbar from '../components/Navbar'
import IntakeRing from '../components/IntakeRing'
import { intakeApi } from '../services/api'
import { useTheme } from '../context/ThemeContext'
import type { IntakeSummary } from '../types'

function formatDate(dateStr: string): string {
  // dateStr is 'YYYY-MM-DD'; render as a local, human-friendly date without
  // shifting days due to timezone parsing of a bare date string.
  const [y, m, d] = dateStr.split('-').map(Number)
  const date = new Date(y, (m || 1) - 1, d || 1)
  return date.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })
}

export default function TodayPage() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [summary, setSummary] = useState<IntakeSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const userId = parseInt(localStorage.getItem('user_id') || '0')

  useEffect(() => {
    if (!userId) { navigate('/profile-setup'); return }
    intakeApi.today(userId)
      .then(setSummary)
      .catch(() => setError('Could not load today\'s intake. Please try again.'))
      .finally(() => setLoading(false))
  }, [userId])

  const handleDelete = async (logId: number) => {
    setDeletingId(logId)
    try {
      const updated = await intakeApi.deleteLog(userId, logId)
      setSummary(updated)
    } catch {
      setError('Could not remove that entry. Please try again.')
    } finally {
      setDeletingId(null)
    }
  }

  const cardStyle = {
    background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
    boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
    border: `1px solid ${theme.cardBorder}`,
    marginBottom: 16,
  }

  return (
    <div style={{ minHeight: '100vh', background: theme.pageBg }}>
      <Navbar />
      <div style={{ paddingTop: 80, maxWidth: 640, margin: '0 auto', padding: '80px 1rem 3rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Header */}
          <div style={{ marginBottom: 20 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, color: theme.text, marginBottom: 4 }}>
              Today's Intake
            </h1>
            <p style={{ color: theme.textMuted, fontSize: 14 }}>
              {summary ? formatDate(summary.date) : ''}
            </p>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: theme.textSubtle }}>
              Loading today's intake...
            </div>
          ) : error ? (
            <div style={{
              background: theme.isDark ? '#1f0a0a' : '#fee2e2',
              color: '#dc2626', padding: '12px 16px', borderRadius: 10, fontSize: 14,
            }}>
              {error}
            </div>
          ) : summary && (
            <>
              {/* Summary line */}
              <p style={{ color: theme.textMuted, fontSize: 14, marginBottom: 16 }}>
                You've consumed <strong style={{ color: theme.text }}>{Math.round(summary.totals.calories)} kcal</strong> today
                {' '}({Math.round(summary.percentages.calories)}% of daily goal).
              </p>

              {/* Rings */}
              <div style={cardStyle}>
                <style>{`
                  @media (max-width: 480px) {
                    .intake-rings-grid { grid-template-columns: repeat(2, 1fr) !important; }
                  }
                `}</style>
                <div className="intake-rings-grid" style={{
                  display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16,
                  width: '100%', justifyItems: 'center',
                }}>
                  <IntakeRing
                    label="Calories"
                    current={summary.totals.calories}
                    limit={summary.limits.calories}
                    percentage={summary.percentages.calories}
                    unit=""
                  />
                  <IntakeRing
                    label="Sodium"
                    current={summary.totals.sodium_mg}
                    limit={summary.limits.sodium_mg}
                    percentage={summary.percentages.sodium_mg}
                    unit="mg"
                  />
                  <IntakeRing
                    label="Sugar"
                    current={summary.totals.sugar_g}
                    limit={summary.limits.sugar_g}
                    percentage={summary.percentages.sugar_g}
                    unit="g"
                  />
                  <IntakeRing
                    label="Sat. Fat"
                    current={summary.totals.saturated_fat_g}
                    limit={summary.limits.saturated_fat_g}
                    percentage={summary.percentages.saturated_fat_g}
                    unit="g"
                  />
                </div>
              </div>

              {/* Logged products list */}
              <div style={cardStyle}>
                <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>
                  Logged Today
                </h3>

                {summary.logged_products.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
                    <ScanLine size={32} color={theme.textSubtle} style={{ margin: '0 auto 10px' }} />
                    <p style={{ color: theme.textSubtle, fontSize: 14 }}>
                      Nothing logged yet today. Scan a product to begin.
                    </p>
                  </div>
                ) : (
                  <AnimatePresence initial={false}>
                    {summary.logged_products.map(item => (
                      <motion.div
                        key={item.id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 12,
                          padding: '10px 4px',
                          borderBottom: `1px solid ${theme.cardBorder}`,
                        }}
                      >
                        <div style={{
                          width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                          background: theme.pageBg,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <Package size={18} color={theme.textSubtle} />
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{
                            fontSize: 14, fontWeight: 600, color: theme.text,
                            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                          }}>
                            {item.product_name}
                          </div>
                        </div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: theme.textMuted, flexShrink: 0 }}>
                          {Math.round(item.calories)} kcal
                        </div>
                        <motion.button
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleDelete(item.id)}
                          disabled={deletingId === item.id}
                          style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            padding: 4, flexShrink: 0,
                            color: theme.textSubtle,
                            opacity: deletingId === item.id ? 0.5 : 1,
                          }}
                        >
                          <X size={16} />
                        </motion.button>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
}
