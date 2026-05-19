// ── STT ───────────────────────────────────────────────────────
export interface AudioFile {
  name:       string
  size:       string
  duration:   number   // seconds
  sampleRate: string
}

export interface Segment {
  t:    number          // start seconds
  end:  number
  spk:  number          // speaker index
  conf: number          // 0..1
  text: string
}

export type ExportFormat = 'srt' | 'vtt' | 'txt'
export type STTMode = 'transcribe' | 'sts'
export type WhisperModel = 'tiny' | 'base' | 'small' | 'medium' | 'large-v3'

// ── TTS ───────────────────────────────────────────────────────
export type TTSEngine = 'xtts' | 'kokoro' | 'hume'

export interface Voice {
  id:   string
  name: string
  meta: string
}

// ── Queue ─────────────────────────────────────────────────────
export type JobState = 'processing' | 'waiting' | 'done' | 'error'

export interface QueueJob {
  id:       string
  name:     string
  kind:     string
  size:     string
  model:    string
  state:    JobState
  progress: number   // 0..1
  time:     string
}

// ── Archive ───────────────────────────────────────────────────
export interface ArchiveDoc {
  id:       string
  title:    string
  date:     string
  dur:      string
  speakers: number
  words:    number
  snippet:  string
}

// ── Toast (re-export for convenience) ─────────────────────────
export type { Toast, ToastKind } from '@/stores/useAppStore'
