import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Leaf, ChevronRight, ChevronLeft, CheckCircle, User, Heart, AlertTriangle, Utensils } from 'lucide-react'
import { profileApi } from '../services/api'
import { DISEASES_OPTIONS, ALLERGIES_OPTIONS, DIET_OPTIONS } from '../types'

const STEPS = [
  { label: 'Basic Info', icon: User },
  { label: 'Conditions', icon: Heart },
  { label: 'Allergies', icon: AlertTriangle },
  { label: 'Diet Type', icon: Utensils },
]

interface FormData {
  name: string
  age: string
  gender: string
  weight: string
  diseases: string[]
  allergies: string[]
  diet_type: string
}

const inputStyle = {
  width: '100%', padding: '12px 16px', borderRadius: 10,
  border: '2px solid #e5e7eb', fontSize: 16, fontFamily: 'inherit',
  outline: 'none', transition: 'border-color 0.2s',
  background: 'white',
}

function CheckItem({
  label, checked, onChange,
}: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <motion.label
      whileTap={{ scale: 0.97 }}
      style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '14px 16px', borderRadius: 12, cursor: 'pointer',
        border: `2px solid ${checked ? '#22c55e' : '#e5e7eb'}`,
        background: checked ? '#f0fdf4' : 'white',
        transition: 'all 0.2s', marginBottom: 8,
      }}
    >
      <input
        type="checkbox" checked={checked}
        onChange={e => onChange(e.target.checked)}
        style={{ display: 'none' }}
      />
      <div style={{
        width: 22, height: 22, borderRadius: 6, flexShrink: 0,
        border: `2px solid ${checked ? '#22c55e' : '#d1d5db'}`,
        background: checked ? '#22c55e' : 'white',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        transition: 'all 0.2s',
      }}>
        {checked && (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 400 }}>
            <CheckCircle size={14} color="white" fill="white" />
          </motion.div>
        )}
      </div>
      <span style={{ fontWeight: 500, fontSize: 15, color: '#374151' }}>{label}</span>
    </motion.label>
  )
}

