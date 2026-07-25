import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import type { NutriScore as NutriScoreData, NutriGrade } from '../types'

// Official Nutri-Score palette
const GRADE_COLORS: Record<NutriGrade, string> = {
  A: '#038141',
  B: '#85BB2F',
  C: '#FECB02',
  D: '#EE8100',
  E: '#E63E11',
}

const GRADE_DESCRIPTIONS: Record<NutriGrade, string> = {
  A: 'Excellent nutritional quality',
  B: 'Good nutritional quality',
  C: 'Average nutritional quality',
  D: 'Poor nutritional quality',
  E: 'Low nutritional quality',
}

const GRADES: NutriGrade[] = ['A', 'B', 'C', 'D', 'E']

// Guard any value so the UI never shows NaN/undefined/null
function n(v: number | undefined | null): number {
  return typeof v === 'number' && !isNaN(v) ? v : 0
}

export default function NutriScore({ data }: { data: NutriScoreData }) {
  const { theme } = useTheme()
  const [expanded, setExpanded] = useState(false)

  if (!data) return null

  const activeGrade: NutriGrade = GRADES.includes(data.grade) ? data.grade : 'B'
  const activeColor = GRADE_COLORS[activeGrade]
  const b = data.breakdown || ({} as NutriScoreData['breakdown'])

  const description = data.insufficient_data
    ? 'Limited nutritional data available — grade shown is a default estimate.'
    : GRADE_DESCRIPTIONS[activeGrade]

  // Rows for the breakdown table: negatives (red when >0), positives (green when >0)
  const negativeRows = [
    { label: 'Energy', points: n(b.energy_points) },
    { label: 'Sugars', points: n(b.sugars_points) },
    { label: 'Saturated Fat', points: n(b.saturated_fat_points) },
    { label: 'Sodium', points: n(b.sodium_points) },
  ]
  const positiveRows = [
    { label: 'Fiber', points: n(b.fiber_points) },
    { label: 'Protein', points: n(b.protein_points) },
    { label: 'Fruits/Veg/Nuts', points: n(b.fruits_veg_points) },
  ]

  const rowStyle: React.CSSProperties = {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '8px 0', borderBottom: `1px solid ${theme.cardBorder}`,
    fontSize: 14, color: theme.text,
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      style={{
        background: theme.cardBg,
        borderRadius: 20,
        padding: 20,
        marginBottom: 16,
        border: `1px solid ${theme.cardBorder}`,
        boxShadow: theme.isDark ? '0 4px 20px rgba(0,0,0,0.3)' : '0 4px 20px rgba(0,0,0,0.07)',
      }}
    >
      {/* Section label */}
      <div style={{ fontSize: 13, fontWeight: 600, color: theme.textMuted, marginBottom: 14, letterSpacing: '0.02em' }}>
        NUTRITIONAL QUALITY (per 100g)
      </div>

      {/* Row of five letter boxes */}
      <div style={{ display: 'flex', gap: 8, justifyContent: 'center', alignItems: 'center', padding: '10px 0 16px' }}>
        {GRADES.map(g => {
          const isActive = g === activeGrade
          return (
            <motion.div
              key={g}
              initial={isActive ? { scale: 0.5 } : false}
              animate={{ scale: isActive ? 1.3 : 0.85 }}
              transition={isActive
                ? { duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }
                : { duration: 0.3 }}
              style={{
                width: 44,
                height: 44,
                borderRadius: 10,
                background: GRADE_COLORS[g],
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 20,
                fontWeight: isActive ? 800 : 600,
                opacity: isActive ? 1 : 0.45,
                boxShadow: isActive ? '0 4px 15px rgba(0,0,0,0.3)' : 'none',
                flexShrink: 0,
              }}
            >
              {g}
            </motion.div>
          )
        })}
      </div>

      {/* Heading + description */}
      <div style={{ textAlign: 'center', marginBottom: 6 }}>
        <div style={{ fontSize: 20, fontWeight: 800, color: activeColor }}>
          Nutri-Score: {activeGrade}
        </div>
        <div style={{ fontSize: 14, color: theme.textMuted, marginTop: 4, lineHeight: 1.5 }}>
          {description}
        </div>
      </div>

      {/* Collapsible breakdown */}
      <div style={{ marginTop: 14 }}>
        <button
          onClick={() => setExpanded(v => !v)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'none', border: 'none', cursor: 'pointer',
            color: theme.textMuted, fontSize: 14, fontWeight: 600, padding: '4px 0',
            fontFamily: 'inherit',
          }}
        >
          See breakdown
          <motion.span
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
            style={{ display: 'inline-flex' }}
          >
            <ChevronDown size={16} />
          </motion.span>
        </button>

        <AnimatePresence initial={false}>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              style={{ overflow: 'hidden' }}
            >
              <div style={{ marginTop: 10 }}>
                {negativeRows.map(r => (
                  <div key={r.label} style={rowStyle}>
                    <span>{r.label}</span>
                    <span style={{ fontWeight: 700, color: r.points > 0 ? '#dc2626' : theme.textSubtle }}>
                      +{r.points}
                    </span>
                  </div>
                ))}
                {positiveRows.map(r => (
                  <div key={r.label} style={rowStyle}>
                    <span>{r.label}</span>
                    <span style={{ fontWeight: 700, color: r.points > 0 ? '#16a34a' : theme.textSubtle }}>
                      -{r.points}
                    </span>
                  </div>
                ))}
                <div style={{ ...rowStyle, borderBottom: 'none', paddingTop: 12 }}>
                  <span style={{ fontWeight: 800 }}>Final Score</span>
                  <span style={{ fontWeight: 800, color: theme.text }}>{n(data.score)}</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom note */}
      <div style={{ fontSize: 12, color: theme.textSubtle, marginTop: 14, lineHeight: 1.6 }}>
        Nutri-Score rates nutritional quality per 100g using the official European system.
        It does not replace your personal health analysis above, which considers your specific conditions.
      </div>
    </motion.div>
  )
}
