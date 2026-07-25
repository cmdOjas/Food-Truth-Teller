import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Save, LogOut, CheckCircle, User } from 'lucide-react'
import Navbar from '../components/Navbar'
import { profileApi } from '../services/api'
import { DISEASES_OPTIONS, ALLERGIES_OPTIONS, DIET_OPTIONS, SENSITIVITY_OPTIONS } from '../types'
import { useTheme } from '../context/ThemeContext'

function CheckItem({ label, checked, onChange, theme }: {
  label: string; checked: boolean; onChange: (v: boolean) => void;
  theme: ReturnType<typeof useTheme>['theme']
}) {
  return (
    <motion.label
      whileTap={{ scale: 0.97 }}
      style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '12px 14px', borderRadius: 10, cursor: 'pointer',
        border: `2px solid ${checked ? theme.green : theme.inputBorder}`,
        background: checked ? theme.greenBg : theme.cardBg,
        transition: 'all 0.2s', marginBottom: 6,
      }}
    >
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} style={{ display: 'none' }} />
      <div style={{
        width: 20, height: 20, borderRadius: 5, flexShrink: 0,
        border: `2px solid ${checked ? theme.green : theme.textSubtle}`,
        background: checked ? theme.green : theme.inputBg,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {checked && <CheckCircle size={13} color="white" fill="white" />}
      </div>
      <span style={{ fontWeight: 500, fontSize: 14, color: theme.text }}>{label}</span>
    </motion.label>
  )
}

