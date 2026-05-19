import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '@/stores/useAppStore'
import { Segmented } from '@/components/shared/Segmented'
import { Switch }    from '@/components/shared/Switch'
import { I }         from '@/components/shared/Icons'

interface Message { role: 'user' | 'assistant'; text: string }

const INIT_MESSAGES: Message[] = [
  { role: 'user',      text: 'Summarize the architecture decisions for EchoForge v0.7 in 2 bullet points.' },
  { role: 'assistant', text: '• Whisper STT moves from CPU to local GPU node — roughly 6× faster, with the medium model loaded by default and large-v3 selectable from Settings.\n• STS pipeline streams sentence-by-sentence: each segment is dispatched to XTTSv2 (local) or Hume TADA (cloud, throttled) without waiting for the full transcript.' },
  { role: 'user',      text: 'How does the diarization layer fit in?' },
  { role: 'assistant', text: 'Diarization runs as a parallel pass on the same audio buffer using pyannote 3.1. Speaker labels are joined to Whisper segments by overlap — when the toggle is off, labels are still computed in the background but suppressed from the UI, so flipping the switch is instant with no re-run.' },
]

const msgVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.22, ease: [0.16, 1, 0.3, 1] } },
}

export default function PanelTTT() {
  const pushToast = useAppStore((s) => s.pushToast)
  const [backend,   setBackend]   = useState('ollama')
  const [translate, setTranslate] = useState(false)
  const [input,     setInput]     = useState('')
  const [messages,  setMessages]  = useState<Message[]>(INIT_MESSAGES)
  const msgsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight
  }, [messages])

  const send = () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', text: input }
    setMessages((m) => [...m, userMsg])
    setInput('')
    // TODO Faz 8: POST /api/ttt/stream → SSE stream
    setTimeout(() => {
      setMessages((m) => [...m, {
        role: 'assistant',
        text: `Streaming response from ${backend === 'ollama' ? 'llama3.1:8b-instruct' : 'gemini-1.5-pro'}… [Faz 8'de gerçek API bağlanacak]`,
      }])
    }, 800)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <div className="panel-inner" style={{ height: '100%' }}>
      <div className="panel-header">
        <div>
          <h1 className="panel-title">TTT Chat</h1>
          <p className="panel-sub">Text-to-text · local LLM (Ollama) or cloud (Gemini) · streaming</p>
        </div>
        <div className="panel-actions">
          <Segmented
            options={[
              { value: 'ollama',  label: 'Ollama',  icon: I.cpu   },
              { value: 'gemini',  label: 'Gemini',  icon: I.globe },
            ]}
            value={backend}
            onChange={setBackend}
          />
        </div>
      </div>

      {/* Model info bar */}
      <div className="card card-pad" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>MODEL</span>
            <span className="mono" style={{ fontSize: 12 }}>
              {backend === 'ollama' ? 'llama3.1:8b-instruct-q4' : 'gemini-1.5-pro'}
            </span>
          </div>
          <div style={{ width: 1, height: 16, background: 'var(--border)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--text-3)' }}>CONTEXT</span>
            <span className="mono" style={{ fontSize: 12 }}>2.4k / 32k</span>
          </div>
        </div>
        <Switch on={translate} onChange={setTranslate} label="Translation mode" />
      </div>

      {/* Chat area */}
      <div className="chat">
        <div className="chat-msgs" ref={msgsRef}>
          <AnimatePresence initial={false}>
            {messages.map((m, i) => (
              <motion.div
                key={i}
                className={`msg ${m.role}`}
                variants={msgVariants}
                initial="initial"
                animate="animate"
              >
                <div className="msg-avatar">
                  {m.role === 'user'
                    ? 'BA'
                    : <I.brain style={{ width: 14, height: 14 }} />}
                </div>
                <div>
                  <div className="msg-bubble">{m.text}</div>
                  {m.role === 'assistant' && (
                    <div className="msg-actions">
                      <button
                        className="msg-action"
                        onClick={() => pushToast({ kind: 'success', title: 'Sent to TTS Studio' })}
                      >
                        <I.speaker /> Send to TTS
                      </button>
                      <button className="msg-action"><I.copy /> Copy</button>
                      <button className="msg-action"><I.refresh /> Regenerate</button>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        <div className="chat-input-wrap">
          <textarea
            className="chat-input"
            placeholder={`Message ${backend === 'ollama' ? 'llama3.1' : 'Gemini'}… (Enter to send, Shift+Enter for newline)`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button className="chat-send" onClick={send}><I.send /></button>
        </div>
      </div>
    </div>
  )
}
