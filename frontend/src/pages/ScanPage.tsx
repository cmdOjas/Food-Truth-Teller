import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ScanLine, Keyboard, X, Camera, Package, ChevronRight } from 'lucide-react'
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats } from 'html5-qrcode'
import Navbar from '../components/Navbar'
import { productApi } from '../services/api'

const RECENT_KEY = 'recent_scans'

function getRecentScans(): string[] {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
  } catch {
    return []
  }
}

function addRecentScan(barcode: string) {
  const scans = getRecentScans()
  const updated = [barcode, ...scans.filter(s => s !== barcode)].slice(0, 5)
  localStorage.setItem(RECENT_KEY, JSON.stringify(updated))
}

export default function ScanPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'idle' | 'camera' | 'manual'>('idle')
  const [manual, setManual] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [recentScans, setRecentScans] = useState<string[]>(getRecentScans())
  const [loadingBarcode, setLoadingBarcode] = useState('')
  const scannerRef = useRef<Html5QrcodeScanner | null>(null)
  const userName = localStorage.getItem('user_name') || 'there'

  const handleScan = async (barcode: string) => {
    setError('')
    setSuccess(true)
    setLoadingBarcode(barcode)
    addRecentScan(barcode)
    setRecentScans(getRecentScans())

    // Brief success animation before navigating
    setTimeout(() => {
      navigate(`/results/${barcode}`)
    }, 600)
  }

  useEffect(() => {
    if (mode !== 'camera') return

    const scanner = new Html5QrcodeScanner(
      'qr-reader',
      {
        fps: 10,
        qrbox: { width: 260, height: 120 },
        rememberLastUsedCamera: true,
        supportedScanTypes: [],
        formatsToSupport: [
          Html5QrcodeSupportedFormats.EAN_13,
          Html5QrcodeSupportedFormats.UPC_A,
          Html5QrcodeSupportedFormats.UPC_E,
          Html5QrcodeSupportedFormats.EAN_8,
          Html5QrcodeSupportedFormats.CODE_128,
        ],
      },
      false,
    )

    scanner.render(
      (decodedText) => {
        scanner.clear().catch(() => {})
        handleScan(decodedText.trim())
      },
      () => {},
    )

    scannerRef.current = scanner

    return () => {
      scannerRef.current?.clear().catch(() => {})
    }
  }, [mode])

  const handleManualSubmit = () => {
    const barcode = manual.trim()
    if (!barcode) {
      setError('Please enter a barcode number')
      return
    }
    handleScan(barcode)
  }

  const handleRecentScan = (barcode: string) => {
    navigate(`/results/${barcode}`)
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      <Navbar />
      <div style={{ paddingTop: 80, maxWidth: 600, margin: '0 auto', padding: '80px 1rem 2rem' }}>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', marginBottom: 32 }}
        >
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#111827', marginBottom: 8 }}>
            Hi {userName}! 👋
          </h1>
          <p style={{ color: '#6b7280', fontSize: 16 }}>
            Scan a product barcode to check if it's right for you.
          </p>
        </motion.div>

        {/* Success overlay */}
        <AnimatePresence>
          {success && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              style={{
                position: 'fixed', inset: 0, zIndex: 999,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
              }}
            >
              <motion.div
                animate={{ scale: [1, 1.15, 1] }}
                transition={{ duration: 0.5, times: [0, 0.5, 1] }}
                style={{
                  background: 'white', borderRadius: 24, padding: '2.5rem 3rem',
                  textAlign: 'center', boxShadow: '0 25px 60px rgba(0,0,0,0.2)',
                }}
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  style={{ fontSize: 64, marginBottom: 12 }}
                >
                  ✅
                </motion.div>
                <h3 style={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>Barcode Detected!</h3>
                <p style={{ color: '#6b7280', fontSize: 15, marginTop: 4 }}>
                  {loadingBarcode}
                </p>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action cards */}
        {mode === 'idle' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 32 }}>
              <motion.button
                whileHover={{ scale: 1.03, y: -3 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setMode('camera')}
                style={{
                  padding: '2rem 1rem', borderRadius: 20, border: '2px solid #22c55e',
                  background: 'linear-gradient(135deg, #f0fdf4, #dcfce7)',
                  cursor: 'pointer', textAlign: 'center',
                  boxShadow: '0 4px 20px rgba(34,197,94,0.15)',
                }}
              >
                <Camera size={36} color="#22c55e" style={{ margin: '0 auto 12px' }} />
                <div style={{ fontWeight: 700, fontSize: 16, color: '#166534' }}>Scan Barcode</div>
                <div style={{ fontSize: 13, color: '#16a34a', marginTop: 4 }}>Use Camera</div>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.03, y: -3 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setMode('manual')}
                style={{
                  padding: '2rem 1rem', borderRadius: 20, border: '2px solid #e5e7eb',
                  background: 'white', cursor: 'pointer', textAlign: 'center',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                }}
              >
                <Keyboard size={36} color="#6b7280" style={{ margin: '0 auto 12px' }} />
                <div style={{ fontWeight: 700, fontSize: 16, color: '#374151' }}>Enter Code</div>
                <div style={{ fontSize: 13, color: '#9ca3af', marginTop: 4 }}>Type Manually</div>
              </motion.button>
            </div>

            {/* Browse all products */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate('/results/browse')}
              style={{
                width: '100%', padding: '16px', borderRadius: 14, border: '2px dashed #d1d5db',
                background: 'white', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                color: '#6b7280', fontWeight: 600, fontSize: 15, marginBottom: 32,
              }}
            >
              <Package size={20} />
              Browse 20 Sample Products
            </motion.button>

            {/* Recent scans */}
            {recentScans.length > 0 && (
              <div>
                <h3 style={{ fontWeight: 700, fontSize: 16, color: '#374151', marginBottom: 12 }}>
                  Recent Scans
                </h3>
                {recentScans.map((barcode, i) => (
                  <motion.button
                    key={barcode}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRecentScan(barcode)}
                    style={{
                      width: '100%', padding: '14px 16px', borderRadius: 12,
                      border: '1px solid #e5e7eb', background: 'white',
                      cursor: 'pointer', textAlign: 'left', marginBottom: 8,
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <ScanLine size={16} color="#22c55e" />
                      <span style={{ fontWeight: 500, fontSize: 15, color: '#374151' }}>{barcode}</span>
                    </div>
                    <ChevronRight size={16} color="#9ca3af" />
                  </motion.button>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Camera Scanner */}
        {mode === 'camera' && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div style={{
              background: 'white', borderRadius: 20, padding: '1.5rem',
              boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
              border: '1px solid #e5e7eb',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2 style={{ fontWeight: 700, fontSize: 18, color: '#111827' }}>
                  📷 Point at barcode
                </h2>
                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={() => { scannerRef.current?.clear().catch(() => {}); setMode('idle') }}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
                >
                  <X size={22} color="#6b7280" />
                </motion.button>
              </div>

              <div style={{ borderRadius: 12, overflow: 'hidden' }}>
                <div id="qr-reader" />
              </div>

              <p style={{ textAlign: 'center', color: '#9ca3af', fontSize: 13, marginTop: 12 }}>
                Hold the barcode steady within the viewfinder · EAN-13, UPC-A supported
              </p>
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={() => setMode('manual')}
              style={{
                width: '100%', marginTop: 16, padding: '14px', borderRadius: 12,
                border: '2px solid #e5e7eb', background: 'white', cursor: 'pointer',
                fontWeight: 600, fontSize: 15, color: '#374151',
              }}
            >
              Can't scan? Enter manually →
            </motion.button>
          </motion.div>
        )}

        {/* Manual Entry */}
        {mode === 'manual' && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <div style={{
              background: 'white', borderRadius: 20, padding: '2rem',
              boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
              border: '1px solid #e5e7eb',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2 style={{ fontWeight: 700, fontSize: 18, color: '#111827' }}>
                  Enter Barcode Number
                </h2>
                <motion.button
                  whileTap={{ scale: 0.9 }}
                  onClick={() => { setMode('idle'); setManual(''); setError('') }}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
                >
                  <X size={22} color="#6b7280" />
                </motion.button>
              </div>

              <input
                value={manual}
                onChange={e => { setManual(e.target.value); setError('') }}
                onKeyDown={e => e.key === 'Enter' && handleManualSubmit()}
                placeholder="e.g. 049000006346"
                type="number"
                autoFocus
                style={{
                  width: '100%', padding: '14px 16px',
                  border: `2px solid ${error ? '#ef4444' : '#e5e7eb'}`,
                  borderRadius: 12, fontSize: 18, fontFamily: 'inherit',
                  outline: 'none', letterSpacing: '0.05em', marginBottom: 8,
                  background: 'white',
                }}
              />

              {error && <p style={{ color: '#ef4444', fontSize: 14, marginBottom: 12 }}>{error}</p>}

              <p style={{ color: '#9ca3af', fontSize: 13, marginBottom: 20 }}>
                Find the barcode number printed below the barcode stripes on the package.
              </p>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleManualSubmit}
                style={{
                  width: '100%', padding: '14px', borderRadius: 12, border: 'none',
                  background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                  color: 'white', fontWeight: 700, fontSize: 16, cursor: 'pointer',
                  boxShadow: '0 4px 15px rgba(34,197,94,0.3)',
                }}
              >
                Analyze This Product →
              </motion.button>
            </div>

            {/* Sample barcodes */}
            <div style={{ marginTop: 24 }}>
              <p style={{ fontSize: 14, color: '#6b7280', marginBottom: 12, fontWeight: 600 }}>
                Try a sample barcode:
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {[
                  { barcode: '049000006346', name: 'Coca-Cola' },
                  { barcode: '028400050845', name: "Lay's Chips" },
                  { barcode: '030000010112', name: 'Quaker Oats' },
                  { barcode: '074684006085', name: 'Häagen-Dazs' },
                ].map(item => (
                  <motion.button
                    key={item.barcode}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setManual(item.barcode)}
                    style={{
                      padding: '8px 12px', borderRadius: 8,
                      border: '1px solid #e5e7eb', background: 'white',
                      cursor: 'pointer', fontSize: 13, fontWeight: 500, color: '#374151',
                    }}
                  >
                    {item.name}
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