export default function ProfileEditPage() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    name: '', age: '', gender: '', weight: '',
    diseases: [] as string[], allergies: [] as string[],
    diet_type: 'non-vegetarian',
    sensitivity: 'medium',
  })
  const [noneDisease, setNoneDisease] = useState(false)
  const [otherDiseaseChecked, setOtherDiseaseChecked] = useState(false)
  const [otherDiseaseText, setOtherDiseaseText] = useState('')
  const [noneAllergy, setNoneAllergy] = useState(false)
  const [otherAllergyChecked, setOtherAllergyChecked] = useState(false)
  const [otherAllergyText, setOtherAllergyText] = useState('')

  const userId = localStorage.getItem('user_id')

  const inputStyle = {
    width: '100%', padding: '12px 16px', borderRadius: 10,
    border: `2px solid ${theme.inputBorder}`, fontSize: 15, fontFamily: 'inherit',
    outline: 'none', background: theme.inputBg, color: theme.text,
  }

  useEffect(() => {
    if (!userId) { navigate('/profile-setup'); return }
    profileApi.get(parseInt(userId))
      .then(p => {
        const stdDiseaseVals = DISEASES_OPTIONS.map(o => o.value)
        const stdAllergyVals = ALLERGIES_OPTIONS.map(o => o.value)
        const loadedDiseases = p.diseases || []
        const loadedAllergies = p.allergies || []
        const stdDiseases = loadedDiseases.filter(d => stdDiseaseVals.includes(d))
        const otherDiseases = loadedDiseases.filter(d => !stdDiseaseVals.includes(d))
        const stdAllergies = loadedAllergies.filter(a => stdAllergyVals.includes(a))
        const otherAllergies = loadedAllergies.filter(a => !stdAllergyVals.includes(a))
        setForm({
          name: p.name || '',
          age: String(p.age || ''),
          gender: p.gender || '',
          weight: String(p.weight || ''),
          diseases: stdDiseases,
          allergies: stdAllergies,
          diet_type: p.diet_type || 'non-vegetarian',
          sensitivity: p.sensitivity || 'medium',
        })
        if (otherDiseases.length > 0) {
          setOtherDiseaseChecked(true)
          setOtherDiseaseText(otherDiseases.join(', '))
        }
        if (otherAllergies.length > 0) {
          setOtherAllergyChecked(true)
          setOtherAllergyText(otherAllergies.join(', '))
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const update = (field: string, value: string | string[]) =>
    setForm(f => ({ ...f, [field]: value }))

  const toggleList = (field: 'diseases' | 'allergies', value: string) =>
    setForm(f => ({
      ...f,
      [field]: f[field].includes(value) ? f[field].filter(v => v !== value) : [...f[field], value],
    }))

  const handleSave = async () => {
    if (!form.name.trim()) { setError('Name is required'); return }
    setSaving(true); setError('')
    const finalDiseases = noneDisease ? [] : otherDiseaseChecked && otherDiseaseText.trim()
      ? [...form.diseases, otherDiseaseText.trim()] : form.diseases
    const finalAllergies = noneAllergy ? [] : otherAllergyChecked && otherAllergyText.trim()
      ? [...form.allergies, otherAllergyText.trim()] : form.allergies
    try {
      await profileApi.update({
        id: parseInt(userId!),
        name: form.name.trim(),
        age: form.age ? parseInt(form.age) : undefined,
        gender: form.gender || undefined,
        weight: form.weight ? parseFloat(form.weight) : undefined,
        diseases: finalDiseases,
        allergies: finalAllergies,
        diet_type: form.diet_type as any,
        sensitivity: form.sensitivity as any,
      })
      localStorage.setItem('user_name', form.name.trim())
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    localStorage.removeItem('recent_scans')
    navigate('/')
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: theme.pageBg }}>
        <Navbar />
        <div style={{ paddingTop: 100, textAlign: 'center', color: theme.textSubtle }}>Loading profile...</div>
      </div>
    )
  }

  const sectionStyle = {
    background: theme.cardBg, borderRadius: 20, padding: '1.5rem',
    boxShadow: theme.isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.06)',
    border: `1px solid ${theme.cardBorder}`, marginBottom: 16,
  }

  return (
    <div style={{ minHeight: '100vh', background: theme.pageBg }}>
      <Navbar />
      <div style={{ paddingTop: 80, maxWidth: 580, margin: '0 auto', padding: '80px 1rem 3rem' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: 'linear-gradient(135deg, #22c55e, #16a34a)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <User size={22} color="white" />
            </div>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 800, color: theme.text }}>Your Profile</h1>
              <p style={{ color: theme.textMuted, fontSize: 14 }}>Update your health information</p>
            </div>
          </div>

          {/* Saved banner */}
          {saved && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{
                background: theme.greenBg, color: theme.greenDark, padding: '12px 16px',
                borderRadius: 10, marginBottom: 16, fontWeight: 600,
                display: 'flex', alignItems: 'center', gap: 8,
                border: `1px solid ${theme.isDark ? '#1a4a28' : '#bbf7d0'}`,
              }}
            >
              <CheckCircle size={18} /> Profile saved successfully!
            </motion.div>
          )}

          {error && (
            <div style={{
              background: theme.isDark ? '#1f0a0a' : '#fee2e2',
              color: '#dc2626', padding: '12px 16px', borderRadius: 10, marginBottom: 16, fontSize: 14,
            }}>
              {error}
            </div>
          )}

          {/* Basic Info */}
          <div style={sectionStyle}>
            <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 16 }}>Basic Information</h3>
            <div style={{ marginBottom: 14 }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: theme.textMuted, marginBottom: 6 }}>NAME *</label>
              <input style={inputStyle} value={form.name} onChange={e => update('name', e.target.value)} placeholder="Your name" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: theme.textMuted, marginBottom: 6 }}>AGE</label>
                <input style={inputStyle} type="number" value={form.age} onChange={e => update('age', e.target.value)} placeholder="Age" min="1" max="120" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: theme.textMuted, marginBottom: 6 }}>WEIGHT (kg)</label>
                <input style={inputStyle} type="number" value={form.weight} onChange={e => update('weight', e.target.value)} placeholder="Weight" />
              </div>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: theme.textMuted, marginBottom: 8 }}>GENDER</label>
              <div style={{ display: 'flex', gap: 8 }}>
                {['Male', 'Female', 'Other'].map(g => (
                  <motion.button key={g} whileTap={{ scale: 0.95 }} onClick={() => update('gender', g.toLowerCase())}
                    style={{
                      flex: 1, padding: '10px', borderRadius: 8, cursor: 'pointer',
                      border: `2px solid ${form.gender === g.toLowerCase() ? theme.green : theme.inputBorder}`,
                      background: form.gender === g.toLowerCase() ? theme.greenBg : theme.inputBg,
                      color: form.gender === g.toLowerCase() ? theme.greenDark : theme.text,
                      fontWeight: 600, fontSize: 14,
                    }}>
                    {g}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>

          {/* Health Conditions */}
          <div style={sectionStyle}>
            <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>Health Conditions</h3>
            <CheckItem
              label="None"
              checked={noneDisease}
              onChange={checked => {
                setNoneDisease(checked)
                if (checked) {
                  update('diseases', [])
                  setOtherDiseaseChecked(false)
                  setOtherDiseaseText('')
                }
              }}
              theme={theme}
            />
            {DISEASES_OPTIONS.map(opt => (
              <CheckItem
                key={opt.value}
                label={opt.label}
                checked={form.diseases.includes(opt.value)}
                onChange={() => {
                  setNoneDisease(false)
                  toggleList('diseases', opt.value)
                }}
                theme={theme}
              />
            ))}
            <CheckItem
              label="Other"
              checked={otherDiseaseChecked}
              onChange={checked => {
                setOtherDiseaseChecked(checked)
                if (checked) setNoneDisease(false)
                if (!checked) setOtherDiseaseText('')
              }}
              theme={theme}
            />
            {otherDiseaseChecked && (
              <input
                value={otherDiseaseText}
                onChange={e => setOtherDiseaseText(e.target.value)}
                placeholder="Type your condition..."
                style={inputStyle}
              />
            )}
          </div>

          {/* Allergies */}
          <div style={sectionStyle}>
            <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>Food Allergies</h3>
            <CheckItem
              label="None"
              checked={noneAllergy}
              onChange={checked => {
                setNoneAllergy(checked)
                if (checked) {
                  update('allergies', [])
                  setOtherAllergyChecked(false)
                  setOtherAllergyText('')
                }
              }}
              theme={theme}
            />
            {ALLERGIES_OPTIONS.map(opt => (
              <CheckItem
                key={opt.value}
                label={opt.label}
                checked={form.allergies.includes(opt.value)}
                onChange={() => {
                  setNoneAllergy(false)
                  toggleList('allergies', opt.value)
                }}
                theme={theme}
              />
            ))}
            <CheckItem
              label="Other"
              checked={otherAllergyChecked}
              onChange={checked => {
                setOtherAllergyChecked(checked)
                if (checked) setNoneAllergy(false)
                if (!checked) setOtherAllergyText('')
              }}
              theme={theme}
            />
            {otherAllergyChecked && (
              <input
                value={otherAllergyText}
                onChange={e => setOtherAllergyText(e.target.value)}
                placeholder="Type your allergy..."
                style={inputStyle}
              />
            )}
          </div>

          {/* Diet */}
          <div style={sectionStyle}>
            <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>Dietary Preference</h3>
            {DIET_OPTIONS.map(opt => (
              <motion.button key={opt.value} whileTap={{ scale: 0.97 }} onClick={() => update('diet_type', opt.value)}
                style={{
                  width: '100%', padding: '14px', borderRadius: 10, marginBottom: 8,
                  cursor: 'pointer', textAlign: 'left', fontWeight: 600, fontSize: 15,
                  border: `2px solid ${form.diet_type === opt.value ? theme.green : theme.inputBorder}`,
                  background: form.diet_type === opt.value ? theme.greenBg : theme.inputBg,
                  color: form.diet_type === opt.value ? theme.greenDark : theme.text,
                }}>
                {opt.value === 'non-vegetarian' ? '🍗 ' : opt.value === 'vegetarian' ? '🌿 ' : '🌱 '}{opt.label}
              </motion.button>
            ))}
          </div>

          {/* Sensitivity Level */}
          <div style={sectionStyle}>
            <h3 style={{ fontWeight: 700, fontSize: 16, color: theme.text, marginBottom: 14 }}>Sensitivity Level</h3>
            {SENSITIVITY_OPTIONS.map(opt => (
              <motion.button key={opt.value} whileTap={{ scale: 0.97 }} onClick={() => update('sensitivity', opt.value)}
                style={{
                  width: '100%', padding: '14px 16px', borderRadius: 10, marginBottom: 8,
                  cursor: 'pointer', textAlign: 'left',
                  border: `2px solid ${form.sensitivity === opt.value ? theme.green : theme.inputBorder}`,
                  background: form.sensitivity === opt.value ? theme.greenBg : theme.inputBg,
                }}>
                <div style={{
                  fontWeight: 700, fontSize: 15,
                  color: form.sensitivity === opt.value ? theme.greenDark : theme.text,
                  marginBottom: 4,
                }}>
                  {opt.label}
                </div>
                <div style={{ fontSize: 13, color: theme.textMuted, lineHeight: 1.5 }}>
                  {opt.description}
                </div>
              </motion.button>
            ))}
            <p style={{ fontSize: 12, color: theme.textSubtle, marginTop: 8, lineHeight: 1.5, fontStyle: 'italic' }}>
              This changes how early we warn you — not the official health limits themselves.
            </p>
          </div>

          {/* Save */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleSave}
            disabled={saving}
            style={{
              width: '100%', padding: '16px', borderRadius: 12, border: 'none',
              background: 'linear-gradient(135deg, #22c55e, #16a34a)',
              color: 'white', fontWeight: 700, fontSize: 16, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              boxShadow: '0 4px 15px rgba(34,197,94,0.3)', marginBottom: 12,
            }}
          >
            <Save size={18} />
            {saving ? 'Saving...' : 'Save Changes'}
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={handleLogout}
            style={{
              width: '100%', padding: '14px', borderRadius: 12,
              border: `2px solid ${theme.isDark ? '#3b1212' : '#fee2e2'}`,
              background: theme.isDark ? '#1a0808' : 'white',
              color: '#dc2626', fontWeight: 600, fontSize: 15, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            <LogOut size={16} /> Reset Profile
          </motion.button>
        </motion.div>
      </div>
    </div>
  )
}
