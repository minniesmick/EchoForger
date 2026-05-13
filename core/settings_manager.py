# core/settings_manager.py
"""
EchoForge — Kalıcı ayarlar yöneticisi.
Ayarları proje kökündeki settings.json dosyasına yazar/okur.
Singleton pattern — her yerden SettingsManager.instance() ile erişilir.
"""
from __future__ import annotations

import json
from pathlib import Path

# Proje kökü (core/ klasörünün bir üstü)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = _PROJECT_ROOT / "settings.json"

DEFAULTS: dict = {
    # ── Whisper / STT ────────────────────────────────────────────────
    "whisper_model":    "large-v3-turbo",
    "hf_cache_dir":  str(Path.home() / ".cache" / "huggingface"),


    # ── XTTS / TTS ───────────────────────────────────────────────────
    "tts_model_dir": str(Path.home() / "ses_modelleri"),
    "chunk_threshold":  250,
    "silence_ms":       400,

    # ── Genel ────────────────────────────────────────────────────────
    "output_dir":       "",    # boşsa FileManager varsayılanı kullanılır
    "last_mode":        "stt", # welcome screen son seçim
    "ollama_url":  "http://localhost:11434",
}


class SettingsManager:
    """
    Uygulama ayarlarını okur/yazar.

    Kullanım:
        sm = SettingsManager.instance()
        sm.get("chunk_threshold")       # → 250
        sm.set("chunk_threshold", 300)  # → kaydeder
    """

    _inst: SettingsManager | None = None

    def __init__(self) -> None:
        self._data: dict = {}
        self._load()

    @classmethod
    def instance(cls) -> SettingsManager:
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    # ── Okuma / Yazma ─────────────────────────────────────────────────

    def get(self, key: str, fallback=None):
        return self._data.get(key, DEFAULTS.get(key, fallback))

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self._save()

    def set_many(self, updates: dict) -> None:
        self._data.update(updates)
        self._save()

    def reset(self) -> None:
        self._data = dict(DEFAULTS)
        self._save()

    # ── Dosya işlemleri ───────────────────────────────────────────────

    def _load(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                self._data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                self._data = dict(DEFAULTS)
        else:
            self._data = dict(DEFAULTS)
            self._save()

    def _save(self) -> None:
        SETTINGS_FILE.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
