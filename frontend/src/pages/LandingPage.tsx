import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ScanLine, ShieldCheck, Brain, ArrowRight, Leaf, Zap, Lock } from 'lucide-react'
import Navbar from '../components/Navbar'

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] },
  }),
}

const steps = [
  {
    icon: ScanLine,
    title: 'Scan a Barcode',
    desc: 'Use your phone camera to scan any packaged food product barcode in seconds.',
    color: '#22c55e',
    bg: '#f0fdf4',
  },
  {
    icon: Brain,
    title: 'AI Analysis',
    desc: 'Our ML model analyzes ingredients against your unique health profile and conditions.',
    color: '#8b5cf6',
    bg: '#f5f3ff',
  },
  {
    icon: ShieldCheck,
    title: 'Get Your Rating',
    desc: 'Receive a personalized Safe / Caution / Avoid rating with plain-language explanations.',
    color: '#f59e0b',
    bg: '#fffbeb',
  },
]

const features = [
  { icon: Zap, title: 'Instant Results', desc: 'Scan and get analysis in under 2 seconds' },
  { icon: Lock, title: 'Private & Local', desc: 'Your health data never leaves your device' },
  { icon: Leaf, title: 'Personalized', desc: 'Tailored to your conditions and allergies' },
]

const floatingIcons = ['🥦', '🍎', '🥕', '🍋', '🫐', '🌽', '🍇', '🥑']

