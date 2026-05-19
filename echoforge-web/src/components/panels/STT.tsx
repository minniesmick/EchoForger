/**
 * STT Panel — Speech to Text
 *
 * Mock data lives in MOCK_* constants at the top.
 * Faz 8'de bunlar useSTT() hook'una taşınacak:
 *   const { segments, status, transcribe } = useSTT()
 */
import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { AudioFile, Segment, STTMode, WhisperModel, ExportFormat } from '@/types'
import { useAppStore } from '@/stores/useAppStore'
import { Switch }    from '@/components/shared/Switch'
import { Segmented } from '@/components/shared/Segmented'
import { I }         from '@/components/shared/Icons'
import { AudioPlayer }     from './stt/AudioPlayer'
import { FileIntake }      from './stt/FileIntake'
import { TranscriptList }  from './stt/TranscriptList'

// ── Mock data (replace with API in Faz 8) ────────────────────
const MOCK_FILE: AudioFile = {
  name:       'kickoff_meeting_2026-05-18.wav',
  size:       '14.8 MB',
  duration:   197.4,
  sampleRate: '48 kHz · stereo · 16-bit',
}

const MOCK_SEGMENTS: Segment[] = [
  { t: 0.0,  end: 4.2,  spk: 1, conf: 0.98, text: 'Alright everyone, thanks for joining. Let me share the plan for the v0.7 release real quick.' },
  { t: 4.6,  end: 8.9,  spk: 1, conf: 0.96, text: 'The big shift is moving Whisper inference off CPU and onto the local GPU node — should be roughly 6x faster.' },
  { t: 9.3,  end: 13.1, spk: 2, conf: 0.94, text: 'Nice. Are we still pinning to the medium model, or are we letting users pick large-v3?' },
  { t: 13.5, end: 18.0, spk: 1, conf: 0.97, text: 'Both. The Settings panel exposes the model selector. Default stays medium for VRAM headroom.' },
  { t: 18.4, end: 23.2, spk: 3, conf: 0.91, text: 'Question — when STS mode is on, does the pipeline buffer the whole transcript before passing to TTS, or stream sentence-by-sentence?' },
  { t: 23.6, end: 28.8, spk: 1, conf: 0.95, text: 'Sentence-by-sentence. We segment on the Whisper output and dispatch to XTTS as each segment closes.' },
  { t: 29.2, end: 33.4, spk: 2, conf: 0.89, text: 'Got it. And the Hume TADA path — that\'s still queued behind the API throttle, right?' },
  { t: 33.8, end: 38.6, spk: 1, conf: 0.93, text: 'Correct. Hume goes through the cloud throttle. XTTS and Kokoro are local, no rate limit.' },
  { t: 39.0, end: 44.5, spk: 3, conf: 0.96, text: 'Last thing — the speaker diarization toggle. Are we using pyannote, or did we end up on Sherpa?' },
  { t: 44.9, end: 49.7, spk: 1, conf: 0.62, text: 'Pyannote 3.1 with the diarization-3.1 pipeline. Sherpa was slower on long files.' },
  { t: 50.1, end: 54.4, spk: 2, conf: 0.94, text: 'Cool. I\'ll start on the Settings UI tomorrow. Anything else for me?' },
  { t: 54.8, end: 58.2, spk: 1, conf: 0.97, text: 'Just keep the Geist Mono in the transcript panel — it reads way better for long sessions.' },
]

const WHISPER_OPTIONS = [
  { value: 'tiny',     label: 'whisper-tiny · 39M'   },
  { value: 'base',     label: 'whisper-base · 74M'   },
  { value: 'small',    label: 'whisper-small · 244M' },
  { value: 'medium',   label: 'whisper-medium · 769M'},
  { value: 'large-v3', label: 'whisper-large-v3 · 1.55B' },
]

// ── STS pipeline banner ───────────────────────────────────────
const stsBannerVariants = {
  initial: { opacity: 0, height: 0, marginBottom: 0 },
  animate: { opacity: 1, height: 'auto', marginBottom: 16 },
  exit:    { opacity: 0, height: 0, marginBottom: 0 },
}

// ── Panel root ────────────────────────────────────────────────
interface PanelSTTProps {
  pushToast: ReturnType<typeof useAppStore>['pushToast']
}

