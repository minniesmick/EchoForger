# core/file_manager.py
"""
EchoForge — Dosya yönetimi modülü.

Klasör yapısı:
    antigravity/
    ├── voice_files/          ← STT giriş dosyaları (Whisper)
    ├── reference_voices/     ← TTS klonlama referans sesleri
    └── output/
        ├── transcripts/      ← TXT / SRT / VTT çıktıları
        └── audio/            ← TTS WAV çıktıları

Tüm path işlemleri pathlib ile yapılır.
Windows / macOS / Linux uyumludur.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List


# ── Kök dizin (core/ klasörünün bir üstü = proje kökü) ───────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── STT klasörleri ────────────────────────────────────────────────────────────
VOICE_DIR    = PROJECT_ROOT / "voice_files"

# ── TTS klasörleri ────────────────────────────────────────────────────────────
REFERENCE_VOICES_DIR = PROJECT_ROOT / "reference_voices"

# ── Çıktı klasörleri ──────────────────────────────────────────────────────────
OUTPUT_DIR        = PROJECT_ROOT / "output"
TRANSCRIPTS_DIR   = OUTPUT_DIR / "transcripts"
AUDIO_DIR         = OUTPUT_DIR / "audio"

# ── Desteklenen uzantılar ─────────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".webm"}
REFERENCE_EXTENSIONS = {".wav"}   # Klonlama yalnızca WAV kabul eder

# Tip takma adı — segment listesi: [(start, end, text), ...]
SegmentList = list[tuple[float, float, str]]


# ── Zaman format yardımcıları ─────────────────────────────────────────────────

def _srt_time(seconds: float) -> str:
    """Saniyeyi SRT zaman formatına çevirir: HH:MM:SS,mmm"""
    h  = int(seconds) // 3600
    m  = (int(seconds) % 3600) // 60
    s  = int(seconds) % 60
    ms = round((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _vtt_time(seconds: float) -> str:
    """Saniyeyi WebVTT zaman formatına çevirir: HH:MM:SS.mmm"""
    h  = int(seconds) // 3600
    m  = (int(seconds) % 3600) // 60
    s  = int(seconds) % 60
    ms = round((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


# ══════════════════════════════════════════════════════════════════════════════
#  FileManager
# ══════════════════════════════════════════════════════════════════════════════

class FileManager:
    """
    Proje klasörlerini ve ses dosyalarını yöneten yardımcı sınıf.
    Tüm metodlar statik — örnek oluşturmaya gerek yok.
    """

    # ── Klasör yönetimi ───────────────────────────────────────────────────────

    @staticmethod
    def ensure_directories() -> None:
        """Gerekli tüm klasörleri oluşturur (zaten varsa dokunmaz)."""
        for directory in (
            VOICE_DIR,
            REFERENCE_VOICES_DIR,
            TRANSCRIPTS_DIR,
            AUDIO_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    # ── STT: voice_files/ ─────────────────────────────────────────────────────

    @staticmethod
    def get_voice_files() -> List[Path]:
        """
        voice_files/ klasöründeki tüm desteklenen ses dosyalarını döndürür.
        Büyük/küçük harf uzantı farkını gözetmez.
        """
        if not VOICE_DIR.exists():
            return []

        files: list[Path] = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(VOICE_DIR.glob(f"*{ext}"))
            files.extend(VOICE_DIR.glob(f"*{ext.upper()}"))

        return sorted(set(files), key=lambda p: p.name.lower())

    @staticmethod
    def copy_to_voice_dir(source: Path) -> Path | None:
        """
        Kaynağı voice_files/ klasörüne kopyalar.
        Döndürür: kopyalanan dosya Path'i | None (desteklenmiyorsa veya zaten varsa).
        """
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return None
        dest = VOICE_DIR / source.name
        if dest.exists():
            return None
        shutil.copy2(source, dest)
        return dest

    @staticmethod
    def get_voice_dir() -> Path:
        return VOICE_DIR

    # ── TTS: reference_voices/ ────────────────────────────────────────────────

    @staticmethod
    def get_reference_voices() -> List[Path]:
        """
        reference_voices/ klasöründeki .wav dosyalarını döndürür.
        Yalnızca WAV kabul edilir (XTTSv2 ve Fish Speech gereksinimi).
        """
        if not REFERENCE_VOICES_DIR.exists():
            return []

        files: list[Path] = []
        for ext in REFERENCE_EXTENSIONS:
            files.extend(REFERENCE_VOICES_DIR.glob(f"*{ext}"))
            files.extend(REFERENCE_VOICES_DIR.glob(f"*{ext.upper()}"))

        return sorted(set(files), key=lambda p: p.name.lower())

    @staticmethod
    def copy_to_reference_voices(source: Path) -> Path | None:
        """
        Kaynağı reference_voices/ klasörüne kopyalar.
        Yalnızca .wav dosyaları kabul edilir.
        Döndürür: kopyalanan dosya Path'i | None.
        """
        if source.suffix.lower() not in REFERENCE_EXTENSIONS:
            return None
        dest = REFERENCE_VOICES_DIR / source.name
        if dest.exists():
            return None
        shutil.copy2(source, dest)
        return dest

    @staticmethod
    def get_reference_voices_dir() -> Path:
        return REFERENCE_VOICES_DIR

    # ── Çıktı path üreticileri ────────────────────────────────────────────────

    @staticmethod
    def get_transcript_path(audio_path: Path, suffix: str = "_transcript.txt") -> Path:
        """Transkripsiyon çıktı dosyası için hazır Path döndürür."""
        return TRANSCRIPTS_DIR / f"{audio_path.stem}{suffix}"

    @staticmethod
    def get_audio_output_path(filename: str) -> Path:
        """TTS çıktı dosyası için hazır Path döndürür."""
        return AUDIO_DIR / filename

    @staticmethod
    def get_transcripts_dir() -> Path:
        return TRANSCRIPTS_DIR

    @staticmethod
    def get_audio_dir() -> Path:
        return AUDIO_DIR

    @staticmethod
    def get_output_dir() -> Path:
        """Geriye dönük uyumluluk — output/ kökünü döndürür."""
        return OUTPUT_DIR

    # ── Transkripsiyon kaydetme ───────────────────────────────────────────────

    @staticmethod
    def save_transcript(audio_path: Path, text: str) -> Path:
        """
        Transkripti düz metin olarak output/transcripts/ altına kaydeder.
        """
        output_path = TRANSCRIPTS_DIR / f"{audio_path.stem}_transcript.txt"
        output_path.write_text(text, encoding="utf-8")
        return output_path

    @staticmethod
    def save_srt(audio_path: Path, segments: SegmentList) -> Path:
        """
        Segmentleri SRT formatında output/transcripts/ altına kaydeder.

        Örnek çıktı:
            1
            00:00:01,240 --> 00:00:04,880
            Merhaba, bu bir test cümlesidir.
        """
        lines: list[str] = []
        for i, (start, end, text) in enumerate(segments, start=1):
            lines.append(str(i))
            lines.append(f"{_srt_time(start)} --> {_srt_time(end)}")
            lines.append(text)
            lines.append("")   # Boş satır — blok ayracı

        output_path = TRANSCRIPTS_DIR / f"{audio_path.stem}_transcript.srt"
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    @staticmethod
    def save_vtt(audio_path: Path, segments: SegmentList) -> Path:
        """
        Segmentleri WebVTT formatında output/transcripts/ altına kaydeder.

        Örnek çıktı:
            WEBVTT

            00:00:01.240 --> 00:00:04.880
            Merhaba, bu bir test cümlesidir.
        """
        lines: list[str] = ["WEBVTT", ""]
        for start, end, text in segments:
            lines.append(f"{_vtt_time(start)} --> {_vtt_time(end)}")
            lines.append(text)
            lines.append("")

        output_path = TRANSCRIPTS_DIR / f"{audio_path.stem}_transcript.vtt"
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path