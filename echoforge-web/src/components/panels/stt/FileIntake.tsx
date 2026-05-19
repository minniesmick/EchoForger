import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import type { AudioFile } from '@/types'
import { LiveWaveform } from './LiveWaveform'
import { I } from '@/components/shared/Icons'

function fmt(t: number): string {
  const m = Math.floor(t / 60)
  const s = Math.floor(t % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

interface FileIntakeProps {
  file:         AudioFile | null
  onFile:       (f: AudioFile) => void
  recording:    boolean
  setRecording: (v: boolean) => void
}

export function FileIntake({ file, onFile, recording, setRecording }: FileIntakeProps) {
  const onDrop = useCallback((accepted: File[]) => {
    const f = accepted[0]
    if (!f) return
    // TODO Faz 8: POST /api/stt/upload → real metadata
    onFile({
      name:       f.name,
      size:       `${(f.size / 1_048_576).toFixed(1)} MB`,
      duration:   0,    // will be filled after server parse
      sampleRate: '—',
    })
  }, [onFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.opus'],
      'video/*': ['.mp4', '.mkv'],
    },
    maxSize: 2 * 1024 * 1024 * 1024, // 2 GB
    multiple: false,
    noClick: recording,
  })

  return (
    <div
      {...getRootProps()}
      className={`dropzone${isDragActive ? ' drag' : ''}`}
    >
      <input {...getInputProps()} />

      {/* Icon */}
      <div className="dropzone-icon">
		<I.audio style={{ width: 24, height: 24 }} />
	  </div>

      {/* Meta */}
      <div className="dropzone-meta">
        {file ? (
          <>
            <div className="dropzone-title">{file.name}</div>
            <div className="dropzone-sub">
              {file.size}
              {file.duration > 0 && ` · ${fmt(file.duration)}`}
              {file.sampleRate !== '—' && ` · ${file.sampleRate}`}
              &nbsp;·&nbsp;
              <span style={{ color: 'var(--violet-2)' }}>Click to replace</span>
            </div>
          </>
        ) : (
          <>
            <div className="dropzone-title">Drop audio file, or click to browse</div>
            <div className="dropzone-sub">
              WAV · MP3 · FLAC · M4A · OGG · MP4 · up to 2 GB
            </div>
          </>
        )}
      </div>

      <div className="dropzone-divider" />

      {/* Mic / recording area */}
      <AnimatePresence mode="wait">
        {recording ? (
          <motion.div
            key="recording"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.18 }}
            style={{ flex: 1, maxWidth: 360 }}
            onClick={(e) => e.stopPropagation()}
          >
            <LiveWaveform active={recording} />
            <div style={{ textAlign: 'center', marginTop: 8 }}>
              <button
                className="btn ghost sm"
                onClick={() => setRecording(false)}
              >
                <I.x /> Stop recording
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.14 }}
            style={{ textAlign: 'center' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="dropzone-sub" style={{ marginBottom: 8 }}>or capture live</div>
            <button
              className="mic-btn"
              onClick={() => setRecording(true)}
              title="Record from microphone"
            >
              <I.mic />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
