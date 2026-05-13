# core/ollama_client.py
"""
EchoForge — Ollama API istemcisi.

Özellikler:
    - Model listesi çekme
    - Model unload (VRAM temizleme) → keep_alive: 0
    - Stream ile metin üretimi
    - QThread tabanlı worker'lar (GUI bloklamaz)
"""
from __future__ import annotations

import json
from typing import Callable

import urllib.request
import urllib.error

from PyQt6.QtCore import QThread, pyqtSignal

from core.settings_manager import SettingsManager


def _base_url() -> str:
    return SettingsManager.instance().get("ollama_url", "http://localhost:11434")


# ══════════════════════════════════════════════════════════════════════════════
#  Düşük seviye yardımcılar (senkron, worker içinde çağrılır)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_models() -> list[str]:
    """Ollama'daki kurulu model isimlerini döndürür."""
    url = f"{_base_url()}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def unload_model(model_name: str) -> None:
    """
    Modeli Ollama'dan VRAM'den kaldırır.
    keep_alive=0 → model hemen boşaltılır.
    """
    url  = f"{_base_url()}/api/generate"
    body = json.dumps({
        "model":      model_name,
        "prompt":     ".",
        "keep_alive": 0,
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass


def generate_stream(
    model_name: str,
    prompt: str,
    stream_callback: Callable[[str], None],
    stop_flag: Callable[[], bool] | None = None,
) -> str:
    """
    Ollama'dan stream ile metin üretir.
    Her token gelince stream_callback(token) çağrılır.
    Tüm metni string olarak döndürür.
    """
    url  = f"{_base_url()}/api/generate"
    body = json.dumps({
        "model":      model_name,
        "prompt":     prompt,
        "stream":     True,
        "keep_alive": 600,   # saniye cinsinden int
    }).encode()

    req = urllib.request.Request(url, data=body, method="POST",
                                  headers={"Content-Type": "application/json"})

    full_text = ""
    with urllib.request.urlopen(req, timeout=120) as resp:
        for raw_line in resp:
            if stop_flag and stop_flag():
                break
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                if token:
                    full_text += token
                    stream_callback(token)
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue

    return full_text


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Model listesi çekme
# ══════════════════════════════════════════════════════════════════════════════

class ModelFetchWorker(QThread):
    """
    Sinyaller:
        finished(list[str]): model isimleri
        error(str)
    """
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def run(self) -> None:
        try:
            models = fetch_models()
            if not models:
                self.error.emit("Model bulunamadı veya Ollama çalışmıyor.")
            else:
                self.finished.emit(models)
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Model unload + load (geçiş)
# ══════════════════════════════════════════════════════════════════════════════

class ModelSwitchWorker(QThread):
    """
    Eski modeli unload eder, yeni modeli ısıtır (boş prompt ile).

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
            if self.old_model and self.old_model != self.new_model:
                self.progress.emit(
                    f"🧹 '{self.old_model}' VRAM'den kaldırılıyor..."
                )
                unload_model(self.old_model)
                self.progress.emit("✅ VRAM temizlendi.")

            self.progress.emit(f"⚡ '{self.new_model}' yükleniyor...")
            # Kısa prompt ile modeli ön yükle (boş prompt Ollama'da 500 verebilir)
            generate_stream(self.new_model, "Merhaba.", lambda _: None)
            self.progress.emit(f"✅ '{self.new_model}' hazır.")
            self.finished.emit()

        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  Worker: Metin üretimi (stream)
# ══════════════════════════════════════════════════════════════════════════════

class GenerateWorker(QThread):
    """
    Sinyaller:
        token(str)     → her token UI'a anlık iletilir
        finished(str)  → tüm metin
        error(str)
    """
    token    = pyqtSignal(str)
    first_token  = pyqtSignal(float)
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, model: str, prompt: str) -> None:
        super().__init__()
        self.model       = model
        self.prompt      = prompt
        self._cancelled  = False

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
