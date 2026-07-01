import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Leaf } from 'lucide-react'
import Navbar from '../components/Navbar'
import { chatApi } from '../services/api'
import { useTheme } from '../context/ThemeContext'
import type { ChatMessage } from '../types'

const SUGGESTED = [
  'What should I avoid with diabetes?',
  'Tell me about my allergies',
  'Is this product safe for me?',
  'What are heart-healthy foods?',
  'How much sugar is too much?',
  'What hidden gluten sources should I know?',
]

function MessageBubble({ msg, theme }: { msg: ChatMessage; theme: ReturnType<typeof useTheme>['theme'] }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 10, alignItems: 'flex-end', marginBottom: 16,
      }}
    >
      {/* Avatar */}
      <div style={{
        width: 34, height: 34, borderRadius: '50%', flexShrink: 0,
        background: isUser ? theme.green : 'linear-gradient(135deg, #166534, #16a34a)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {isUser ? <User size={16} color="white" /> : <Leaf size={16} color="white" />}
      </div>

      {/* Bubble */}
      <div style={{
        maxWidth: '75%',
        background: isUser
          ? 'linear-gradient(135deg, #22c55e, #16a34a)'
          : theme.cardBg,
        color: isUser ? 'white' : theme.text,
        padding: '12px 16px', borderRadius: isUser ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
        boxShadow: theme.isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)',
        border: isUser ? 'none' : `1px solid ${theme.cardBorder}`,
        fontSize: 14, lineHeight: 1.7,
        whiteSpace: 'pre-line',
      }}>
        {msg.content.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
          part.startsWith('**') && part.endsWith('**') ? (
            <strong key={i}>{part.slice(2, -2)}</strong>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </div>
    </motion.div>
  )
}

function TypingIndicator({ theme }: { theme: ReturnType<typeof useTheme>['theme'] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      style={{ display: 'flex', gap: 10, alignItems: 'flex-end', marginBottom: 16 }}
    >
      <div style={{
        width: 34, height: 34, borderRadius: '50%',
        background: 'linear-gradient(135deg, #166534, #16a34a)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Leaf size={16} color="white" />
      </div>
      <div style={{
        background: theme.cardBg, padding: '12px 16px', borderRadius: '4px 18px 18px 18px',
        border: `1px solid ${theme.cardBorder}`,
        boxShadow: theme.isDark ? '0 2px 8px rgba(0,0,0,0.25)' : '0 2px 8px rgba(0,0,0,0.06)',
        display: 'flex', gap: 4, alignItems: 'center',
      }}>
        {[0, 1, 2].map(i => (
          <motion.div key={i}
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }}
            style={{ width: 7, height: 7, borderRadius: '50%', background: theme.textSubtle }}
          />
        ))}
      </div>
    </motion.div>
  )
}

export default function ChatPage() {
  const location = useLocation()
  const { theme } = useTheme()
  const productBarcode = new URLSearchParams(location.search).get('barcode') || undefined
  const userId = parseInt(localStorage.getItem('user_id') || '0')
  const userName = localStorage.getItem('user_name') || 'there'

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '0', role: 'bot', timestamp: new Date().toISOString(),
      content: `Hello ${userName}! 🌿 I'm your EatWise AI assistant.\n\nI can help you understand how different foods affect your health, explain ingredients, and answer questions about your profile.\n\nWhat would you like to know?`,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text: string) => {
    const msg = text.trim()
    if (!msg || loading) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(), role: 'user',
      content: msg, timestamp: new Date().toISOString(),
    }
    setMessages(m => [...m, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await chatApi.send(userId, msg, productBarcode)
      setMessages(m => [...m, {
        id: (Date.now() + 1).toString(), role: 'bot',
        content: response, timestamp: new Date().toISOString(),
      }])
    } catch {
      setMessages(m => [...m, {
        id: (Date.now() + 1).toString(), role: 'bot',
        content: 'Sorry, I could not get a response. Please try again.',
        timestamp: new Date().toISOString(),
      }])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: theme.pageBg, display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      {/* Chat container */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        maxWidth: 640, width: '100%', margin: '0 auto',
        paddingTop: 64,
      }}>
        {/* Chat header */}
        <div style={{
          padding: '1rem 1.5rem', borderBottom: `1px solid ${theme.cardBorder}`,
          background: theme.cardBg, display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <div style={{
            width: 42, height: 42, borderRadius: 12,
            background: 'linear-gradient(135deg, #166534, #22c55e)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Bot size={22} color="white" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: theme.text }}>EatWise AI</div>
            <div style={{ fontSize: 13, color: theme.green, display: 'flex', alignItems: 'center', gap: 4 }}>
              <div style={{ width: 7, height: 7, borderRadius: '50%', background: theme.green }} />
              Online · Personalized to your profile
            </div>
          </div>
          {productBarcode && (
            <div style={{
              marginLeft: 'auto', background: theme.greenBg, color: theme.greenDark,
              padding: '4px 10px', borderRadius: 999, fontSize: 12, fontWeight: 600,
              border: `1px solid ${theme.isDark ? '#1a4a28' : 'transparent'}`,
            }}>
              Product: {productBarcode}
            </div>
          )}
        </div>

        {/* Messages */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '1.5rem',
          display: 'flex', flexDirection: 'column',
        }}>
          <AnimatePresence>
            {messages.map(msg => <MessageBubble key={msg.id} msg={msg} theme={theme} />)}
            {loading && <TypingIndicator theme={theme} />}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Suggested prompts */}
        {messages.length <= 2 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ padding: '0 1.5rem 1rem', display: 'flex', flexWrap: 'wrap', gap: 6 }}
          >
            {SUGGESTED.map(s => (
              <motion.button
                key={s}
                whileTap={{ scale: 0.95 }}
                onClick={() => sendMessage(s)}
                style={{
                  padding: '7px 12px', borderRadius: 999,
                  border: `1px solid ${theme.cardBorder}`,
                  background: theme.cardBg,
                  fontSize: 13, color: theme.text, cursor: 'pointer', fontWeight: 500,
                  transition: 'all 0.15s',
                }}
              >
                {s}
              </motion.button>
            ))}
          </motion.div>
        )}

        {/* Input bar */}
        <div style={{
          padding: '1rem 1.5rem', borderTop: `1px solid ${theme.cardBorder}`,
          background: theme.cardBg,
          display: 'flex', gap: 10, alignItems: 'flex-end',
        }}>
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
            placeholder="Ask about your food or health..."
            style={{
              flex: 1, padding: '12px 16px', borderRadius: 12,
              border: `2px solid ${theme.inputBorder}`, fontSize: 15, fontFamily: 'inherit',
              outline: 'none', background: theme.inputBg, color: theme.text,
              resize: 'none', transition: 'border-color 0.2s',
            }}
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            style={{
              width: 46, height: 46, borderRadius: 12, border: 'none', flexShrink: 0,
              background: input.trim() && !loading ? 'linear-gradient(135deg, #22c55e, #16a34a)' : theme.stepNumBg,
              color: input.trim() && !loading ? 'white' : theme.textSubtle,
              cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s',
            }}
          >
            <Send size={18} />
          </motion.button>
        </div>
      </div>
    </div>
  )
}
