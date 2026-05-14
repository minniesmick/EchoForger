# ui/transcription_panel.py
"""
EchoForge — Transkripsiyon Paneli.
Model seçimi, transkripsiyon kontrolü, waveform ve sonuç gösterimi.

Değişiklikler (Adım 5):
  - text_sent_to_tts(str) sinyali → "→ TTS'e Gönder" butonu pipeline köprüsü
  - pipeline_btn: transkripsiyon tamamlanınca aktif olur, metni TTS paneline iletir
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel,
    QComboBox, QProgressBar, QMenu,
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal

from core.transcriber import TranscriptionWorker
from core.file_manager import FileManager, SegmentList
from ui.waveform_widget import WaveformWidget


def _fmt_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


class TranscriptionPanel(QWidget):
    """Transkripsiyon çıktısını ve kontrolleri barındıran sağ panel."""

    # ── Sinyaller ────────────────────────────────────────────────────
    text_sent_to_tts = pyqtSignal(str)   # Pipeline köprüsü → TTSPanel.receive_text

    MODELS = [
        "tiny",
        "base",
        "small",
        "medium",
        "large-v2",
        "large-v3",
        "large-v3-turbo",
    ]

    COLOR_TIMESTAMP = "#555555"
    COLOR_TEXT      = "#F0F0F0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file: Path | None          = None
        self._worker: TranscriptionWorker | None = None
        self._full_text: str                     = ""
        self._segments: SegmentList              = []   # [(start, end, text), ...]
        self._sts_mode: bool                     = False

        self._setup_ui()

    # ── Arayüz kurulumu ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ── Başlık satırı ──
        header = QHBoxLayout()

        title = QLabel("TRANSKRİPSİYON")
        title.setObjectName("section_label")
        header.addWidget(title)
        header.addStretch()

        model_lbl = QLabel("Model:")
        model_lbl.setObjectName("status_label")
        header.addWidget(model_lbl)

        self.model_combo = QComboBox()
        self.model_combo.addItems(self.MODELS)
        self.model_combo.setCurrentText("large-v3-turbo")
        self.model_combo.setCurrentText("large-v3-turbo")
        self.model_combo.setToolTip(...)
        header.addWidget(self.model_combo)

        self.denoise_chk = QCheckBox("🔇 Gürültü Temizle")
        self.denoise_chk.setToolTip(
            "Transkripsiyon öncesi ses gürültüsünü azaltır.\n"
            "Mikrofon kayıtları ve gürültülü ortamlar için önerilir."
        )
        header.addWidget(self.denoise_chk)
        layout.addLayout(header)

        # ── Seçili dosya etiketi ──
        self.file_lbl = QLabel("Henüz dosya seçilmedi")
        self.file_lbl.setObjectName("status_label")
        self.file_lbl.setWordWrap(True)
        layout.addWidget(self.file_lbl)

        # ── Waveform ──
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform)

        # ── Progress bar ──
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # ── Durum logu ──
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status_label")
        layout.addWidget(self.status_lbl)

        # ── Transkript çıktısı ──
        output_lbl = QLabel("ÇIKTI")
        output_lbl.setObjectName("section_label")
        layout.addWidget(output_lbl)

        self.output_edit = QTextEdit()
        self.output_edit.setPlaceholderText(
            "Sol panelden bir ses dosyası seçin  —  ya da doğrudan sürükleyip bırakın.\n"
            "Ardından 'Transkribe Et' düğmesine basın."
        )
        self.output_edit.setReadOnly(False)
        layout.addWidget(self.output_edit, stretch=1)

        # ── Alt buton grubu ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.transcribe_btn = QPushButton("▶  Transkribe Et")
        self.transcribe_btn.setObjectName("primary_btn")
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.clicked.connect(self._start_transcription)
        btn_layout.addWidget(self.transcribe_btn)

        self.cancel_btn = QPushButton("■  Durdur")
        self.cancel_btn.setObjectName("danger_btn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_transcription)
        btn_layout.addWidget(self.cancel_btn)

        # Kopyala — dropdown menü: Düz metin / SRT / VTT
        self.copy_btn = QPushButton("⎘  Kopyala")
        self.copy_btn.setEnabled(False)
        copy_menu = QMenu(self)
        copy_menu.addAction("Düz metin",   self._copy_plain)
        copy_menu.addAction("SRT formatı", self._copy_srt)
        copy_menu.addAction("VTT formatı", self._copy_vtt)
        self.copy_btn.setMenu(copy_menu)
        btn_layout.addWidget(self.copy_btn)

        # Kaydet — dropdown menü: TXT / SRT / VTT
        self.save_btn = QPushButton("💾  Kaydet")
        self.save_btn.setEnabled(False)
        save_menu = QMenu(self)
        save_menu.addAction("TXT olarak kaydet", self._save_txt)
        save_menu.addAction("SRT olarak kaydet", self._save_srt)
        save_menu.addAction("VTT olarak kaydet", self._save_vtt)
        save_menu.addSeparator()
        save_menu.addAction("Hepsini kaydet (TXT + SRT + VTT)", self._save_all)
        self.save_btn.setMenu(save_menu)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        # ── Pipeline butonu — tam genişlik, ayrı satır ──
        self.pipeline_btn = QPushButton("→  TTS'e Gönder")
        self.pipeline_btn.setObjectName("pipeline_btn")
        self.pipeline_btn.setEnabled(False)
        self.pipeline_btn.setToolTip(
            "Transkripsiyon metnini 'Ses Üret' sekmesine gönder.\n"
            "TTS paneli açılır ve metin giriş alanına otomatik yapıştırılır."
        )
        self.pipeline_btn.clicked.connect(self._send_to_tts)
        layout.addWidget(self.pipeline_btn)

    # ── Dosya seçimi ─────────────────────────────────────────────────

    @pyqtSlot(Path)
    def on_file_selected(self, path: Path) -> None:
        self._current_file = path
        self._full_text    = ""
        self._segments     = []
        self.file_lbl.setText(f"📄  {path.name}")
        self.transcribe_btn.setEnabled(True)
        self.output_edit.clear()
        self.status_lbl.setText("")
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.pipeline_btn.setEnabled(False)
        self.waveform.load(path)

    # ── Transkripsiyon ────────────────────────────────────────────────

    def _start_transcription(self) -> None:
        if self._current_file is None:
            return

        self.output_edit.clear()
        self._full_text = ""
        self._segments  = []

        model_size   = self.model_combo.currentText()
        self._worker = TranscriptionWorker(self._current_file, model_size)
        self._worker.progress.connect(self._on_progress)
        self._worker.segment.connect(self._on_segment)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._set_busy(True)
        self._worker.start()

    def _cancel_transcription(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        self._set_busy(False)
        self.status_lbl.setText("⛔ İşlem iptal edildi.")

    # ── Worker sinyalleri ─────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_progress(self, message: str) -> None:
        self.status_lbl.setText(message)

    @pyqtSlot(float, float, str)
    def _on_segment(self, start: float, end: float, text: str) -> None:
        # Segment listesine ekle (export için)
        self._segments.append((start, end, text))

        # Görsel akış
        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        ts_fmt = QTextCharFormat()
        ts_fmt.setForeground(QColor(self.COLOR_TIMESTAMP))
        ts_fmt.setFontFamily("monospace")
        ts_fmt.setFontPointSize(10)
        cursor.insertText(f"[{_fmt_time(start)} → {_fmt_time(end)}]  ", ts_fmt)

        txt_fmt = QTextCharFormat()
        txt_fmt.setForeground(QColor(self.COLOR_TEXT))
        txt_fmt.setFontFamily("monospace")
        txt_fmt.setFontPointSize(12)
        cursor.insertText(text + "\n", txt_fmt)

        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    @pyqtSlot(str)
    def _on_finished(self, text: str) -> None:
        self._full_text = text
        self._set_busy(False)
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.pipeline_btn.setEnabled(True)
        self.status_lbl.setText(
            f"✅ Hazır  |  {len(self._segments)} segment"
        )
        if self._sts_mode and text:
            self.status_lbl.setText(
                f"✅ Hazır  |  {len(self._segments)} segment  "
                f"— STS: TTS'e otomatik gönderildi."
            )
            self.text_sent_to_tts.emit(text)
            
    def set_sts_mode(self, enabled: bool) -> None:
        """STS modunda transkripsiyon bitince otomatik TTS'e gönderir."""
        self._sts_mode = enabled

    @pyqtSlot(str)
    def _on_error(self, message: str) -> None:
        self.output_edit.setPlainText(f"[HATA]\n{message}")
        self._set_busy(False)
        self.status_lbl.setText(f"❌ {message}")

    # ── Pipeline ─────────────────────────────────────────────────────

    def _send_to_tts(self) -> None:
        """
        Transkripsiyon metnini TTS paneline iletir.
        MainWindow bu sinyali TTSPanel.receive_text slotuna bağlar.
        """
        if self._full_text:
            self.text_sent_to_tts.emit(self._full_text)
            self.status_lbl.setText(
                "📤 Metin TTS paneline gönderildi  —  'Ses Üret' sekmesine geçin."
            )

    # ── Kopyalama işlemleri ───────────────────────────────────────────

    def _copy_plain(self) -> None:
        self._to_clipboard(self._full_text)
        self.status_lbl.setText("📋 Düz metin kopyalandı.")

    def _copy_srt(self) -> None:
        self._to_clipboard(self._build_srt())
        self.status_lbl.setText("📋 SRT formatı kopyalandı.")

    def _copy_vtt(self) -> None:
        self._to_clipboard(self._build_vtt())
        self.status_lbl.setText("📋 VTT formatı kopyalandı.")

    # ── Kaydetme işlemleri ────────────────────────────────────────────

    def _save_txt(self) -> None:
        if not self._current_file:
            return
        p = FileManager.save_transcript(self._current_file, self._full_text)
        self.status_lbl.setText(f"💾 Kaydedildi: {p.name}")

    def _save_srt(self) -> None:
        if not self._current_file:
            return
        p = FileManager.save_srt(self._current_file, self._segments)
        self.status_lbl.setText(f"💾 Kaydedildi: {p.name}")

    def _save_vtt(self) -> None:
        if not self._current_file:
            return
        p = FileManager.save_vtt(self._current_file, self._segments)
        self.status_lbl.setText(f"💾 Kaydedildi: {p.name}")

    def _save_all(self) -> None:
        if not self._current_file:
            return
        p1 = FileManager.save_transcript(self._current_file, self._full_text)
        p2 = FileManager.save_srt(self._current_file, self._segments)
        p3 = FileManager.save_vtt(self._current_file, self._segments)
        self.status_lbl.setText(
            f"💾 Kaydedildi: {p1.name}  |  {p2.name}  |  {p3.name}"
        )

    # ── Format üreticileri ────────────────────────────────────────────

    def _build_srt(self) -> str:
        """Segment listesinden SRT string üretir (dosyaya yazmadan)."""
        lines: list[str] = []
        for i, (start, end, text) in enumerate(self._segments, start=1):
            h  = lambda sec: f"{int(sec)//3600:02d}:{(int(sec)%3600)//60:02d}:{int(sec)%60:02d}"  # noqa: E731
            ms = lambda sec: round((sec - int(sec)) * 1000)                                         # noqa: E731
            lines += [
                str(i),
                f"{h(start)},{ms(start):03d} --> {h(end)},{ms(end):03d}",
                text,
                "",
            ]
        return "\n".join(lines)

    def _build_vtt(self) -> str:
        """Segment listesinden VTT string üretir (dosyaya yazmadan)."""
        lines: list[str] = ["WEBVTT", ""]
        for start, end, text in self._segments:
            h  = lambda sec: f"{int(sec)//3600:02d}:{(int(sec)%3600)//60:02d}:{int(sec)%60:02d}"  # noqa: E731
            ms = lambda sec: round((sec - int(sec)) * 1000)                                         # noqa: E731
            lines += [
                f"{h(start)}.{ms(start):03d} --> {h(end)}.{ms(end):03d}",
                text,
                "",
            ]
        return "\n".join(lines)

    # ── Yardımcılar ───────────────────────────────────────────────────

    @staticmethod
    def _to_clipboard(text: str) -> None:
        from PyQt6.QtWidgets import QApplication  # noqa: PLC0415
        QApplication.clipboard().setText(text)

    def _set_busy(self, busy: bool) -> None:
        self.progress_bar.setVisible(busy)
        self.transcribe_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.model_combo.setEnabled(not busy)
        # Transkripsiyon devam ederken pipeline butonu da devre dışı
        if busy:
            self.pipeline_btn.setEnabled(False)