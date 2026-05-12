"""
Toplu transkripsiyon motoru.
Dosya listesini sırayla işler; her adımda UI'a sinyal gönderir.
Her dosya için ayrı bir WhisperModel örneği oluşturmak yerine
modeli bir kez yükler ve yeniden kullanır — bellek ve zaman tasarrufu.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.file_manager import SegmentList


class BatchWorker(QThread):
    """
    Sinyaller:
        started(int, Path)                        → sıra numarası, dosya
        progress(int, Path, str)                  → sıra no, dosya, mesaj
        segment(int, float, float, str)           → sıra no, start, end, text
        file_done(int, Path, str, SegmentList)    → sıra no, dosya, tam metin, segmentler
        file_error(int, Path, str)                → sıra no, dosya, hata mesajı
        all_done()                                → tüm kuyruk tamamlandı
    """

    started_file = pyqtSignal(int, Path)
    progress     = pyqtSignal(int, Path, str)
    segment      = pyqtSignal(int, float, float, str)
    file_done    = pyqtSignal(int, Path, str, list)   # list = SegmentList
    file_error   = pyqtSignal(int, Path, str)
    all_done     = pyqtSignal()

    def __init__(
        self,
        files: list[Path],
        model_size: str = "large-v3-turbo",
    ) -> None:
        super().__init__()
        self.files       = files
        self.model_size  = model_size
        self._is_cancelled = False

    # ── Ana döngü ────────────────────────────────────────────────────

    def run(self) -> None:
        try:
            from faster_whisper import WhisperModel  # noqa: PLC0415
            import torch                              # noqa: PLC0415

            device       = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            device_label = "CUDA (GPU)" if device == "cuda" else "CPU"

            # Modeli bir kez yükle — tüm dosyalar için yeniden kullan
            self.progress.emit(
                0, Path(""),
                f"🔄 Model yükleniyor → {self.model_size}  |  {device_label}"
            )

            model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=compute_type,
            )

            for idx, file_path in enumerate(self.files):
                if self._is_cancelled:
                    break

                self.started_file.emit(idx, file_path)
                self.progress.emit(idx, file_path, f"🎙️ İşleniyor…")

                try:
                    segments_gen, info = model.transcribe(
                        str(file_path),
                        beam_size=5,
                        language=None,
                        vad_filter=True,
                        vad_parameters={"min_silence_duration_ms": 500},
                        word_timestamps=False,
                    )

                    parts: list[str]    = []
                    seg_list: SegmentList = []

                    for seg in segments_gen:
                        if self._is_cancelled:
                            break
                        text = seg.text.strip()
                        if text:
                            parts.append(text)
                            seg_list.append((seg.start, seg.end, text))
                            self.segment.emit(idx, seg.start, seg.end, text)

                    if self._is_cancelled:
                        break

                    full_text = " ".join(parts)
                    detected  = info.language.upper() if info.language else "?"
                    conf      = f"{info.language_probability:.0%}"
                    dur       = f"{info.duration:.1f}s"

                    self.progress.emit(
                        idx, file_path,
                        f"✅ Tamamlandı  |  Dil: {detected} ({conf})  |  Süre: {dur}"
                    )
                    self.file_done.emit(idx, file_path, full_text, seg_list)

                except Exception as exc:  # noqa: BLE001
                    self.file_error.emit(idx, file_path, str(exc))

        except Exception as exc:  # noqa: BLE001
            self.progress.emit(0, Path(""), f"❌ Kritik hata: {exc}")

        finally:
            self.all_done.emit()

    def cancel(self) -> None:
        self._is_cancelled = True