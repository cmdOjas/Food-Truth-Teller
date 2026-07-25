import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Package, ChevronRight } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import type { AlternativeProduct } from '../types'

export default function AlternativesRow({ items }: { items: AlternativeProduct[] }) {
  const { theme } = useTheme()
  const navigate = useNavigate()

  if (!items || items.length === 0) return null

  return (
    <div style={{
      background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
      boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
      border: `1px solid ${theme.cardBorder}`,
      marginBottom: 16,
    }}>
      <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>
        Better options for you
      </h3>

      <div style={{
        display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 4,
        scrollSnapType: 'x proximity',
      }}>
        {items.map(item => (
          <motion.button
            key={item.barcode}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate(`/results/${item.barcode}`)}
            style={{
              flex: '0 0 auto', width: 160, textAlign: 'left', cursor: 'pointer',
              border: `1px solid ${theme.cardBorder}`, borderRadius: 14,
              background: theme.inputBg, padding: 12, scrollSnapAlign: 'start',
              display: 'flex', flexDirection: 'column', gap: 8,
            }}
          >
            {item.image_url ? (
              <img
                src={item.image_url} alt={item.name}
                style={{ width: '100%', height: 90, objectFit: 'cover', borderRadius: 10 }}
                onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
            ) : (
              <div style={{
                width: '100%', height: 90, borderRadius: 10, background: theme.pageBg,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Package size={28} color={theme.textSubtle} />
              </div>
            )}

            <div style={{
              fontSize: 13, fontWeight: 700, color: theme.text, lineHeight: 1.3,
              display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}>
              {item.name}
            </div>

            {item.brand && (
              <div style={{ fontSize: 11, color: theme.textSubtle }}>
                {item.brand}
              </div>
            )}

            <div style={{
              fontSize: 12, fontWeight: 700, color: theme.green,
              display: 'flex', alignItems: 'center', gap: 2, marginTop: 'auto',
            }}>
              {item.why_better}
            </div>

            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4,
              fontSize: 11, fontWeight: 600, color: theme.greenDark,
              background: theme.greenBg, borderRadius: 999, padding: '4px 8px',
            }}>
              View <ChevronRight size={12} />
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
