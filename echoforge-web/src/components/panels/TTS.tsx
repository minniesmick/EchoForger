import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '@/stores/useAppStore'
import { AudioPlayer } from './stt/AudioPlayer'
import { Slider }     from '@/components/shared/Slider'
import { I }          from '@/components/shared/Icons'
import type { TTSEngine, AudioFile } from '@/types'

const VOICES = [
  { id: 'aria', name: 'Aria', meta: 'Female · warm · en-US',    grad: 'linear-gradient(135deg,#7c3aed,#22d3ee)' },
  { id: 'kai',  name: 'Kai',  meta: 'Male · neutral · en-US',   grad: 'linear-gradient(135deg,#06b6d4,#1e40af)' },
  { id: 'mei',  name: 'Mei',  meta: 'Female · bright · en-GB',  grad: 'linear-gradient(135deg,#ec4899,#f59e0b)' },
  { id: 'noor', name: 'Noor', meta: 'Cloned · 12s ref · custom',grad: 'linear-gradient(135deg,#22c55e,#7c3aed)'  },
]

const ENGINES = [
  { id: 'xtts',   name: 'XTTSv2',    meta: 'Local · clone' },
  { id: 'kokoro', name: 'Kokoro',     meta: 'Local · fast'  },
  { id: 'hume',   name: 'Hume TADA', meta: 'Cloud · emotive'},
]

const DUMMY_OUTPUT: AudioFile = {
  name: 'output_aria_xtts.wav', duration: 11.6, sampleRate: '24 kHz · mono · float', size: '—',
}

// ── Reference voice dropzone ──────────────────────────────────
function ReferenceDropzone() {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'audio/*': ['.wav', '.mp3', '.flac'] },
    maxFiles: 1,
  })
  return (
    <div {...getRootProps()} style={{
      border: `1.5px dashed ${isDragActive ? 'var(--violet)' : 'var(--border-2)'}`,
      borderRadius: 8, padding: 14, marginTop: 10,
      display: 'flex', alignItems: 'center', gap: 10,
      cursor: 'pointer', background: isDragActive ? 'var(--violet-dim)' : 'transparent',
      transition: 'all 180ms',
    }}>
      <input {...getInputProps()} />
      <I.upload style={{ width: 16, height: 16, color: 'var(--text-3)' }} />
      <div style={{ flex: 1, fontSize: 12 }}>
        <div style={{ fontWeight: 500 }}>noor_reference.wav</div>
        <div style={{ color: 'var(--text-3)', fontSize: 11 }}>6.2s · clean · ready for clone</div>
      </div>
      <button className="btn ghost sm"><I.play style={{ width: 10, height: 10 }} /></button>
    </div>
  )
}

// ── Panel ─────────────────────────────────────────────────────
export default function PanelTTS() {
  const pushToast = useAppStore((s) => s.pushToast)
  const [model,       setModel]    = useState<TTSEngine>('xtts')
  const [voice,       setVoice]    = useState('aria')
  const [lang,        setLang]     = useState('en-US')
  const [text,        setText]     = useState('In the silent observatory, the constellations whispered secrets that only the patient could hear. She tuned her instruments, and waited for the night to speak.')
  const [generated,   setGenerated]= useState(false)
  const [playing,     setPlaying]  = useState(false)
  const [currentTime, setCT]       = useState(0)

  const onGenerate = () => {
    // TODO Faz 8: POST /api/tts/generate
    pushToast({ kind: 'success', title: 'Generating speech', msg: 'XTTSv2 · ~11.6s estimated · queued' })
    setGenerated(true); setCT(0); setPlaying(false)
  }

  return (
    <div className="panel-inner">
      <div className="panel-header">
        <div>
          <h1 className="panel-title">TTS Studio</h1>
          <p className="panel-sub">Generate speech from text · voice cloning · multi-language</p>
        </div>
      </div>

      <div className="tts-grid">
        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Text input */}
          <div className="card card-pad">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <label className="field-label" style={{ margin: 0 }}>Text input</label>
              <span className="mono" style={{ fontSize: 11, color: 'var(--text-3)' }}>
                {text.length} chars · ~{(text.length / 14).toFixed(1)}s
              </span>
            </div>
            <textarea
              className="textarea"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type or paste text to synthesize…"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14 }}>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn ghost sm"><I.copy /> Paste</button>
                <button className="btn ghost sm"><I.file /> Load .txt</button>
                <button className="btn ghost sm"><I.brain /> Polish with LLM</button>
              </div>
              <button className="btn primary lg" onClick={onGenerate}>
                <I.zap /> Generate
              </button>
            </div>
          </div>

          {/* Output player */}
          {generated && (
            <div className="card">
              <div className="transcript-head">
                <div>
                  <div className="t-title">Output</div>
                  <div className="t-sub">{DUMMY_OUTPUT.name} · {DUMMY_OUTPUT.sampleRate}</div>
                </div>
                <div className="transcript-head-actions">
                  <span className="badge done"><span className="dot" />ready · 384ms</span>
                  <button className="btn ghost sm"><I.download /> WAV</button>
                  <button className="btn ghost sm"><I.download /> MP3</button>
                </div>
              </div>
              <div style={{ padding: 16 }}>
                <AudioPlayer
                  file={DUMMY_OUTPUT}
                  playing={playing}
                  setPlaying={setPlaying}
                  currentTime={currentTime}
                  setCurrentTime={setCT}
                />
              </div>
            </div>
          )}
        </div>

        {/* Right column — controls */}
        <div className="tts-controls">
          {/* Engine picker */}
          <div className="card card-pad">
            <label className="field-label">Engine</label>
            <div className="model-tiles">
              {ENGINES.map((e) => (
                <div
                  key={e.id}
                  className={`model-tile${model === e.id ? ' active' : ''}`}
                  onClick={() => setModel(e.id as TTSEngine)}
                >
                  <div className="mt-name">{e.name}</div>
                  <div className="mt-meta">{e.meta}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Language + voice */}
          <div className="card card-pad">
            <label className="field-label">Language</label>
            <select className="select" value={lang} onChange={(e) => setLang(e.target.value)}>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
              <option value="tr-TR">Turkish</option>
              <option value="es-ES">Spanish</option>
              <option value="fr-FR">French</option>
              <option value="de-DE">German</option>
              <option value="ja-JP">Japanese</option>
            </select>

            <label className="field-label" style={{ marginTop: 14 }}>Voice</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {VOICES.map((v) => (
                <div
                  key={v.id}
                  className={`voice-card${voice === v.id ? ' active' : ''}`}
                  onClick={() => setVoice(v.id)}
                >
                  <div className="va" style={{ background: v.grad }} />
                  <div style={{ flex: 1 }}>
                    <div className="v-name">{v.name}</div>
                    <div className="v-meta">{v.meta}</div>
                  </div>
                  {voice === v.id && <I.check style={{ width: 14, height: 14, color: 'var(--violet-2)' }} />}
                </div>
              ))}
            </div>
          </div>

          {/* Reference voice */}
          <div className="card card-pad">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <label className="field-label" style={{ margin: 0 }}>Reference voice</label>
              <span className="badge"><span className="dot" />6s clip ready</span>
            </div>
            <ReferenceDropzone />
          </div>

          {/* Sliders */}
          <div className="card card-pad">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <Slider label="Speed"       value={1.0}  min={0.5} max={2.0} step={0.05} suffix="×" />
              <Slider label="Temperature" value={0.7}  min={0}   max={1}   step={0.05} />
              <Slider label="Stability"   value={0.85} min={0}   max={1}   step={0.05} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
