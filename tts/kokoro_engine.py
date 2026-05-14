# tts/kokoro_engine.py
"""
EchoForge — Kokoro TTS Engine.

Backend: kokoro-onnx (MIT lisanslı, CPU/GPU)
Özellik: XTTSv2'den ~10x hızlı, İngilizce'de üstün kalite
Sınır:   Türkçe desteği zayıf — İngilizce içerik için kullanın

Kurulum:
    pip install kokoro-onnx
    pip install kokoro-onnx[voices]   # ses dosyaları için

Model dosyaları ilk çalıştırmada otomatik indirilir (~300MB).
"""
from __future__ import annotations

import gc
from pathlib import Path
from typing import Callable

from tts.tts_engine import BaseTTSEngine


# Kokoro desteklediği diller
KOKORO_LANGUAGES: dict[str, str] = {
    "İngilizce (ABD)": "en-us",
    "İngilizce (UK)":  "en-gb",
    "Fransızca":        "fr-fr",
    "Japonca":          "ja",
    "Korece":           "ko",
    "Çince":            "cmn",
}

# Kokoro sesleri — dile göre gruplandırılmış
KOKORO_VOICES: dict[str, list[str]] = {
    "en-us": [
        "af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky",
        "am_adam",  "am_michael",
    ],
    "en-gb": [
        "bf_emma", "bf_isabella",
        "bm_george", "bm_lewis",
    ],
    "fr-fr": ["ff_siwis"],
    "ja":    ["jf_alpha", "jf_gongitsune", "jm_kumo"],
    "ko":    ["kf_alpha", "km_omega"],
    "cmn":   ["zf_xiaobei", "zm_yunjian"],
}

MODEL_KOKORO = "kokoro"


class KokoroEngine(BaseTTSEngine):
    """
    Kokoro TTS — ONNX tabanlı, hızlı lokal çıkarım.

    XTTSv2 ile farkı:
        + Çok daha hızlı (CPU'da bile kullanılabilir)
        + Küçük model boyutu (~300MB)
        - Türkçe yok
        - Ses klonlama yok (ön tanımlı sesler)
    """

    def __init__(self) -> None:
        super().__init__()
        self._pipeline = None

    # ── Kapasite ─────────────────────────────────────────────────────

    @property
    def supports_default_speakers(self) -> bool:
        return True

    @property
    def supports_voice_cloning(self) -> bool:
        return False

    @property
    def default_speakers(self) -> list[str]:
        # Tüm dillerdeki sesleri düz liste olarak döndür
        all_voices: list[str] = []
        for voices in KOKORO_VOICES.values():
            all_voices.extend(voices)
        return all_voices

    def voices_for_lang(self, lang_code: str) -> list[str]:
        """Belirli dil kodu için ses listesi."""
        return KOKORO_VOICES.get(lang_code, KOKORO_VOICES["en-us"])

    # ── Model Yükleme ─────────────────────────────────────────────────

    def load_model(self, progress_callback: Callable | None = None) -> None:
        if progress_callback:
            progress_callback("Kokoro — model yükleniyor…")

        try:
            from kokoro_onnx import Kokoro  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "kokoro-onnx kurulu değil.\n"
                "Kurulum: pip install kokoro-onnx kokoro-onnx[voices]"
            ) from exc

        # Model ilk çalıştırmada otomatik indirilir
        self._pipeline = Kokoro()
        self.is_loaded = True

        if progress_callback:
            progress_callback("Kokoro başarıyla yüklendi! ✓")

    # ── Model Kaldırma ────────────────────────────────────────────────

    def unload_model(self, progress_callback: Callable | None = None) -> None:
        if progress_callback:
            progress_callback("Kokoro kaldırılıyor…")
        self._pipeline = None
        super().unload_model(progress_callback)

    # ── Ses Üretimi ───────────────────────────────────────────────────

    def generate(
        self,
        text:              str,
        output_path:       str | Path,
        language:          str = "en-us",
        speaker_name:      str | None = None,
        speaker_wav:       str | Path | None = None,
        progress_callback: Callable | None = None,
    ) -> Path:
        if not self.is_loaded or self._pipeline is None:
            raise RuntimeError("Model yüklenmedi. Önce load_model() çağrın.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Ses seçimi — belirtilmezse dile uygun ilk ses
        voice = speaker_name
        if not voice:
            voice = self.voices_for_lang(language)[0]

        if progress_callback:
            progress_callback(f"Kokoro üretiyor (Ses: {voice}, Dil: {language})…")

        samples, sample_rate = self._pipeline.create(
            text=text,
            voice=voice,
            speed=1.0,
            lang=language,
        )

        import soundfile as sf
        sf.write(str(output_path), samples, sample_rate)

        if progress_callback:
            progress_callback(f"Kaydedildi: {output_path.name} ✓")

        return output_path
