import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'

// Matches the existing Safe/Caution/Avoid color language used elsewhere in the app
const RING_SAFE = '#22c55e'
const RING_CAUTION = '#f59e0b'
const RING_AVOID = '#ef4444'

function ringColor(pct: number): string {
  if (pct > 90) return RING_AVOID
  if (pct >= 70) return RING_CAUTION
  return RING_SAFE
}

export default function IntakeRing({
  label, current, limit, percentage, unit,
}: { label: string; current: number; limit: number; percentage: number; unit: string }) {
  const { theme } = useTheme()

  const size = 96
  const stroke = 9
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, percentage || 0))
  const offset = circumference - (clamped / 100) * circumference
  const color = ringColor(clamped)

  const displayCurrent = Number.isFinite(current) ? Math.round(current) : 0
  const displayLimit = Number.isFinite(limit) && limit > 0 ? Math.round(limit) : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={theme.cardBorder} strokeWidth={stroke}
          />
          <motion.circle
            cx={size / 2} cy={size / 2} r={radius}
            fill="none" stroke={color} strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 16, fontWeight: 800, color: theme.text, lineHeight: 1.1 }}>
            {displayCurrent}
          </span>
          <span style={{ fontSize: 11, color: theme.textSubtle, lineHeight: 1.1 }}>
            / {displayLimit}{unit}
          </span>
        </div>
      </div>
      <span style={{ fontSize: 13, fontWeight: 600, color: theme.textMuted, textAlign: 'center' }}>
        {label}
      </span>
    </div>
  )
}
