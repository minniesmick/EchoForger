# EchoForge — Proje Bağlamı

> Bu dosyayı yeni bir sohbette Claude'a at. Her şeyi bilecek.

---

## 👤 Kişi & Sistem

- **İsim:** Ben Alper — MEF Üniversitesi Bilgisayar Mühendisliği
- **OS:** Windows 11
- **GPU:** NVIDIA RTX 3060 Ti (8 GB VRAM)
- **Python:** 3.11
- **Node:** 24

### Ortamlar
| Ortam | Kullanım | CUDA |
|---|---|---|
| `.venv` | XTTSv2 + Whisper | 11.8 (cu118) |
| `.venv_fish` | Fish Speech | 12.1 (cu121) |

### Depolama
- SSD ömrü için sanal ortamlar `mklink /J` ile `D:\AI_Ortak_Venv`'e yönlendirilmiş
- Venv'ler junction'lı olduğundan normal görünür

### Kod Kuralları
- Her zaman **Windows yolları + PowerShell** sözdizimi
- pip hatasında `python -m pip` hatırlat
- CUDA uyumluluğunu her zaman gözet

---

## 🏗️ Proje Yapısı

```
C:\Users\alper\PROJELER\EchoForge\
├── echoforge-web/          ← React/Vite/TS frontend (BU SOHBETTE YAPILDI)
│   ├── src/
│   │   ├── App.tsx                          ← Ana layout, AnimatePresence
│   │   ├── main.tsx                         ← Entry point
│   │   ├── index.css                        ← Tüm CSS (design token'ları + paneller)
│   │   ├── stores/
│   │   │   └── useAppStore.ts               ← Zustand global state
│   │   ├── types/
│   │   │   └── index.ts                     ← TypeScript tipleri
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx              ← Framer Motion collapse
│   │   │   │   ├── Topbar.tsx               ← VRAM meter, status chips
│   │   │   │   └── ToastStack.tsx           ← Framer Motion toast
│   │   │   ├── shared/
│   │   │   │   ├── Icons.tsx                ← Tüm SVG iconlar
│   │   │   │   ├── Switch.tsx               ← Framer Motion spring thumb
│   │   │   │   ├── Segmented.tsx            ← Animated tab control
│   │   │   │   └── Slider.tsx               ← Range input (TTS için)
│   │   │   └── panels/
│   │   │       ├── Dashboard.tsx            ← GPU ring, metrics, activity
│   │   │       ├── STT.tsx                  ← Ana STT paneli
│   │   │       ├── TTS.tsx                  ← TTS Studio
│   │   │       ├── TTT.tsx                  ← Chat paneli
│   │   │       ├── Queue.tsx                ← Job queue tablosu
│   │   │       ├── Archive.tsx              ← Transcript archive + search
│   │   │       ├── Settings.tsx             ← 4 bölümlü ayarlar
│   │   │       └── stt/                     ← STT alt komponentleri
│   │   │           ├── AudioPlayer.tsx
│   │   │           ├── FileIntake.tsx       ← react-dropzone
│   │   │           ├── LiveWaveform.tsx     ← rAF animasyonlu
│   │   │           └── TranscriptList.tsx   ← Framer Motion stagger
│   ├── package.json
│   ├── vite.config.ts                       ← /api proxy → 8000, /ws proxy
│   ├── tailwind.config.ts                   ← CSS var'larına referans
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── postcss.config.js
│   └── index.html
│
├── yeniler/                ← Deploy klasörü (Claude çıktıları buraya gelir)
│   └── deploy.ps1          ← Otomatik dosya yerleştirme scripti
│
├── core/                   ← Mevcut Python backend (DEĞİŞMEDİ)
│   ├── transcriber.py      ← faster-whisper STT
│   ├── batch_worker.py
│   ├── file_manager.py
│   ├── archive_manager.py
│   ├── ollama_client.py
│   ├── gemini_client.py
│   └── settings_manager.py
│
└── tts/                    ← Mevcut TTS motoru (DEĞİŞMEDİ)
    ├── tts_engine.py       ← XTTSv2 + Kokoro + Hume TADA
    ├── workers.py          ← QThread worker'lar
    └── text_preprocessor.py
```

---

## 🎨 Frontend Stack

