# tts/workers.py
"""
EchoForge — QThread tabanlı TTS Worker sınıfları.
Tüm BaseTTSEngine alt sınıflarıyla (XTTSEngine, HumeTADAEngine)
uyumlu şekilde çalışır.

Sınıflar:
    ModelLoaderWorker    — engine.load_model()   arka planda çalıştırır.
    ModelUnloaderWorker  — engine.unload_model()  çalıştırır.
    TTSWorker            — Kısa metinler için tek parça üretim.
    ChunkedTTSWorker     — Uzun metinler için bölme + birleştirme.

Değişiklik (Voice Forge → EchoForge):
    - from tts_engine      → from tts.tts_engine
    - from text_preprocessor → from tts.text_preprocessor
"""

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from tts.tts_engine import BaseTTSEngine   # ← güncellendi


# ══════════════════════════════════════════════════════════════════════════════
#  ModelLoaderWorker
# ══════════════════════════════════════════════════════════════════════════════

class ModelLoaderWorker(QThread):
    """
    engine.load_model() işlemini arka planda çalıştırır.
    GUI thread'ini bloklamaz.

    Sinyaller:
        progress (str):  Yükleme aşamasındaki durum mesajları.
        finished:        Model başarıyla yüklendiğinde yayınlanır.
        error (str):     Hata mesajını iletir.
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error    = pyqtSignal(str)

    def __init__(self, engine: BaseTTSEngine) -> None:
        super().__init__()
        self.engine = engine

    def run(self) -> None:
        try:
            self.engine.load_model(progress_callback=self.progress.emit)
            self.finished.emit()
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  ModelUnloaderWorker
# ══════════════════════════════════════════════════════════════════════════════

class ModelUnloaderWorker(QThread):
    """
    engine.unload_model() işlemini arka planda çalıştırır.

    Model geçişlerinde eski motoru GPU'dan temizlemek için kullanılır.
    RTX 3060 Ti'nin 8 GB VRAM'ini verimli kullanmak için model geçişlerinde
    bu worker çalıştırılmalı, ardından yeni model yüklenmelidir.

    Sinyaller:
        progress (str):  VRAM temizleme mesajları.
        finished:        Temizleme tamamlandığında yayınlanır.
        error (str):     Hata mesajı.
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error    = pyqtSignal(str)

    def __init__(self, engine: BaseTTSEngine) -> None:
        super().__init__()
        self.engine = engine

    def run(self) -> None:
        try:
            self.engine.unload_model(progress_callback=self.progress.emit)
            self.finished.emit()
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  TTSWorker — Tek parça üretim
# ══════════════════════════════════════════════════════════════════════════════

class TTSWorker(QThread):
    """
    Kısa metinler için engine.generate() işlemini arka planda çalıştırır.

    Kullanım:
        Metin CHUNK_THRESHOLD (varsayılan 250) karakterin altındaysa bu
        worker kullanılır. Uzun metinler için ChunkedTTSWorker tercih edin.

    Sinyaller:
        progress (str):   Üretim aşaması mesajları.
        finished (str):   Başarıyla oluşturulan dosyanın tam yolu.
        error (str):      Hata mesajı.
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal(str)   # çıktı dosya yolu
    error    = pyqtSignal(str)

    def __init__(
        self,
        engine: BaseTTSEngine,
        text: str,
        output_path: Path,
        language: str,
        speaker_name: str | None = None,
        speaker_wav: Path | None = None,
    ) -> None:
        super().__init__()
        self.engine       = engine
        self.text         = text
        self.output_path  = output_path
        self.language     = language
        self.speaker_name = speaker_name
        self.speaker_wav  = speaker_wav

    def run(self) -> None:
        try:
            result_path = self.engine.generate(
                text=self.text,
                output_path=self.output_path,
                language=self.language,
                speaker_name=self.speaker_name,
                speaker_wav=self.speaker_wav,
                progress_callback=self.progress.emit,
            )
            self.finished.emit(str(result_path))
        except Exception as exc:
            self.error.emit(str(exc))


# ══════════════════════════════════════════════════════════════════════════════
#  ChunkedTTSWorker — Uzun metin bölme + birleştirme
# ══════════════════════════════════════════════════════════════════════════════

class ChunkedTTSWorker(QThread):
    """
    Uzun metinleri TextPreprocessor ile parçalara böler, her parçayı ayrı
    üretir ve pydub ile birleştirir.

    İş Akışı:
        1. TextPreprocessor.split()         → metin parçalara bölünür
        2. engine.generate()                → her parça için ayrı .wav üretilir
        3. TextPreprocessor.merge_audio_files() → parçalar birleştirilir
        4. Geçici parça dosyaları silinir

    Sinyaller:
        progress (str):        İlerleme mesajları.
        chunk_done (int, int): (tamamlanan_parça_no, toplam_parça).
        finished (str):        Birleştirilmiş nihai dosyanın tam yolu.
        error (str):           Hata mesajı.
    """

    progress   = pyqtSignal(str)
    chunk_done = pyqtSignal(int, int)   # (done, total)
    finished   = pyqtSignal(str)
    error      = pyqtSignal(str)

    def __init__(
        self,
        engine: BaseTTSEngine,
        text: str,
        output_path: Path,
        language: str,
        speaker_name: str | None = None,
        speaker_wav: Path | None = None,
        max_chars: int = 250,
        silence_ms: int = 400,
    ) -> None:
        super().__init__()
        self.engine       = engine
        self.text         = text
        self.output_path  = output_path
        self.language     = language
        self.speaker_name = speaker_name
        self.speaker_wav  = speaker_wav
        self.max_chars    = max_chars
        self.silence_ms   = silence_ms

    def run(self) -> None:
        from tts.text_preprocessor import TextPreprocessor   # ← güncellendi

        preprocessor = TextPreprocessor(
            max_chars=self.max_chars,
            silence_ms=self.silence_ms,
        )

        tmp_dir = self.output_path.parent / "_chunks_tmp"

        try:
            # 1 — Metni böl
            chunks = preprocessor.split(self.text)
            if not chunks:
                self.error.emit("Metin boş; üretilecek içerik yok.")
                return

            total = len(chunks)
            self.progress.emit(
                f"Metin {total} parçaya bölündü "
                f"(maks. {self.max_chars} karakter/parça)."
            )

            tmp_dir.mkdir(parents=True, exist_ok=True)
            chunk_paths: list[Path] = []

            # 2 — Her parçayı üret
            for i, chunk_text in enumerate(chunks, start=1):
                self.progress.emit(f"Parça {i}/{total} üretiliyor...")
                chunk_path = tmp_dir / f"chunk_{i:04d}.wav"

                self.engine.generate(
                    text=chunk_text,
                    output_path=chunk_path,
                    language=self.language,
                    speaker_name=self.speaker_name,
                    speaker_wav=self.speaker_wav,
                    progress_callback=self.progress.emit,
                )

                chunk_paths.append(chunk_path)
                self.chunk_done.emit(i, total)

            # 3 — Birleştir
            final_path = preprocessor.merge_audio_files(
                chunk_paths=chunk_paths,
                output_path=self.output_path,
                progress_callback=self.progress.emit,
            )

            # 4 — Temizle
            preprocessor.cleanup_chunks(chunk_paths)
            try:
                tmp_dir.rmdir()
            except OSError:
                pass

            self.finished.emit(str(final_path))

        except Exception as exc:
            try:
                for p in tmp_dir.glob("chunk_*.wav"):
                    p.unlink(missing_ok=True)
                tmp_dir.rmdir()
            except OSError:
                pass
            self.error.emit(str(exc))