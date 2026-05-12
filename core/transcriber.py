"""
Transkripsiyon motoru — faster-whisper backend.

Whisper large-v3-turbo modelini kullanır.
RTX 3060 Ti üzerinde float16 + CUDA ile çalışır;
CUDA bulunamazsa otomatik olarak CPU'ya (int8) döner.

Yenilik:
  - segment(float, float, str) sinyali → her segment gelince UI'a iletilir
  - finished(str)              → tüm metin birleşik olarak iletilir (kaydetme için)
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal


def _detect_device() -> tuple[str, str]:
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"


class TranscriptionWorker(QThread):
    """
    faster-whisper transkripsiyon işlemini arka planda çalıştıran thread.

    Sinyaller:
        progress(str)          → Durum mesajı
        segment(float,float,str) → (başlangıç_sn, bitiş_sn, metin) her segment için
        finished(str)          → Tüm metin birleşik (kaydetme / kopyalama için)
        error(str)             → Hata mesajı
    """

    progress = pyqtSignal(str)
    segment  = pyqtSignal(float, float, str)   # start, end, text
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, audio_path: Path, model_size: str = "large-v3-turbo"):
        super().__init__()
        self.audio_path  = audio_path
        self.model_size  = model_size
        self._is_cancelled = False

    # ── Ana çalışma döngüsü ─────────────────────────────────────────

    def run(self) -> None:
        try:
            from faster_whisper import WhisperModel  # noqa: PLC0415

            device, compute_type = _detect_device()
            device_label = "CUDA (GPU)" if device == "cuda" else "CPU"

            self.progress.emit(
                f"🔄 Model yükleniyor → {self.model_size}  |  {device_label}"
            )

            model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
            )

            if self._is_cancelled:
                return

            self.progress.emit(
                f"🎙️ '{self.audio_path.name}' transkribe ediliyor…"
            )

            segments, info = model.transcribe(
                str(self.audio_path),
                beam_size=5,
                language=None,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
                word_timestamps=False,   # Segment bazlı timestamp yeterli
            )

            parts: list[str] = []

            for seg in segments:
                if self._is_cancelled:
                    return

                text = seg.text.strip()
                if text:
                    parts.append(text)
                    # Her segment geldiğinde UI'a hemen ilet
                    self.segment.emit(seg.start, seg.end, text)

            detected   = info.language.upper() if info.language else "?"
            confidence = f"{info.language_probability:.0%}"

            self.progress.emit(
                f"✅ Tamamlandı  |  Dil: {detected} ({confidence})  "
                f"|  Süre: {info.duration:.1f}s"
            )

            # Birleşik metni kaydetme/kopyalama için gönder
            self.finished.emit(" ".join(parts))

        except FileNotFoundError:
            self.error.emit(f"Dosya bulunamadı: {self.audio_path}")
        except Exception as exc:  # noqa: BLE001
            self.error.emit(f"Beklenmeyen hata: {exc}")

    # ── İptal ───────────────────────────────────────────────────────

    def cancel(self) -> None:
        self._is_cancelled = True