| Teknoloji | Versiyon | Kullanım |
|---|---|---|
| React | 18.3.1 | UI |
| TypeScript | 5.4.5 | Tip güvenliği |
| Vite | 5.3.1 | Dev server + build |
| Tailwind CSS | 3.4.4 | Layout utilities |
| Framer Motion | 11.2.10 | Animasyonlar |
| Zustand | 4.5.2 | Global state |
| react-dropzone | 14.2.3 | Dosya yükleme |
| react-router-dom | 6.23.1 | Routing (kurulu ama henüz aktif değil) |

### Design System
- **Font:** Geist + Geist Mono (Google Fonts)
- **Tema:** Sadece dark mode
- **Renkler:** CSS custom properties (`--violet`, `--cyan`, `--surface-*` vb.)
- **Kaynak tasarım:** `EchoForge_Dashboard.html` + `styles.css` (orijinal design dosyaları)

---

## ✅ Tamamlanan Fazlar

### Faz 1 — Scaffold
- Vite + React + TS + Tailwind kurulumu
- `package.json`, `vite.config.ts`, `tailwind.config.ts`, `tsconfig.json`
- `/api` → `localhost:8000` proxy, `/ws` → WebSocket proxy

### Faz 2 — CSS Token Migration
- `styles.css` → `src/index.css`
- Tüm CSS custom property'ler korundu
- Tailwind config CSS var'larına referans veriyor

### Faz 3 — Shell / Layout Components
- `Sidebar.tsx` — Framer Motion spring collapse (232px ↔ 64px)
- `Topbar.tsx` — `useSpring` VRAM bar, breadcrumb animasyonu
- `ToastStack.tsx` — `AnimatePresence` toast
- `Icons.tsx` — 35+ SVG ikon, typed
- `Switch.tsx`, `Segmented.tsx` — Framer Motion spring
- `useAppStore.ts` — Zustand: activePanel, collapsed, vram, toasts, status

### Faz 4 — STT Panel
- `STT.tsx` — Ana panel (mock data `MOCK_*` sabitleri ile izole)
- `AudioPlayer.tsx` — rAF playback clock, seek, PlayerViz
- `FileIntake.tsx` — react-dropzone entegrasyonu
- `LiveWaveform.tsx` — rAF animasyonu
- `TranscriptList.tsx` — Framer Motion stagger, speaker renkleri