export default function ProfileSetupPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState<FormData>({
    name: '', age: '', gender: '', weight: '',
    diseases: [], allergies: [], diet_type: 'non-vegetarian',
  })

  const update = (field: keyof FormData, value: string | string[]) =>
    setForm(f => ({ ...f, [field]: value }))

  const toggleList = (field: 'diseases' | 'allergies', value: string) => {
    setForm(f => ({
      ...f,
      [field]: f[field].includes(value)
        ? f[field].filter(v => v !== value)
        : [...f[field], value],
    }))
  }

  const canNext = () => {
    if (step === 0) return form.name.trim().length >= 2
    return true
  }

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(s => s + 1)
    else handleSubmit()
  }

  const handleSubmit = async () => {
    setSaving(true)
    setError('')
    try {
      const user = await profileApi.create({
        name: form.name.trim(),
        age: form.age ? parseInt(form.age) : undefined,
        gender: form.gender || undefined,
        weight: form.weight ? parseFloat(form.weight) : undefined,
        diseases: form.diseases,
        allergies: form.allergies,
        diet_type: form.diet_type as any,
      })
      localStorage.setItem('user_id', String(user.id))
      localStorage.setItem('user_name', user.name)
      navigate('/scan')
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to save profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', background: 'linear-gradient(160deg, #f0fdf4 0%, #ffffff 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '2rem 1rem',
    }}>
      <div style={{ width: '100%', maxWidth: 500 }}>
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', marginBottom: 32 }}
        >
          <div style={{
            width: 48, height: 48, borderRadius: 14,
            background: 'linear-gradient(135deg, #22c55e, #16a34a)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 12px',
          }}>
            <Leaf size={24} color="white" />
          </div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827' }}>
            Set Up Your Profile
          </h1>
          <p style={{ color: '#6b7280', fontSize: 15, marginTop: 4 }}>
            So we can personalize your food analysis
          </p>
        </motion.div>

        {/* Step indicator */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 32, justifyContent: 'center' }}>
          {STEPS.map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <motion.div
                animate={{
                  background: i === step ? '#22c55e' : i < step ? '#86efac' : '#e5e7eb',
                  scale: i === step ? 1.1 : 1,
                }}
                style={{
                  width: 32, height: 32, borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 13, fontWeight: 700,
                  color: i <= step ? 'white' : '#9ca3af',
                }}
              >
                {i < step ? '✓' : i + 1}
              </motion.div>
              {i < STEPS.length - 1 && (
                <div style={{
                  width: 24, height: 2, borderRadius: 1,
                  background: i < step ? '#86efac' : '#e5e7eb',
                  transition: 'background 0.3s',
                }} />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <motion.div
          style={{
            background: 'white', borderRadius: 24, padding: '2rem',
            boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
            border: '1px solid #f0fdf4',
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
            >
              {/* Step 0: Basic Info */}
              {step === 0 && (
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginBottom: 20 }}>
                    👋 Tell us about yourself
                  </h2>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 6 }}>
                      Your Name *
                    </label>
                    <input
                      style={inputStyle}
                      placeholder="Enter your name"
                      value={form.name}
                      onChange={e => update('name', e.target.value)}
                      autoFocus
                    />
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 6 }}>
                        Age
                      </label>
                      <input
                        style={inputStyle}
                        type="number" placeholder="Age"
                        value={form.age}
                        onChange={e => update('age', e.target.value)}
                        min="1" max="120"
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 6 }}>
                        Weight (kg)
                      </label>
                      <input
                        style={inputStyle}
                        type="number" placeholder="Weight"
                        value={form.weight}
                        onChange={e => update('weight', e.target.value)}
                        min="1" max="500"
                      />
                    </div>
                  </div>
                  <div style={{ marginTop: 16 }}>
                    <label style={{ display: 'block', fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 8 }}>
                      Gender
                    </label>
                    <div style={{ display: 'flex', gap: 8 }}>
                      {['Male', 'Female', 'Other'].map(g => (
                        <motion.button
                          key={g}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => update('gender', g.toLowerCase())}
                          style={{
                            flex: 1, padding: '10px', borderRadius: 10, cursor: 'pointer',
                            border: `2px solid ${form.gender === g.toLowerCase() ? '#22c55e' : '#e5e7eb'}`,
                            background: form.gender === g.toLowerCase() ? '#f0fdf4' : 'white',
                            color: form.gender === g.toLowerCase() ? '#16a34a' : '#374151',
                            fontWeight: 600, fontSize: 14, transition: 'all 0.2s',
                          }}
                        >
                          {g}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 1: Health Conditions */}
              {step === 1 && (
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginBottom: 8 }}>
                    🏥 Health Conditions
                  </h2>
                  <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 20 }}>
                    Select any conditions you have, or skip if none apply.
                  </p>
                  {DISEASES_OPTIONS.map(opt => (
                    <CheckItem
                      key={opt.value}
                      label={opt.label}
                      checked={form.diseases.includes(opt.value)}
                      onChange={checked => toggleList('diseases', opt.value)}
                    />
                  ))}
                  {form.diseases.length === 0 && (
                    <p style={{ color: '#9ca3af', fontSize: 13, marginTop: 8, textAlign: 'center' }}>
                      No conditions selected (products will show general safety ratings)
                    </p>
                  )}
                </div>
              )}

              {/* Step 2: Allergies */}
              {step === 2 && (
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginBottom: 8 }}>
                    ⚠️ Food Allergies
                  </h2>
                  <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 20 }}>
                    We'll flag products containing your allergens immediately.
                  </p>
                  {ALLERGIES_OPTIONS.map(opt => (
                    <CheckItem
                      key={opt.value}
                      label={opt.label}
                      checked={form.allergies.includes(opt.value)}
                      onChange={() => toggleList('allergies', opt.value)}
                    />
                  ))}
                </div>
              )}

              {/* Step 3: Diet Type */}
              {step === 3 && (
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', marginBottom: 8 }}>
                    🥗 Dietary Preference
                  </h2>
                  <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 20 }}>
                    We'll flag products that don't match your diet.
                  </p>
                  {DIET_OPTIONS.map(opt => (
                    <motion.button
                      key={opt.value}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => update('diet_type', opt.value)}
                      style={{
                        width: '100%', padding: '16px', borderRadius: 12,
                        marginBottom: 10, cursor: 'pointer',
                        border: `2px solid ${form.diet_type === opt.value ? '#22c55e' : '#e5e7eb'}`,
                        background: form.diet_type === opt.value ? '#f0fdf4' : 'white',
                        color: form.diet_type === opt.value ? '#16a34a' : '#374151',
                        fontWeight: 600, fontSize: 16, textAlign: 'left',
                        transition: 'all 0.2s',
                      }}
                    >
                      {opt.value === 'non-vegetarian' ? '🍗 ' : opt.value === 'vegetarian' ? '🌿 ' : '🌱 '}
                      {opt.label}
                    </motion.button>
                  ))}
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {error && (
            <div style={{
              background: '#fee2e2', color: '#dc2626', padding: '10px 14px',
              borderRadius: 8, fontSize: 14, marginTop: 16,
            }}>
              {error}
            </div>
          )}

          {/* Navigation */}
          <div style={{ display: 'flex', gap: 10, marginTop: 24 }}>
            {step > 0 && (
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() => setStep(s => s - 1)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '12px 20px', borderRadius: 10,
                  border: '2px solid #e5e7eb', background: 'white',
                  color: '#374151', fontWeight: 600, fontSize: 15, cursor: 'pointer',
                }}
              >
                <ChevronLeft size={18} /> Back
              </motion.button>
            )}
            <motion.button
              whileHover={{ scale: canNext() ? 1.02 : 1 }}
              whileTap={{ scale: canNext() ? 0.97 : 1 }}
              onClick={handleNext}
              disabled={!canNext() || saving}
              style={{
                flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                padding: '14px', borderRadius: 10, border: 'none',
                background: canNext() ? 'linear-gradient(135deg, #22c55e, #16a34a)' : '#e5e7eb',
                color: canNext() ? 'white' : '#9ca3af',
                fontWeight: 700, fontSize: 16, cursor: canNext() ? 'pointer' : 'not-allowed',
                boxShadow: canNext() ? '0 4px 15px rgba(34,197,94,0.3)' : 'none',
              }}
            >
              {saving ? 'Saving...' : step === STEPS.length - 1 ? '🎉 Save & Start Scanning' : (
                <> Continue <ChevronRight size={18} /> </>
              )}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
