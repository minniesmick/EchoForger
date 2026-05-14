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

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.settings_manager import SettingsManager
_hf = SettingsManager.instance().get("hf_cache_dir")
os.environ.setdefault("HF_HOME",      _hf)
os.environ.setdefault("HF_HUB_CACHE", str(Path(_hf) / "hub"))

def _fix_cuda_paths():
    """
    Windows'ta ctranslate2'nin (faster-whisper) CUDA 12 DLL'lerini 
    (cublas64_12.dll vb.) bulabilmesi için PATH ayarı yapar.
    """
    if sys.platform != "win32":
        return

    # Sanal ortam ve sistem site-packages yollarını kontrol et
    import site
    paths_to_check = [Path(sys.prefix) / "Lib" / "site-packages"]
    try:
        for p in site.getsitepackages():
            paths_to_check.append(Path(p))
    except (AttributeError, Exception):
        pass

    nvidia_bin_dirs = [
        "nvidia/cublas/bin",
        "nvidia/cudnn/bin",
        "nvidia/cuda_nvrtc/bin",
        "nvidia/cuda_runtime/bin",
        "nvidia/cudnn/lib",
    ]

    for base in paths_to_check:
        for nbin in nvidia_bin_dirs:
            p = base / nbin
            if p.exists():
                path_str = str(p.absolute())
                if path_str not in os.environ["PATH"]:
                    os.environ["PATH"] = path_str + os.pathsep + os.environ["PATH"]
                
                # Python 3.8+ için DLL directory olarak da ekle (daha güvenli)
                if hasattr(os, "add_dll_directory"):
                    try:
                        os.add_dll_directory(path_str)
                    except Exception:
                        pass

def _denoise(audio_path: Path) -> Path:
    """
    Ses dosyasını gürültüden arındırır, geçici dosya olarak kaydeder.
    Orijinal dosyaya dokunmaz.
    Döner: temizlenmiş geçici dosya Path'i
    """
    import tempfile
    import numpy as np
    import soundfile as sf
    import noisereduce as nr

    data, rate = sf.read(str(audio_path), always_2d=True, dtype="float32")
    mono       = data.mean(axis=1)
    reduced    = nr.reduce_noise(y=mono, sr=rate, stationary=False)

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, reduced, rate)
    return Path(tmp.name)
def _detect_device() -> tuple[str, str]:
    """Donanımı algılar ve uygun compute_type döner."""
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

    def __init__(self, audio_path: Path, model_size: str = "large-v3-turbo",
                 denoise: bool = False):
        super().__init__()
        self.audio_path    = audio_path
        self.model_size    = model_size
        self.denoise       = denoise
        self._is_cancelled = False
        self._tmp_path: Path | None = None

    # ── Ana çalışma döngüsü ─────────────────────────────────────────

    def run(self) -> None:
        try:
            # DLL yollarını düzelt (Windows/CUDA 12 özelinde)
            _fix_cuda_paths()
            
            from faster_whisper import WhisperModel  # noqa: PLC0415
            
            device, compute_type = _detect_device()
            device_label = "CUDA (GPU)" if device == "cuda" else "CPU"

            self.progress.emit(
                f"🔄 Model yükleniyor → {self.model_size}  |  {device_label}"
            )

            try:
                model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                )
            except Exception as e:
                # CUDA hatası alınırsa (örn. DLL eksikliği), CPU'ya düş
                if device == "cuda":
                    self.progress.emit(f"⚠️ CUDA hatası: {e}. CPU'ya geçiliyor...")
                    model = WhisperModel(
                        self.model_size,
                        device="cpu",
                        compute_type="int8",
                    )
                else:
                    raise e

            if self._is_cancelled:
                return

            # Gürültü temizleme (opsiyonel)
            transcribe_path = self.audio_path
            if self.denoise:
                self.progress.emit("🔇 Gürültü temizleniyor…")
                self._tmp_path  = _denoise(self.audio_path)
                transcribe_path = self._tmp_path
                self.progress.emit("✅ Gürültü temizlendi.")

            self.progress.emit(
                f"🎙️ '{self.audio_path.name}' transkribe ediliyor…"
            )

            segments, info = model.transcribe(
                str(transcribe_path),
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
        finally:
            # Geçici dosyayı temizle
            if self._tmp_path and self._tmp_path.exists():
                self._tmp_path.unlink(missing_ok=True)

    # ── İptal ───────────────────────────────────────────────────────

    def cancel(self) -> None:
        self._is_cancelled = True