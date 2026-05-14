# core/mic_worker.py
"""
EchoForge — Gerçek Zamanlı Mikrofon Transkripsiyon Worker'ı.

Akış:
    1. sounddevice ile mikrofondan ses yakala (chunk'lar halinde)
    2. Belirli süre dolunca veya kullanıcı durdurунca kayıt biter
    3. Geçici WAV dosyasına yaz
    4. faster-whisper ile transkribe et
    5. Segment sinyalleri yayınla

Sinyaller TranscriptionWorker ile birebir aynı —
transcription_panel.py her ikisini ayırt etmeden kullanabilir.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class MicWorker(QThread):
    """
    Mikrofonu dinler, transkribe eder.

    Sinyaller:
        progress(str)            → durum mesajları
        recording_started()      → kayıt başladı (UI güncelleme için)
        segment(float,float,str) → TranscriptionWorker ile aynı
        finished(str)            → tüm metin
        error(str)               → hata
        level(float)             → ses seviyesi 0.0–1.0 (VU meter için)
    """

    progress          = pyqtSignal(str)
    recording_started = pyqtSignal()
    segment           = pyqtSignal(float, float, str)
    finished          = pyqtSignal(str)
    error             = pyqtSignal(str)
    level             = pyqtSignal(float)

    SAMPLE_RATE = 16_000   # Whisper 16kHz bekler
    CHANNELS    = 1
    DTYPE       = "float32"

    def __init__(
        self,
        model_size: str = "large-v3-turbo",
        denoise:    bool = False,
        max_sec:    int  = 300,   # maksimum kayıt süresi (saniye)
    ) -> None:
        super().__init__()
        self.model_size    = model_size
        self.denoise       = denoise
        self.max_sec       = max_sec
        self._stop_flag    = False
        self._chunks: list[np.ndarray] = []

    # ── Durdurma ─────────────────────────────────────────────────────

    def stop(self) -> None:
        self._stop_flag = True

    # ── Ana döngü ────────────────────────────────────────────────────

    def run(self) -> None:
        try:
            import sounddevice as sd
        except ImportError:
            self.error.emit(
                "sounddevice kurulu değil.\n"
                "Kurulum: pip install sounddevice"
            )
            return

        try:
            self._chunks.clear()
            self._stop_flag = False

            self.progress.emit("🎤 Mikrofon başlatılıyor…")

            # ── Kayıt ─────────────────────────────────────────────
            CHUNK = int(self.SAMPLE_RATE * 0.1)   # 100ms chunk

            def _callback(indata, frames, time, status):
                if status:
                    pass   # taşma/düşme uyarılarını yut
                chunk = indata[:, 0].copy()
                self._chunks.append(chunk)
                # VU meter
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                self.level.emit(min(rms * 10, 1.0))

            self.recording_started.emit()
            self.progress.emit("🔴 Kayıt ediliyor… (Durdur'a bas)")

            with sd.InputStream(
                samplerate = self.SAMPLE_RATE,
                channels   = self.CHANNELS,
                dtype      = self.DTYPE,
                blocksize  = CHUNK,
                callback   = _callback,
            ):
                elapsed = 0.0
                while not self._stop_flag and elapsed < self.max_sec:
                    self.msleep(100)
                    elapsed += 0.1

            self.progress.emit("⏹ Kayıt tamamlandı, işleniyor…")
            self.level.emit(0.0)

            if not self._chunks:
                self.error.emit("Ses kaydedilemedi.")
                return

            audio = np.concatenate(self._chunks)

            # ── Geçici WAV ────────────────────────────────────────
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = Path(tmp.name)
            tmp.close()

            import soundfile as sf
            sf.write(str(tmp_path), audio, self.SAMPLE_RATE)

            # ── Gürültü temizleme ─────────────────────────────────
            transcribe_path = tmp_path
            if self.denoise:
                self.progress.emit("🔇 Gürültü temizleniyor…")
                try:
                    import noisereduce as nr
                    reduced = nr.reduce_noise(
                        y=audio, sr=self.SAMPLE_RATE, stationary=False
                    )
                    sf.write(str(tmp_path), reduced, self.SAMPLE_RATE)
                    self.progress.emit("✅ Gürültü temizlendi.")
                except ImportError:
                    self.progress.emit("⚠️ noisereduce kurulu değil, atlanıyor.")

            # ── Transkripsiyon ────────────────────────────────────
            from faster_whisper import WhisperModel
            import torch

            device       = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            device_label = "CUDA" if device == "cuda" else "CPU"

            self.progress.emit(
                f"🔄 Model yükleniyor → {self.model_size} | {device_label}"
            )

            model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
            )

            self.progress.emit("📝 Transkribe ediliyor…")

            segments, info = model.transcribe(
                str(transcribe_path),
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )

            parts: list[str] = []
            for seg in segments:
                text = seg.text.strip()
                if text:
                    parts.append(text)
                    self.segment.emit(seg.start, seg.end, text)

            detected   = info.language.upper() if info.language else "?"
            confidence = f"{info.language_probability:.0%}"
            self.progress.emit(
                f"✅ Tamamlandı | Dil: {detected} ({confidence}) "
                f"| {len(parts)} segment"
            )
            self.finished.emit(" ".join(parts))

        except Exception as exc:
            self.error.emit(f"Mikrofon hatası: {exc}")

        finally:
            # Geçici dosyayı temizle
            try:
                if 'tmp_path' in dir() and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass