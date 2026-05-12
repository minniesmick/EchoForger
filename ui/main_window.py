# ui/main_window.py
"""
EchoForge — Ana Pencere.

Mimari:
    ┌─────────────────────────────────────────────────────────┐
    │  QSplitter (Horizontal)                                 │
    │  ┌──────────────┐  ┌──────────────────────────────────┐ │
    │  │  FilePanel   │  │  QTabWidget                      │ │
    │  │  (sol panel) │  │  ├─ 📝 Tekli İşlem              │ │
    │  │              │  │  │     TranscriptionPanel        │ │
    │  │              │  │  ├─ 📋 Toplu İşlem               │ │
    │  │              │  │  │     QueuePanel                │ │
    │  │              │  │  └─ 🎙 Ses Üret                 │ │
    │  │              │  │        TTSPanel                  │ │
    │  └──────────────┘  └──────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────┘

Sinyal bağlantıları:
    FilePanel.file_selected            → TranscriptionPanel.on_file_selected
    FilePanel.files_selected_for_queue → QueuePanel.add_files
    TranscriptionPanel.text_sent_to_tts → TTSPanel.receive_text
      (pipeline: transkripsiyon → ses üretimi)
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.file_manager import FileManager
from ui.file_panel import FilePanel
from ui.transcription_panel import TranscriptionPanel
from ui.queue_panel import QueuePanel
from ui.tts_panel import TTSPanel
from ui.styles import MAIN_STYLESHEET, COLORS


class MainWindow(QMainWindow):
    """
    EchoForge ana penceresi.
    Sol taraf: dosya gezgini (FilePanel).
    Sağ taraf: üç sekmeli işlem alanı.
    """

    APP_NAME    = "EchoForge"
    MIN_WIDTH   = 1200
    MIN_HEIGHT  = 720
    LEFT_WIDTH  = 260   # FilePanel başlangıç genişliği

    def __init__(self) -> None:
        super().__init__()
        FileManager.ensure_directories()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._apply_styles()

    # ── Pencere ayarları ──────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle(self.APP_NAME)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(1400, 820)

    # ── Arayüz kurulumu ───────────────────────────────────────────────

    def _setup_ui(self) -> None:
        # Merkezi widget
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Üst başlık şeridi ──
        header = self._build_header()
        root_layout.addWidget(header)

        # ── Ana içerik: Splitter ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Sol panel — dosya gezgini
        self.file_panel = FilePanel()
        splitter.addWidget(self.file_panel)

        # Sağ panel — sekmeli işlem alanı
        self.tab_widget = self._build_tabs()
        splitter.addWidget(self.tab_widget)

        # Başlangıç boyutları: sol 260px, sağ kalan
        splitter.setSizes([self.LEFT_WIDTH, self.MIN_WIDTH - self.LEFT_WIDTH])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter, stretch=1)

        # ── Status bar ──
        self._setup_status_bar()

    def _build_header(self) -> QWidget:
        """Logo + isim + altyazı içeren ince üst şerit."""
        bar = QWidget()
        bar.setObjectName("header_bar")
        bar.setFixedHeight(48)
        bar.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        title = QLabel(self.APP_NAME)
        title.setObjectName("app_title")
        layout.addWidget(title)

        subtitle = QLabel("Speech-to-Text  ·  Text-to-Speech")
        subtitle.setObjectName("app_subtitle")
        layout.addWidget(subtitle)

        layout.addStretch()

        version = QLabel("v1.0")
        version.setObjectName("subtitle")
        layout.addWidget(version)

        return bar

    def _build_tabs(self) -> QTabWidget:
        """Üç sekmeli sağ panel."""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setDocumentMode(True)

        # ── Sekme 0: Tekli Transkripsiyon ──
        self.transcription_panel = TranscriptionPanel()
        tabs.addTab(self.transcription_panel, "📝  Transkribe Et")

        # ── Sekme 1: Toplu İşlem ──
        self.queue_panel = QueuePanel()
        tabs.addTab(self.queue_panel, "📋  Toplu İşlem")

        # ── Sekme 2: TTS ──
        self.tts_panel = TTSPanel()
        tabs.addTab(self.tts_panel, "🎙  Ses Üret")

        return tabs

    def _setup_status_bar(self) -> None:
        """Alt durum çubuğu — hazır mesajı ve sonraki ipuçları."""
        bar = QStatusBar()
        self.setStatusBar(bar)
        bar.showMessage(
            "Hazır  —  Sol panelden bir ses dosyası seçin veya sürükleyin."
        )
        self._status_bar = bar

    # ── Sinyal bağlantıları ───────────────────────────────────────────

    def _connect_signals(self) -> None:
        # Dosya seçimi → tekli transkripsiyon
        self.file_panel.file_selected.connect(
            self.transcription_panel.on_file_selected
        )

        # Çoklu dosya seçimi → toplu işlem kuyruğu
        self.file_panel.files_selected_for_queue.connect(
            self.queue_panel.add_files
        )

        # Toplu işlem kuyruğuna dosya eklenince sekmeye geç (opsiyonel ipucu)
        self.file_panel.files_selected_for_queue.connect(
            self._on_files_sent_to_queue
        )

        # Pipeline: Transkripsiyon → TTS
        self.transcription_panel.text_sent_to_tts.connect(
            self._on_pipeline_triggered
        )

        # Durum çubuğu güncellemeleri
        self.queue_panel.queue_started.connect(
            lambda: self._status_bar.showMessage("⏳ Toplu işlem başladı…")
        )
        self.queue_panel.queue_finished.connect(
            lambda: self._status_bar.showMessage("🏁 Toplu işlem tamamlandı.")
        )

    # ── Slot: Pipeline ────────────────────────────────────────────────

    @pyqtSlot(str)
    def _on_pipeline_triggered(self, text: str) -> None:
        """
        TranscriptionPanel'den gelen metni TTSPanel'e iletir ve
        'Ses Üret' sekmesine otomatik geçer.
        """
        self.tts_panel.receive_text(text)
        tts_index = self.tab_widget.indexOf(self.tts_panel)
        self.tab_widget.setCurrentIndex(tts_index)
        self._status_bar.showMessage(
            "📤 Metin 'Ses Üret' sekmesine aktarıldı — model seçip üretmeye hazır."
        )

    # ── Slot: Toplu işlem ─────────────────────────────────────────────

    @pyqtSlot(list)
    def _on_files_sent_to_queue(self, paths: list) -> None:
        """
        Dosyalar kuyruğa eklenince 'Toplu İşlem' sekmesine geç.
        """
        queue_index = self.tab_widget.indexOf(self.queue_panel)
        self.tab_widget.setCurrentIndex(queue_index)
        count = len(paths)
        self._status_bar.showMessage(
            f"📋 {count} dosya kuyruğa eklendi  —  'Kuyruğu Başlat'a basın."
        )

    # ── Stil ─────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        self.setStyleSheet(MAIN_STYLESHEET)