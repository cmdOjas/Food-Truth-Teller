import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function SplashScreen({ onDone }: { onDone: () => void }) {
  const [progress, setProgress] = useState(0)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const start = Date.now()
    const duration = 1500

    const tick = () => {
      const elapsed = Date.now() - start
      const pct = Math.min(elapsed / duration, 1)
      setProgress(pct)
      if (pct < 1) {
        requestAnimationFrame(tick)
      }
    }
    requestAnimationFrame(tick)

    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onDone, 400)
    }, duration)

    return () => clearTimeout(timer)
  }, [onDone])

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: '#0a0f0a',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
          }}
        >
          {/* Glow ring */}
          <div style={{ position: 'relative', marginBottom: 28 }}>
            <div style={{
              position: 'absolute', inset: -18,
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(34,197,94,0.30) 0%, transparent 70%)',
              animation: 'pulse-glow 1.6s ease-in-out infinite',
            }} />
            <div style={{
              width: 80, height: 80, borderRadius: 22,
              background: 'linear-gradient(135deg, #22c55e, #16a34a)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 44,
              boxShadow: '0 0 32px rgba(34,197,94,0.45)',
              position: 'relative',
            }}>
              🌿
            </div>
          </div>

          {/* App name */}
          <h1 style={{ fontSize: 36, fontWeight: 900, letterSpacing: '-0.02em', margin: 0, lineHeight: 1 }}>
            <span style={{ color: '#ffffff' }}>EatWise</span>
            <span style={{ color: '#22c55e' }}>AI</span>
          </h1>

          {/* Tagline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            style={{ color: '#6b7280', fontSize: 14, marginTop: 10, letterSpacing: '0.08em', fontWeight: 500 }}
          >
            Scan. Understand. Decide.
          </motion.p>

          {/* Progress bar */}
          <div style={{
            position: 'fixed', bottom: 0, left: 0, right: 0,
            height: 3, background: 'rgba(34,197,94,0.15)',
          }}>
            <motion.div
              style={{
                height: '100%',
                width: `${progress * 100}%`,
                background: 'linear-gradient(90deg, #16a34a, #22c55e)',
                borderRadius: '0 2px 2px 0',
                boxShadow: '0 0 8px rgba(34,197,94,0.6)',
              }}
            />
          </div>

          <style>{`
            @keyframes pulse-glow {
              0%, 100% { transform: scale(1); opacity: 0.7; }
              50% { transform: scale(1.18); opacity: 1; }
            }
          `}</style>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