export default function PanelSTT({ pushToast }: PanelSTTProps) {
  // ── Local UI state ──────────────────────────────────────────
  const [mode, setMode]         = useState<STTMode>('transcribe')
  const [diarize, setDiarize]   = useState(true)
  const [file, setFile]         = useState<AudioFile | null>(MOCK_FILE)
  const [recording, setRecording] = useState(false)
  const [playing, setPlaying]   = useState(false)
  const [currentTime, setCT]    = useState(11.3)
  const [model, setModel]       = useState<WhisperModel>('large-v3')
  const [lang, setLang]         = useState('auto')

  // ── Derived ─────────────────────────────────────────────────
  const activeIdx = useMemo(
    () => MOCK_SEGMENTS.findIndex((s) => currentTime >= s.t && currentTime <= s.end),
    [currentTime],
  )

  const avgConf = (
    MOCK_SEGMENTS.reduce((acc, s) => acc + s.conf, 0) / MOCK_SEGMENTS.length * 100
  ).toFixed(1)

  // ── Handlers ─────────────────────────────────────────────────
  const handleExport = (fmt: ExportFormat) => {
    // TODO Faz 8: GET /api/stt/export/{jobId}?fmt=srt
    pushToast({
      kind:  'success',
      title: `Exported ${fmt.toUpperCase()}`,
      msg:   `${file?.name.replace(/\.[^.]+$/, '') ?? 'transcript'}.${fmt} saved`,
    })
  }

  const handleModeChange = (next: string) => {
    setMode(next as STTMode)
    if (next === 'sts') {
      pushToast({ title: 'STS Mode active', msg: 'Transcribed segments will pipe to TTS Studio.' })
    }
  }

  const handleTranscribe = () => {
    // TODO Faz 8: POST /api/stt/transcribe → stream back segments
    pushToast({ kind: 'success', title: 'Transcription queued', msg: `${model} · ${file?.name}` })
  }

  return (
    <div className="panel-inner">
      {/* Header */}
      <div className="panel-header">
        <div>
          <h1 className="panel-title">Speech to Text</h1>
          <p className="panel-sub">Whisper local inference · transcribe files or stream from mic</p>
        </div>
        <div className="panel-actions">
          <Segmented
            options={[
              { value: 'transcribe', label: 'Transcribe', icon: I.mic  },
              { value: 'sts',        label: 'STS Mode',   icon: I.pipe },
            ]}
            value={mode}
            onChange={handleModeChange}
            stsAccent
          />
        </div>
      </div>

      {/* Toolbar */}
      <div className="stt-toolbar">
        <div className="row gap-2">
          <span className="field-label" style={{ margin: 0 }}>Model</span>
          <select
            className="select"
            style={{ width: 220 }}
            value={model}
            onChange={(e) => setModel(e.target.value as WhisperModel)}
          >
            {WHISPER_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
        <div className="row gap-2">
          <span className="field-label" style={{ margin: 0 }}>Language</span>
          <select
            className="select"
            style={{ width: 150 }}
            value={lang}
            onChange={(e) => setLang(e.target.value)}
          >
            <option value="auto">Auto-detect</option>
            <option value="en">English</option>
            <option value="tr">Turkish</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="ja">Japanese</option>
          </select>
        </div>
        <div style={{ flex: 1 }} />
        <Switch on={diarize} onChange={setDiarize} label="Speaker diarization" />
        <button className="btn primary" onClick={handleTranscribe}>
          <I.play style={{ width: 12, height: 12 }} /> Transcribe
        </button>
      </div>

      {/* STS pipeline banner */}
      <AnimatePresence>
        {mode === 'sts' && (
          <motion.div
            key="sts-banner"
            variants={stsBannerVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <div
              className="card glow"
              style={{
                padding: '12px 16px',
                display: 'flex', alignItems: 'center', gap: 12,
                background: 'linear-gradient(90deg, rgba(124,58,237,0.08), rgba(6,182,212,0.05))',
                borderColor: 'rgba(124,58,237,0.3)',
              }}
            >
              <div style={{
                width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                background: 'linear-gradient(135deg, var(--violet), var(--cyan))',
                display: 'grid', placeItems: 'center', color: 'white',
              }}>
                <I.pipe style={{ width: 16, height: 16 }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 500 }}>STS pipeline active</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
                  Transcribed segments will stream to{' '}
                  <span style={{ color: 'var(--cyan-2)' }}>TTS Studio</span>
                  {' '}as each sentence closes. Output: XTTSv2 · Aria (en-US)
                </div>
              </div>
              <button className="btn ghost sm">
                <I.settings style={{ width: 12, height: 12 }} /> Configure
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* File drop zone */}
      <FileIntake
        file={file}
        onFile={setFile}
        recording={recording}
        setRecording={setRecording}
      />

      {/* Transcript card */}
      <div className="card">
        <div className="transcript-head">
          <div>
            <div className="t-title">Transcript</div>
            <div className="t-sub">
              {MOCK_SEGMENTS.length} segments · {avgConf}% avg confidence
              {file?.duration ? ` · ${Math.floor(file.duration / 60)}:${String(Math.floor(file.duration % 60)).padStart(2, '0')}` : ''}
              {' · en (auto-detected)'}
            </div>
          </div>
          <div className="transcript-head-actions">
            <span className="badge processing">
              <span className="dot" />Streaming
            </span>
            <button className="btn ghost sm" onClick={() => handleExport('srt')}>
              <I.download /> SRT
            </button>
            <button className="btn ghost sm" onClick={() => handleExport('vtt')}>
              <I.download /> VTT
            </button>
            <button className="btn ghost sm" onClick={() => handleExport('txt')}>
              <I.download /> TXT
            </button>
          </div>
        </div>

        <TranscriptList
          segments={MOCK_SEGMENTS}
          diarize={diarize}
          activeIdx={activeIdx}
          onJump={setCT}
          streaming
        />
      </div>

      {/* Audio player */}
      {file && file.duration > 0 && (
        <AudioPlayer
          file={file}
          playing={playing}
          setPlaying={setPlaying}
          currentTime={currentTime}
          setCurrentTime={setCT}
        />
      )}
    </div>
  )
}
