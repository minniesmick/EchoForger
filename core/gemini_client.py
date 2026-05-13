# core/gemini_client.py
"""
EchoForge — Google Gemini API istemcisi.

ollama_client.py ile aynı worker mimarisini kullanır.
TTT paneli her iki motoru da aynı arayüzle kullanır.

Kurulum:
    pip install google-generativeai

API Key:
    Colab  → Colab Secrets'a GEMINI_API_KEY ekle
    Lokal  → set GEMINI_API_KEY=... (PowerShell/bash)
             veya settings.json → "gemini_api_key": "..."
             veya Ayarlar sekmesinden gir
"""
from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from core.environment import Environment

# Desteklenen Gemini modelleri — ileride güncellenebilir
GEMINI_MODELS: list[str] = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


def _get_client():
    """Gemini istemcisini API anahtarıyla yapılandırır."""
    import google.generativeai as genai  # type: ignore

    api_key = Environment.instance().get_api_key("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY bulunamadı.\n"
            "Lokal: ortam değişkeni veya Ayarlar sekmesi\n"
            "Colab: Secrets paneline GEMINI_API_KEY ekle"
        )
    genai.configure(api_key=api_key)
    return genai


def generate_stream(
    model_name: str,
    prompt: str,
    stream_callback,
    stop_flag=None,
) -> str:
    """Gemini'den stream ile yanıt alır. ollama_client.generate_stream ile aynı imza."""
    genai = _get_client()
    model = genai.GenerativeModel(model_name)

    full_text = ""
    response  = model.generate_content(prompt, stream=True)

    for chunk in response:
        if stop_flag and stop_flag():
            break
        token = chunk.text or ""
        if token:
            full_text += token
            stream_callback(token)

    return full_text


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Model listesi
# ══════════════════════════════════════════════════════════════════════════════

class ModelFetchWorker(QThread):
    """
    Gemini model listesini döner (sabit liste, API key doğrulaması yapar).

    Sinyaller:
        finished(list[str])
        error(str)
    """
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def run(self) -> None:
        try:
            # API key kontrolü
            _get_client()
            self.finished.emit(GEMINI_MODELS)
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Model geçişi (Gemini stateless — sadece bildirim)
# ══════════════════════════════════════════════════════════════════════════════

class ModelSwitchWorker(QThread):
    """
    Gemini bulut tabanlı olduğu için VRAM yönetimi yok.
    Sadece API key doğrular ve UI'a bildirir.

    Sinyaller:
        progress(str)
        finished()
        error(str)
    """
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error    = pyqtSignal(str)

    def __init__(self, old_model: str | None, new_model: str) -> None:
        super().__init__()
        self.old_model = old_model
        self.new_model = new_model

    def run(self) -> None:
        try:
            self.progress.emit("🔑 Gemini API anahtarı doğrulanıyor...")
            _get_client()
            self.progress.emit(f"✅ '{self.new_model}' hazır. (Bulut — VRAM kullanmaz)")
            self.finished.emit()
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Metin üretimi
# ══════════════════════════════════════════════════════════════════════════════

class GenerateWorker(QThread):
    """
    ollama_client.GenerateWorker ile birebir aynı sinyal arayüzü.
    ttt_panel.py her iki worker'ı ayırt etmeden kullanır.

    Sinyaller:
        token(str)
        first_token(float)
        finished(str)
        error(str)
    """
    token       = pyqtSignal(str)
    first_token = pyqtSignal(float)
    finished    = pyqtSignal(str)
    error       = pyqtSignal(str)

    def __init__(self, model: str, prompt: str) -> None:
        super().__init__()
        self.model      = model
        self.prompt     = prompt
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        import time
        try:
            t_start     = time.perf_counter()
            first_fired = False

            def on_token(token: str) -> None:
                nonlocal first_fired
                if not first_fired:
                    self.first_token.emit(time.perf_counter() - t_start)
                    first_fired = True
                self.token.emit(token)

            result = generate_stream(
                model_name      = self.model,
                prompt          = self.prompt,
                stream_callback = on_token,
                stop_flag       = lambda: self._cancelled,
            )
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