export default function LandingPage() {
  const navigate = useNavigate()
  const hasProfile = !!localStorage.getItem('user_id')

  return (
    <div style={{ minHeight: '100vh', overflowX: 'hidden' }}>
      <Navbar />

      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        background: 'linear-gradient(160deg, #f0fdf4 0%, #ffffff 50%, #f0fdf4 100%)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', overflow: 'hidden',
        paddingTop: 80,
      }}>
        {/* Floating food icons background */}
        {floatingIcons.map((icon, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 0 }}
            animate={{
              opacity: [0.3, 0.6, 0.3],
              y: [0, -20, 0],
              x: [0, i % 2 === 0 ? 10 : -10, 0],
            }}
            transition={{ duration: 4 + i * 0.5, repeat: Infinity, delay: i * 0.3 }}
            style={{
              position: 'absolute',
              fontSize: 32 + (i % 3) * 8,
              top: `${15 + (i * 10) % 70}%`,
              left: `${5 + (i * 12) % 90}%`,
              filter: 'blur(0.5px)',
              pointerEvents: 'none',
              zIndex: 0,
              userSelect: 'none',
            }}
          >
            {icon}
          </motion.div>
        ))}

        {/* Large green glow blobs */}
        <div style={{
          position: 'absolute', width: 500, height: 500,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%)',
          top: '10%', left: '-10%', pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', width: 400, height: 400,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(34,197,94,0.10) 0%, transparent 70%)',
          bottom: '10%', right: '-5%', pointerEvents: 'none',
        }} />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: 800, margin: '0 auto', padding: '2rem 1.5rem', textAlign: 'center' }}>
          <motion.div
            initial="hidden" animate="visible" variants={fadeUp} custom={0}
          >
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: '#dcfce7', color: '#16a34a',
              padding: '6px 14px', borderRadius: 999,
              fontSize: 14, fontWeight: 600, marginBottom: 24,
            }}>
              <Leaf size={14} />
              AI-Powered Food Analysis
            </span>
          </motion.div>

          <motion.h1
            initial="hidden" animate="visible" variants={fadeUp} custom={1}
            style={{
              fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
              fontWeight: 900, lineHeight: 1.1,
              color: '#111827', marginBottom: 24,
              letterSpacing: '-0.02em',
            }}
          >
            Know What's Really
            <br />
            <span style={{
              background: 'linear-gradient(135deg, #22c55e, #16a34a)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              In Your Food
            </span>
          </motion.h1>

          <motion.p
            initial="hidden" animate="visible" variants={fadeUp} custom={2}
            style={{
              fontSize: 'clamp(1rem, 2vw, 1.25rem)',
              color: '#6b7280', lineHeight: 1.8, marginBottom: 40,
              maxWidth: 560, margin: '0 auto 40px',
            }}
          >
            Scan any food barcode and get a personalized health rating based on
            your medical conditions, allergies, and dietary preferences — powered by ML.
          </motion.p>

          <motion.div
            initial="hidden" animate="visible" variants={fadeUp} custom={3}
            style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}
          >
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(34,197,94,0.3)' }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate(hasProfile ? '/scan' : '/profile-setup')}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                color: 'white', border: 'none',
                padding: '16px 32px', borderRadius: 12,
                fontSize: 17, fontWeight: 700, cursor: 'pointer',
                boxShadow: '0 8px 25px rgba(34,197,94,0.25)',
              }}
            >
              {hasProfile ? 'Start Scanning' : 'Get Started Free'}
              <motion.span
                animate={{ x: [0, 4, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <ArrowRight size={18} />
              </motion.span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                background: 'white', color: '#374151',
                border: '2px solid #e5e7eb',
                padding: '16px 28px', borderRadius: 12,
                fontSize: 17, fontWeight: 600, cursor: 'pointer',
              }}
            >
              See How It Works
            </motion.button>
          </motion.div>

          {/* Animated scanner illustration */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{ marginTop: 60 }}
          >
            <div style={{
              display: 'inline-flex', flexDirection: 'column', alignItems: 'center',
              background: 'white', borderRadius: 24,
              padding: '24px', boxShadow: '0 25px 60px rgba(0,0,0,0.12)',
              border: '1px solid #e5e7eb', position: 'relative',
            }}>
              {/* Mock phone scanner UI */}
              <div style={{
                width: 220, height: 160, borderRadius: 12,
                background: '#f9fafb', display: 'flex', alignItems: 'center',
                justifyContent: 'center', position: 'relative', overflow: 'hidden',
                border: '2px solid #e5e7eb',
              }}>
                {/* Corners */}
                {[['0','0'], ['0','auto'], ['auto','0'], ['auto','auto']].map(([t,b], i) => (
                  <div key={i} style={{
                    position: 'absolute',
                    top: t === '0' ? 8 : 'auto', bottom: b === 'auto' ? 'auto' : 8,
                    left: i < 2 ? 8 : 'auto', right: i >= 2 ? 8 : 'auto',
                    width: 20, height: 20,
                    borderTop: t === '0' ? '3px solid #22c55e' : 'none',
                    borderBottom: b !== 'auto' ? '3px solid #22c55e' : 'none',
                    borderLeft: i % 2 === 0 ? '3px solid #22c55e' : 'none',
                    borderRight: i % 2 !== 0 ? '3px solid #22c55e' : 'none',
                  }} />
                ))}
                {/* Scanning line */}
                <motion.div
                  animate={{ y: [-50, 50, -50] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  style={{
                    position: 'absolute', left: 12, right: 12, height: 2,
                    background: 'linear-gradient(90deg, transparent, #22c55e, transparent)',
                    borderRadius: 1,
                  }}
                />
                {/* Barcode mock */}
                <div style={{ display: 'flex', gap: 2, opacity: 0.4 }}>
                  {[3,1,2,4,1,3,2,1,4,2,3,1].map((w, i) => (
                    <div key={i} style={{ width: w * 3, height: 60, background: '#374151', borderRadius: 1 }} />
                  ))}
                </div>
              </div>
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                style={{
                  marginTop: 12, display: 'flex', alignItems: 'center', gap: 6,
                  background: '#dcfce7', color: '#16a34a',
                  padding: '6px 12px', borderRadius: 8, fontSize: 13, fontWeight: 600,
                }}
              >
                <ShieldCheck size={14} />
                Safe for your profile
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" style={{
        padding: 'clamp(4rem, 8vw, 8rem) 1.5rem',
        background: '#ffffff',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            style={{ textAlign: 'center', marginBottom: 64 }}
          >
            <span style={{
              display: 'inline-block',
              background: '#f0fdf4', color: '#16a34a',
              padding: '6px 14px', borderRadius: 999,
              fontSize: 14, fontWeight: 600, marginBottom: 16,
            }}>
              Simple Process
            </span>
            <h2 style={{
              fontSize: 'clamp(1.75rem, 4vw, 2.75rem)',
              fontWeight: 800, color: '#111827',
              letterSpacing: '-0.02em', lineHeight: 1.2,
            }}>
              How It Works
            </h2>
            <p style={{ color: '#6b7280', fontSize: 17, marginTop: 12, maxWidth: 480, margin: '12px auto 0' }}>
              Three simple steps to understand exactly what you're eating.
            </p>
          </motion.div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 32,
          }}>
            {steps.map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.15 }}
                whileHover={{ y: -6, boxShadow: '0 20px 40px rgba(0,0,0,0.10)' }}
                style={{
                  background: 'white', borderRadius: 20,
                  padding: '2rem', border: '1px solid #f0fdf4',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                  transition: 'box-shadow 0.3s',
                  position: 'relative', overflow: 'hidden',
                }}
              >
                <div style={{
                  position: 'absolute', top: 0, left: 0, right: 0, height: 4,
                  background: `linear-gradient(90deg, ${step.color}, ${step.color}88)`,
                }} />
                <div style={{
                  width: 56, height: 56, borderRadius: 16,
                  background: step.bg, display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  marginBottom: 20,
                }}>
                  <step.icon size={28} color={step.color} />
                </div>
                <div style={{
                  display: 'inline-block',
                  background: '#f3f4f6', color: '#6b7280',
                  padding: '2px 10px', borderRadius: 999,
                  fontSize: 12, fontWeight: 700,
                  letterSpacing: '0.05em', marginBottom: 10,
                }}>
                  STEP {i + 1}
                </div>
                <h3 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginBottom: 10 }}>
                  {step.title}
                </h3>
                <p style={{ color: '#6b7280', lineHeight: 1.7, fontSize: 15 }}>
                  {step.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{
        padding: 'clamp(3rem, 6vw, 6rem) 1.5rem',
        background: 'linear-gradient(160deg, #f0fdf4 0%, #dcfce7 100%)',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 24,
          }}>
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: 16,
                  background: 'white', padding: '1.5rem', borderRadius: 16,
                  boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
                }}
              >
                <div style={{
                  width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                  background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <f.icon size={22} color="#22c55e" />
                </div>
                <div>
                  <h4 style={{ fontWeight: 700, fontSize: 16, color: '#111827', marginBottom: 4 }}>
                    {f.title}
                  </h4>
                  <p style={{ fontSize: 14, color: '#6b7280', lineHeight: 1.6 }}>
                    {f.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        padding: 'clamp(4rem, 8vw, 8rem) 1.5rem',
        textAlign: 'center',
        background: 'white',
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          style={{
            maxWidth: 640, margin: '0 auto',
            background: 'linear-gradient(135deg, #166534, #16a34a)',
            padding: 'clamp(2.5rem, 5vw, 4rem) clamp(1.5rem, 4vw, 3rem)',
            borderRadius: 28, color: 'white',
          }}
        >
          <h2 style={{ fontSize: 'clamp(1.75rem, 4vw, 2.5rem)', fontWeight: 800, marginBottom: 16, lineHeight: 1.2 }}>
            Ready to eat smarter?
          </h2>
          <p style={{ fontSize: 17, opacity: 0.9, marginBottom: 32, lineHeight: 1.7 }}>
            Set up your health profile in under a minute and start scanning.
          </p>
          <motion.button
            whileHover={{ scale: 1.06, boxShadow: '0 15px 35px rgba(0,0,0,0.3)' }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate(hasProfile ? '/scan' : '/profile-setup')}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'white', color: '#16a34a',
              border: 'none', padding: '16px 36px', borderRadius: 12,
              fontSize: 17, fontWeight: 700, cursor: 'pointer',
            }}
          >
            {hasProfile ? 'Start Scanning' : 'Create My Profile'}
            <ArrowRight size={18} />
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '2rem 1.5rem', textAlign: 'center',
        borderTop: '1px solid #e5e7eb',
        color: '#9ca3af', fontSize: 14,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 8 }}>
          <Leaf size={14} color="#22c55e" />
          <span style={{ fontWeight: 600, color: '#374151' }}>Food Truth Teller</span>
        </div>
        <p>Built with ❤️ for healthier food choices · Not a substitute for medical advice</p>
      </footer>
    </div>
  )
}
