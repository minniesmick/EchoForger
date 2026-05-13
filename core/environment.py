# core/environment.py
"""
EchoForge — Ortam Tespiti ve Path Çözümleme.

Singleton Environment sınıfı — tüm modüller buradan sorar.
Hiçbir modül kendi başına platform/path kararı vermez.

Desteklenen ortamlar:
    LOCAL   → Windows/macOS yerel kurulum
    COLAB   → Google Colab (GPU + GDrive)

Kullanım:
    from core.environment import Environment
    env = Environment.instance()

    env.is_colab()                        # → bool
    env.resolve_path("tts_model_dir")     # → platform'a göre Path
    env.get_api_key("GEMINI_API_KEY")     # → str | None
"""
from __future__ import annotations

import os
import sys
from enum import Enum, auto
from pathlib import Path


class RuntimeEnv(Enum):
    LOCAL = auto()
    COLAB = auto()


class Environment:
    """
    Ortam tespiti ve cross-platform path çözümleme.

    Tespit sırası:
        1. --colab CLI flag
        2. COLAB_RELEASE_TAG env var (Colab otomatik set eder)
        3. /content klasörü varlığı
        4. Varsayılan: LOCAL
    """

    _inst: Environment | None = None

    def __init__(self) -> None:
        self._runtime = self._detect()
        self._drive_root: Path | None = None

        if self._runtime == RuntimeEnv.COLAB:
            self._drive_root = self._find_drive_root()

    @classmethod
    def instance(cls) -> Environment:
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    # ── Tespit ───────────────────────────────────────────────────────

    @staticmethod
    def _detect() -> RuntimeEnv:
        if "--colab" in sys.argv:
            return RuntimeEnv.COLAB
        if os.environ.get("COLAB_RELEASE_TAG"):
            return RuntimeEnv.COLAB
        if Path("/content").exists():
            return RuntimeEnv.COLAB
        return RuntimeEnv.LOCAL

    @staticmethod
    def _find_drive_root() -> Path | None:
        """GDrive mount noktasını bulur."""
        candidates = [
            Path("/content/drive/MyDrive"),
            Path("/content/drive/My Drive"),
        ]
        for p in candidates:
            if p.exists():
                return p
        return Path("/content/drive/MyDrive")  # varsayılan, henüz mount edilmemiş olabilir

    # ── Sorgular ─────────────────────────────────────────────────────

    def is_colab(self) -> bool:
        return self._runtime == RuntimeEnv.COLAB

    def is_local(self) -> bool:
        return self._runtime == RuntimeEnv.LOCAL

    def runtime(self) -> RuntimeEnv:
        return self._runtime

    def runtime_label(self) -> str:
        return "Google Colab" if self.is_colab() else "Yerel Makine"

    @property
    def drive_root(self) -> Path | None:
        return self._drive_root

    # ── Path çözümleme ────────────────────────────────────────────────

    def resolve_path(self, key: str) -> Path:
        """
        settings_manager'dan gelen path key'ini ortama göre çözer.

        LOCAL : settings.json'daki değeri kullanır
        COLAB : GDrive altındaki karşılığını döner

        Colab path eşleme:
            tts_model_dir  → GDrive/EchoForge/Ses_Modelleri
            hf_cache_dir   → GDrive/EchoForge/hf_cache
            output_dir     → GDrive/EchoForge/output
        """
        from core.settings_manager import SettingsManager
        raw = SettingsManager.instance().get(key, "")

        if self.is_local():
            return Path(raw) if raw else self._local_fallback(key)

        # Colab: GDrive altına yönlendir
        return self._colab_path(key)

    def _local_fallback(self, key: str) -> Path:
        """settings boşsa platform'a göre makul bir varsayılan döner."""
        home = Path.home()
        defaults = {
            "tts_model_dir": home / "ses_modelleri",
            "hf_cache_dir":  home / ".cache" / "huggingface",
            "output_dir":    Path(__file__).resolve().parent.parent / "output",
        }
        return defaults.get(key, Path.home())

    def _colab_path(self, key: str) -> Path:
        base = self._drive_root or Path("/content/drive/MyDrive")
        echo = base / "EchoForge"
        mapping = {
            "tts_model_dir": echo / "Ses_Modelleri",
            "hf_cache_dir":  echo / "hf_cache",
            "output_dir":    echo / "output",
        }
        return mapping.get(key, echo)

    def project_root(self) -> Path:
        """Proje kökü — LOCAL: repo dizini, COLAB: /content/EchoForge"""
        if self.is_colab():
            return Path("/content/EchoForge")
        return Path(__file__).resolve().parent.parent

    # ── API Key çözümleme ─────────────────────────────────────────────

    def get_api_key(self, key_name: str) -> str | None:
        """
        API anahtarını şu sırayla arar:
            1. Google Colab Secrets (userdata) — sadece Colab'da
            2. Ortam değişkeni (os.getenv)
            3. settings.json

        Hiçbirinde yoksa None döner.
        """
        # 1 — Colab Secrets
        if self.is_colab():
            try:
                from google.colab import userdata  # type: ignore
                val = userdata.get(key_name)
                if val:
                    return val
            except Exception:
                pass

        # 2 — Ortam değişkeni
        val = os.environ.get(key_name)
        if val:
            return val

        # 3 — settings.json
        from core.settings_manager import SettingsManager
        return SettingsManager.instance().get(key_name.lower(), None)

    # ── Colab kurulum yardımcıları ────────────────────────────────────

    def ensure_drive_mounted(self) -> bool:
        """
        GDrive bağlı değilse mount eder.
        Sadece Colab'da çağrılmalı.
        """
        if not self.is_colab():
            return True
        if self._drive_root and self._drive_root.exists():
            return True
        try:
            from google.colab import drive  # type: ignore
            drive.mount("/content/drive")
            self._drive_root = self._find_drive_root()
            return True
        except Exception:
            return False

    def ensure_colab_dirs(self) -> None:
        """Colab'da gerekli GDrive klasörlerini oluşturur."""
        if not self.is_colab():
            return
        for key in ("tts_model_dir", "hf_cache_dir", "output_dir"):
            self._colab_path(key).mkdir(parents=True, exist_ok=True)
