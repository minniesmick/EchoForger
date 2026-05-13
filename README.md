# EchoForge

> **Speech-to-Text · Text-to-Speech · Text Processing · Voice Cloning**
> A local-first, GPU-accelerated audio workstation built with PyQt6.

---

## Overview

EchoForge is a desktop application that combines **Whisper-based transcription**, **XTTSv2 voice synthesis**, and **Ollama-powered text processing** into a unified workflow. All heavy lifting runs on your local GPU — no cloud, no subscriptions.

Built for: Windows 11 · RTX 3060 Ti · Python 3.11

---

## Features

| Mode | Description | Backend |
|------|-------------|---------|
| **STT** — Speech → Text | Transcribe audio files with timestamps | faster-whisper (large-v3-turbo) |
| **TTS** — Text → Speech | Generate natural speech, voice cloning | Coqui XTTSv2 / Hume TADA |
| **TTT** — Text → Text | Translation, grammar check, summarize | Ollama (aya-expanse, qwen2.5, …) |
| **STS** — Speech → Speech | Re-voice audio with a different speaker | STT + TTS pipeline |

### Highlights

- **Real-time waveform** visualization (pyqtgraph)
- **Streaming output** — LLM tokens appear as they arrive
- **Chunked TTS** — long texts auto-split and merged with pydub
- **Batch transcription** queue with auto-save (TXT / SRT / VTT)
- **Pipeline bridges** — send transcription directly to TTS or TTT
- **Persistent settings** — all paths and parameters saved to `settings.json`
- **Cross-platform paths** — pathlib throughout, no hardcoded separators

---

## Project Structure

```
EchoForge/
├── main.py                  # Entry point
├── core/
│   ├── file_manager.py      # Path management, transcript export
│   ├── transcriber.py       # faster-whisper QThread worker
│   ├── batch_worker.py      # Batch transcription queue
│   ├── ollama_client.py     # Ollama API client + workers
│   └── settings_manager.py  # JSON-backed singleton settings
├── tts/
│   ├── tts_engine.py        # XTTSEngine, HumeTADAEngine, Factory
│   ├── workers.py           # ModelLoader, TTSWorker, ChunkedTTSWorker
│   └── text_preprocessor.py # Text splitting + audio merging
├── ui/
│   ├── main_window.py       # QMainWindow, tab orchestration
│   ├── welcome_panel.py     # Mode selection screen
│   ├── file_panel.py        # Left sidebar file browser
│   ├── transcription_panel.py
│   ├── queue_panel.py       # Batch processing UI
│   ├── tts_panel.py         # Voice synthesis UI
│   ├── ttt_panel.py         # LLM text processing UI
│   ├── waveform_widget.py   # pyqtgraph waveform
│   ├── settings_panel.py
│   └── styles.py            # Unified dark theme + COLORS dict
├── voice_files/             # STT input audio (gitignored)
├── reference_voices/        # TTS cloning reference WAVs (gitignored)
├── output/
│   ├── transcripts/         # TXT / SRT / VTT exports
│   └── audio/               # TTS WAV outputs
└── settings.json            # User settings (gitignored)
```

---

## Requirements

### System
- Windows 11 / macOS (CPU-only on Mac)
- NVIDIA GPU with CUDA 11.8 (for GPU acceleration)
- Python 3.11
- [Ollama](https://ollama.com) running locally (`ollama serve`)

### Python Environment

> **Install PyTorch first** (index-url required):

```powershell
pip install torch==2.0.1+cu118 torchaudio==2.0.2+cu118 `
  --index-url https://download.pytorch.org/whl/cu118
```

Then install remaining dependencies:

```powershell
pip install -r requirements.txt
```

### cuDNN Fix (if you see `cudnnGetLibConfig` error)

```powershell
pip install nvidia-cudnn-cu11==8.6.0.163
```

---

## Setup

### 1. Clone & create environment

```powershell
git clone https://github.com/yourname/EchoForge.git
cd EchoForge
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install torch==2.0.1+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

### 3. Configure model paths

Edit `settings.json` (auto-created on first run) or use the **Settings** tab:

```json
{
  "hf_cache_dir":    "D:\\AI_Ortak_Venv\\hf_cache",
  "tts_model_dir":   "D:\\Ses_Modelleri",
  "chunk_threshold": 250,
  "silence_ms":      400,
  "ollama_url":      "http://localhost:11434"
}
```

### 4. Pull an Ollama model

```powershell
ollama pull aya-expanse
ollama serve
```

### 5. Run

```powershell
python main.py
```

---

## Voice Cloning

Place `.wav` reference files in `reference_voices/`. The TTS panel will detect them automatically via `QFileSystemWatcher`. XTTSv2 requires WAV format; 10–30 seconds of clean speech works best.

---

## Supported Audio Formats

Input (STT): `.mp3` `.wav` `.m4a` `.ogg` `.flac` `.mp4` `.webm`

Output (TTS): `.wav`

---

## TTT — Text Processing Modes

| Action | What it does |
|--------|-------------|
| ✅ Yazım Kontrol | Grammar & spelling correction (Turkish-aware) |
| 📝 Özetle | Summarize |
| 🔤 Biçimlendir | Reformat into clean paragraphs |
| 🌐 Çevir | Translate to any language via scrollable list |
| Serbest Mod | Free-form prompt, `{text}` placeholder supported |

First-token latency is displayed after each request.

---

## Architecture Notes

- All heavy operations run in `QThread` subclasses — GUI never blocks
- `SettingsManager` is a singleton; any module can call `SettingsManager.instance().get(key)`
- TTS engine switching unloads the previous model from VRAM before loading the new one
- Ollama model switching sends `keep_alive: 0` to free GPU memory before loading the next model
- `FileManager` centralizes all path logic; output dirs are created automatically

---

## Roadmap

- [ ] SQLite history with semantic search (nomic-embed-text)
- [ ] Audio playback widget (play / pause / seek)
- [ ] Additional TTS voice model
- [ ] TTT → TTS pipeline (process text then synthesize)
- [ ] Ollama model management (pull / delete from UI)

---

## License

MIT