### Faz 5 — Diğer Paneller
- `Dashboard.tsx` — GPU ring SVG, metric kartlar, quick start (navigate'e bağlı)
- `TTS.tsx` — Engine tiles, voice cards, reference dropzone, Slider
- `TTT.tsx` — AnimatePresence mesaj animasyonu, Ollama/Gemini segmented
- `Queue.tsx` — motion.div progress bar, KindBadge renkleri
- `Archive.tsx` — Framer Motion height expand, keyword highlight
- `Settings.tsx` — 4 bölüm sticky nav, gerçek Windows path'leri
- `Slider.tsx` — TTS için range slider komponenti

### Deploy Sistemi
- `yeniler/` klasörüne dosyaları koy
- `deploy.ps1` scripti dosyaları otomatik doğru yerlere kopyalar
- Her faz sonunda script güncellenir

---

## ⏳ Yapılacaklar

### Faz 6 — App.tsx Routing Refinement
- [ ] React Router v6 `HashRouter` aktif et (şu an `useState` routing var)
- [ ] URL ↔ panel sync (`/stt`, `/tts` vb.)
- [ ] `React.lazy()` + `Suspense` zaten var, test et
- [ ] `Dashboard` stub'daki "GPU · RTX 4090 · 24 GB" yazısı RTX 3060 Ti · 8 GB olarak güncellendi ama kontrol et

### Faz 7 — FastAPI Backend Skeleton
Dosya: `echoforge-web/../backend/` veya mevcut proje köküne entegre

```
backend/
├── main.py              ← FastAPI app, CORS, lifespan (model preload)
├── routers/
│   ├── stt.py           ← POST /api/stt/transcribe, GET /api/stt/status/{job_id}
│   │                       GET /api/stt/export/{job_id}?fmt=srt|vtt|txt
│   ├── tts.py           ← POST /api/tts/generate, GET /api/tts/download/{id}
│   ├── ttt.py           ← POST /api/ttt/chat (SSE stream)
│   ├── queue.py         ← GET /api/queue, DELETE /api/queue/{id}
│   ├── archive.py       ← GET /api/archive/search?q=..., POST /api/archive/reindex
│   └── system.py        ← GET /api/system/stats (VRAM, GPU util)
│                           WS  /ws/system (real-time VRAM stream)
├── schemas/
│   └── models.py        ← Pydantic request/response modelleri
└── core/                ← Mevcut core/* Python modüllerini wrap eder
```

**Kritik:** `core/` ve `tts/` modülleri PyQt6'ya bağımlı (QThread sinyalleri). FastAPI entegrasyonunda bunlar asyncio uyumlu wrapper'lara alınmalı.

### Faz 8 — API Client + Hooks + WebSocket
- [ ] `src/api/client.ts` — typed fetch wrapper, abort controller, error handling
- [ ] `src/hooks/useSTT.ts` — WebSocket veya polling ile job status
- [ ] `src/hooks/useVram.ts` — `ws://localhost:8000/ws/system` real-time VRAM
- [ ] `src/hooks/useTTS.ts` — generate + download
- [ ] `src/hooks/useArchive.ts` — search, reindex
- [ ] Tüm `MOCK_*` sabitleri sökülür, gerçek API'ye bağlanır
- [ ] `useAppStore` `vramDrift` simülasyonu → `useVram()` hook ile değiştirilir

### Faz 9 — Polish & Eksikler
- [ ] STT AudioPlayer: sadece `duration > 0` iken görünür — server'dan parse döndükten sonra açılacak
- [ ] Dashboard'daki mock istatistikler (`1,284 files` vb.) API'den gelmeli
- [ ] Queue'da real-time progress WebSocket ile güncellenmeli
- [ ] Settings: form submit → `PUT /api/settings` endpoint
- [ ] TTT: SSE stream token-by-token rendering
- [ ] `nav-item.active::before` violet bar eksik (CSS'e eklenmeli)
- [ ] Sidebar footer avatar: "SO" → "BA" düzeltildi, tekrar kontrol et

---

## 🐛 Bilinen Sorunlar / Notlar

| Sorun | Durum | Çözüm |
|---|---|---|
| `.app` grid CSS eksikti | ✅ Çözüldü | `index.css`'e eklendi |
| STT transcript alt alta görünüyordu | ✅ Çözüldü | `index.css` son versiyonla |
| `main.tsx` deploy scriptinde eksikti | ✅ Elle eklendi | Script'e dahil edildi |
| Dashboard stub paneller | ✅ Çözüldü | Faz 5'te gerçek component'ler yazıldı |
| `faz5-append.css` otomatik eklenmemişti | ✅ Çözüldü | Tam `index.css` yeniden üretildi |
| AudioPlayer mock file'da `duration: 197.4` var | ⚠️ Mock | Faz 8'de server'dan gelecek |
| Archive filter sadece keyword match yapıyor | ⚠️ Mock | Faz 8'de `/api/archive/search` |
| PyQt6 core modülleri FastAPI ile uyumsuz | ⚠️ Bekliyor | Faz 7'de asyncio wrapper |

---

## 🔧 Geliştirme Komutları

```powershell
# Frontend başlat
cd C:\Users\alper\PROJELER\EchoForge\echoforge-web
npm run dev
# → http://localhost:5173

# Build
npm run build

# Deploy (yeni dosyaları yerleştir)
.\yeniler\deploy.ps1
```

---

## 📋 Hızlı Tanılama Bloğu

Yeni sohbette Claude'a şunu ver:

```
Proje: EchoForge | OS: Win11 | GPU: RTX 3060 Ti | Python 3.11 | Node 24
Stack: FastAPI backend + React/Vite/TS/Tailwind/shadcn/Framer Motion frontend
Durum: Faz 1-5 tamamlandı (scaffold + tüm paneller çalışıyor)
Sıradaki: Faz 6 (routing) veya Faz 7 (FastAPI skeleton)
Dosyalar: C:\Users\alper\PROJELER\EchoForge\echoforge-web\
Deploy: yeniler/ klasörüne koy → deploy.ps1 çalıştır
```

---

## 🎯 Aktif Skill'ler

- `frontend-design` — Framer Motion animasyon kararları, design token, mikrointeraksiyonlar
- Gelecekte `FastAPI` + `asyncio` için backend skill gerekebilir

---

*Son güncelleme: Faz 5 tamamlandı — tüm paneller çalışır durumda, API bağlantısı yok (mock data)*
