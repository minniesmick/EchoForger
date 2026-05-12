<div align="center">

# 🔊 EchoForge

**Speech-to-Text · Text-to-Speech · Voice Pipeline**

*Whisper ile transkripsiyon yapın, XTTSv2 veya Fish Speech ile istediğiniz seste konuşturun.*

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?logo=qt&logoColor=white)
![Whisper](https://img.shields.io/badge/STT-faster--whisper-FF6B6B)
![License](https://img.shields.io/badge/License-MIT-6EE7B7)

</div>

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 📝 **Tekli Transkripsiyon** | Ses dosyasını seç, `large-v3-turbo` ile gerçek zamanlı akış |
| 📋 **Toplu İşlem Kuyruğu** | Onlarca dosyayı tek modelle sırayla işle, otomatik TXT/SRT/VTT kaydet |
| 🎙 **Ses Üretimi (TTS)** | XTTSv2 ile klonlama, Fish Speech ile yüksek kaliteli sentez |
| 🔗 **Pipeline** | Transkripsiyon metnini tek tıkla TTS sekmesine gönder |
| 🌊 **Waveform Görünümü** | pyqtgraph ile canlı dalga formu, süre / örnekleme hızı bilgisi |
| 💾 **Export** | TXT, SRT (altyazı), WebVTT — tek tek veya hepsini bir arada |

---

## 🗂 Proje Yapısı

```
echoforge/
├── main.py                    ← Giriş noktası
├── requirements.txt
│
├── core/                      ← İş mantığı (UI'sız)
│   ├── file_manager.py        ← Klasör yapısı, kaydetme yardımcıları
│   ├── transcriber.py         ← TranscriptionWorker (QThread + faster-whisper)
│   └── batch_worker.py        ← BatchWorker — modeli bir kez yükle, tüm kuyruğu işle
│
├── tts/                       ← Text-to-Speech motoru
│   ├── tts_engine.py          ← BaseTTSEngine, XTTSEngine, FishSpeechEngine
│   ├── text_preprocessor.py   ← Uzun metin → parça → birleştirme
│   └── workers.py             ← ModelLoaderWorker, TTSWorker, ChunkedTTSWorker
│
└── ui/                        ← Qt arayüzü
    ├── main_window.py         ← Ana pencere + sekme sistemi
    ├── file_panel.py          ← Dosya gezgini, drag & drop, QFileSystemWatcher
    ├── transcription_panel.py ← Tekli transkripsiyon + export butonları
    ├── queue_panel.py         ← Toplu işlem tablosu + ilerleme çubuğu
    ├── tts_panel.py           ← TTS kontrol paneli
    ├── waveform_widget.py     ← pyqtgraph waveform görselleştirici
    └── styles.py              ← MAIN_STYLESHEET, COLORS paleti
```

---

## ⚙️ Kurulum

### 1 — Depoyu klonla

```bash
git clone https://github.com/minniesmick/echoforge.git
cd echoforge
```

### 2 — Sanal ortam oluştur

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Bağımlılıkları kur

```bash
pip install -r requirements.txt
```

> **GPU (CUDA) için** — PyTorch'u CUDA destekli sürümle kur:
>
> ```bash
> pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```

### 4 — ffmpeg kur (ses birleştirme için)

| Platform | Komut |
|---|---|
| Windows | `winget install Gyan.FFmpeg` veya [ffmpeg.org](https://ffmpeg.org/download.html) |
| macOS | `brew install ffmpeg` |
| Ubuntu | `sudo apt install ffmpeg` |

### 5 — Fish Speech (opsiyonel, ayrı ortam)

Fish Speech farklı bir PyTorch versiyonu gerektirdiğinden ayrı bir ortamda çalışır:

```bash
python -m venv .venv_fish
.venv_fish\Scripts\activate
pip install fish-speech   # veya projenin kendi kurulum yönergesini takip edin
```

EchoForge, Fish Speech'i `subprocess` üzerinden çağırır — iki ortam birbirini etkilemez.

---

## 🚀 Kullanım

```bash
python main.py
```

### Hızlı başlangıç

1. **Sol panel** → `voice_files/` klasöründeki dosyalar listelenir; doğrudan dosya sürükleyebilirsiniz.
2. **📝 Transkribe Et** sekmesi → Dosyayı seçin, model seçin (varsayılan: `large-v3-turbo`), **Transkribe Et** düğmesine basın.
3. **Kaydet** düğmesi → TXT / SRT / VTT veya hepsini bir arada kaydedin. Çıktılar `output/transcripts/` altına yazılır.
4. **→ TTS'e Gönder** → Transkripsiyon metni otomatik olarak **🎙 Ses Üret** sekmesine aktarılır.
5. **📋 Toplu İşlem** → Ctrl/Shift ile çoklu seçim yapın, kuyruğa ekleyin, başlatın.

---

## 📁 Klasör Yapısı (Çalışma Zamanı)

```
echoforge/
├── voice_files/          ← STT giriş dosyaları (.mp3, .wav, .m4a, …)
├── reference_voices/     ← TTS klonlama referans sesleri (.wav)
└── output/
    ├── transcripts/      ← TXT / SRT / VTT çıktıları
    └── audio/            ← TTS WAV çıktıları
```

Uygulama ilk açılışta bu klasörleri otomatik oluşturur.

---

## 🖥 Sistem Gereksinimleri

| Bileşen | Minimum | Önerilen |
|---|---|---|
| Python | 3.10 | 3.11+ |
| RAM | 8 GB | 16 GB |
| GPU (VRAM) | — (CPU modu) | 8 GB+ (RTX 3060 Ti vb.) |
| Depolama | 5 GB | 10 GB+ (model dosyaları) |
| İşletim Sistemi | Windows 10, macOS 12, Ubuntu 20.04 | — |

### Whisper Model Boyutları

| Model | VRAM | Hız | Doğruluk |
|---|---|---|---|
| `tiny` | ~1 GB | ⚡⚡⚡⚡⚡ | ★☆☆ |
| `base` | ~1 GB | ⚡⚡⚡⚡ | ★★☆ |
| `small` | ~2 GB | ⚡⚡⚡ | ★★☆ |
| `medium` | ~5 GB | ⚡⚡ | ★★★ |
| `large-v3` | ~10 GB | ⚡ | ★★★ |
| `large-v3-turbo` | ~6 GB | ⚡⚡⚡ | ★★★ ✓ Önerilen |

---

## 🧩 Mimari Notlar

- **Thread güvenliği**: Tüm ağır işlemler (`TranscriptionWorker`, `BatchWorker`, `TTSWorker`) `QThread` alt sınıflarında çalışır; GUI thread'i hiçbir zaman bloklanmaz.
- **Bellek yönetimi**: `BatchWorker` modeli bir kez yükler ve tüm kuyruk için yeniden kullanır (her dosyada yeniden yükleme yok).
- **Fish Speech izolasyonu**: `subprocess` köprüsü sayesinde iki sanal ortam birbirinden tamamen bağımsızdır.
- **Chunk sistemi**: `TextPreprocessor`, 250 karakter üzeri metinleri cümle sınırlarından böler; `pydub` ile sessizlik ekleyerek birleştirir — XTTSv2'nin üretim kalitesi korunur.

---

## 📄 Lisans

MIT License — ayrıntılar için `LICENSE` dosyasına bakın.

---

<div align="center">
Made with ♥ and 🎙
</div>
