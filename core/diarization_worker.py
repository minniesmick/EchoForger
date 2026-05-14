# core/diarization_worker.py
"""
EchoForge — Konuşmacı Tanıma (Speaker Diarization) Worker'ı.

Backend: pyannote.audio 3.x
Model:   pyannote/speaker-diarization-3.1 (HuggingFace)

Gereksinimler:
    pip install pyannote.audio
    HuggingFace token (Settings sekmesinden gir)
    Model erişim onayı:
        https://huggingface.co/pyannote/speaker-diarization-3.1
        https://huggingface.co/pyannote/segmentation-3.0

Çıktı formatı:
    [KONUŞMACI_1  00:00 → 00:12]  Segment metni...
    [KONUŞMACI_2  00:12 → 00:18]  Segment metni...
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.environment import Environment


class DiarizationWorker(QThread):
    """
    Ses dosyasında konuşmacıları tespit eder,
    opsiyonel olarak Whisper ile transkripsiyon da yapar.

    Sinyaller:
        progress(str)                         → durum mesajları
        speaker_segment(str, float, float, str) → (konuşmacı, start, end, metin)
        finished(str)                         → formatlanmış tam çıktı
        error(str)
    """

    progress        = pyqtSignal(str)
    speaker_segment = pyqtSignal(str, float, float, str)
    finished        = pyqtSignal(str)
    error           = pyqtSignal(str)

    def __init__(
        self,
        audio_path:   Path,
        model_size:   str  = "large-v3-turbo",
        num_speakers: int  | None = None,   # None → otomatik tespit
        min_speakers: int  | None = None,
        max_speakers: int  | None = None,
        transcribe:   bool = True,
        denoise:      bool = False,
    ) -> None:
        super().__init__()
        self.audio_path   = audio_path
        self.model_size   = model_size
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.transcribe   = transcribe
        self.denoise      = denoise
        self._cancelled   = False

    def cancel(self) -> None:
        self._cancelled = True

    # ── Ana döngü ────────────────────────────────────────────────────

    def run(self) -> None:
        tmp_path = None
        try:
            import torch

            # ── HF Token ──────────────────────────────────────────
            hf_token = Environment.instance().get_api_key("HF_TOKEN")
            if not hf_token:
                self.error.emit(
                    "HuggingFace token bulunamadı.\n"
                    "Ayarlar sekmesine HF_TOKEN ekleyin.\n"
                    "Token: https://huggingface.co/settings/tokens"
                )
                return

            # ── Gürültü temizleme ──────────────────────────────────
            process_path = self.audio_path
            if self.denoise:
                self.progress.emit("🔇 Gürültü temizleniyor…")
                from core.transcriber import _denoise
                tmp_path     = _denoise(self.audio_path)
                process_path = tmp_path
                self.progress.emit("✅ Gürültü temizlendi.")

            # ── Diarization ───────────────────────────────────────
            self.progress.emit("👥 Konuşmacılar tespit ediliyor…")

            from pyannote.audio import Pipeline  # type: ignore

            device = "cuda" if torch.cuda.is_available() else "cpu"

            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token,
            )
            pipeline.to(torch.device(device))

            diarize_kwargs: dict = {}
            if self.num_speakers:
                diarize_kwargs["num_speakers"] = self.num_speakers
            if self.min_speakers:
                diarize_kwargs["min_speakers"] = self.min_speakers
            if self.max_speakers:
                diarize_kwargs["max_speakers"] = self.max_speakers

            diarization = pipeline(str(process_path), **diarize_kwargs)

            if self._cancelled:
                return

            # Konuşmacı segmentlerini listele
            speaker_turns: list[tuple[float, float, str]] = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_turns.append((turn.start, turn.end, speaker))

            speakers_found = len({s for _, _, s in speaker_turns})
            self.progress.emit(
                f"✅ {speakers_found} konuşmacı, {len(speaker_turns)} segment bulundu."
            )

            # ── Transkripsiyon (opsiyonel) ────────────────────────
            segment_texts: dict[tuple[float, float], str] = {}

            if self.transcribe and not self._cancelled:
                self.progress.emit(
                    f"📝 Transkripsiyon başlıyor → {self.model_size}…"
                )

                from faster_whisper import WhisperModel

                compute_type = "float16" if device == "cuda" else "int8"
                wmodel = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                )

                whisper_segs, info = wmodel.transcribe(
                    str(process_path),
                    beam_size=5,
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 300},
                )

                # Whisper segmentlerini topla
                w_segments: list[tuple[float, float, str]] = []
                for seg in whisper_segs:
                    if self._cancelled:
                        break
                    w_segments.append((seg.start, seg.end, seg.text.strip()))

                # Her diarization segmentine en yakın Whisper metnini eşleştir
                for d_start, d_end, speaker in speaker_turns:
                    matched: list[str] = []
                    for w_start, w_end, w_text in w_segments:
                        # Örtüşme kontrolü
                        overlap = min(d_end, w_end) - max(d_start, w_start)
                        if overlap > 0.1 and w_text:
                            matched.append(w_text)
                    segment_texts[(d_start, d_end)] = " ".join(matched)

            if self._cancelled:
                return

            # ── Çıktıyı formatla ve sinyalle ─────────────────────
            output_lines: list[str] = []

            for d_start, d_end, speaker in speaker_turns:
                text = segment_texts.get((d_start, d_end), "")
                self.speaker_segment.emit(speaker, d_start, d_end, text)

                start_fmt = self._fmt(d_start)
                end_fmt   = self._fmt(d_end)
                line = f"[{speaker}  {start_fmt} → {end_fmt}]"
                if text:
                    line += f"  {text}"
                output_lines.append(line)

            self.progress.emit(
                f"🏁 Diarization tamamlandı  |  "
                f"{speakers_found} konuşmacı  |  {len(speaker_turns)} segment"
            )
            self.finished.emit("\n".join(output_lines))

        except Exception as exc:
            self.error.emit(f"Diarization hatası: {exc}")
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    @staticmethod
    def _fmt(seconds: float) -> str:
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"
