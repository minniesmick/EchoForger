# ui/file_panel.py
"""
EchoForge — Dosya Gezgini Paneli.

İşlev:
    1. voice_files/ klasöründeki sesleri listeler.
    2. Yeni ses dosyaları eklemeye izin verir (kopyalama).
    3. Dosya seçildiğinde TranscriptionPanel'e sinyal gönderir.
    4. Çoklu seçim ile Toplu İşlem kuyruğuna dosya gönderir.
"""
from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFileDialog,
    QMenu,
    QFrame,
)

from core.file_manager import FileManager
from ui.styles import COLORS


class FilePanel(QWidget):
    """
    Sol panel: Kullanıcının işleyeceği ses dosyalarını yönettiği yer.
    """
    # Sinyaller
    file_selected = pyqtSignal(Path)           # Tekli transkripsiyon için
    files_selected_for_queue = pyqtSignal(list)  # Toplu işlem kuyruğu için

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("file_panel")
        self._setup_ui()
        self.refresh_list()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)

        # ── Başlık Bölümü ──
        header_layout = QHBoxLayout()
        title = QLabel("SES DOSYALARI")
        title.setObjectName("section_title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedSize(28, 28)
        btn_refresh.setToolTip("Listeyi Yenile")
        btn_refresh.clicked.connect(self.refresh_list)
        header_layout.addWidget(btn_refresh)
        
        layout.addLayout(header_layout)

        # ── Dosya Listesi ──
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setDragEnabled(False)
        self.list_widget.setSpacing(2)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

        # ── Alt Butonlar ──
        btn_add = QPushButton("➕ DOSYA EKLE")
        btn_add.setObjectName("primary_button")
        btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._on_add_files)
        layout.addWidget(btn_add)

        btn_queue = QPushButton("📋 KUYRUĞA EKLE")
        btn_queue.setObjectName("secondary_button")
        btn_queue.setFixedHeight(36)
        btn_queue.clicked.connect(self._on_send_to_queue)
        layout.addWidget(btn_queue)

        # Bilgi notu
        info = QLabel("Çift tıkla: Transkript\nSeçili + Kuyruk: Toplu İşlem")
        info.setObjectName("subtitle")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

    # ── Veri Yönetimi ─────────────────────────────────────────────────────────

    def refresh_list(self) -> None:
        """voice_files/ klasörünü tara ve listeyi güncelle."""
        self.list_widget.clear()
        files = FileManager.get_voice_files()
        
        for fpath in files:
            item = QListWidgetItem(fpath.name)
            item.setData(Qt.ItemDataRole.UserRole, str(fpath))
            item.setToolTip(str(fpath))
            # Ses ikonu (varsa)
            # item.setIcon(QIcon("...")) 
            self.list_widget.addItem(item)

    # ── Olaylar ───────────────────────────────────────────────────────────────

    def _on_add_files(self) -> None:
        """Dışarıdan dosya seçip proje klasörüne kopyalar."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Ses Dosyaları Seç", "", 
            "Ses Dosyaları (*.mp3 *.wav *.m4a *.ogg *.flac *.mp4 *.webm)"
        )
        if not files:
            return

        for f in files:
            FileManager.copy_to_voice_dir(Path(f))
        
        self.refresh_list()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Çift tıklandığında dosyayı ana transkripsiyon paneline gönderir."""
        path_str = item.data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(Path(path_str))

    def _on_send_to_queue(self) -> None:
        """Seçili dosyaları toplu işlem kuyruğuna gönderir."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        paths = [Path(i.data(Qt.ItemDataRole.UserRole)) for i in selected_items]
        self.files_selected_for_queue.emit(paths)

    def _show_context_menu(self, pos) -> None:
        """Sağ tık menüsü."""
        item = self.list_widget.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        
        act_transcribe = QAction("Transkripsiyona Gönder", self)
        act_transcribe.triggered.connect(lambda: self._on_item_double_clicked(item))
        menu.addAction(act_transcribe)

        act_queue = QAction("Kuyruğa Ekle", self)
        act_queue.triggered.connect(self._on_send_to_queue)
        menu.addAction(act_queue)

        menu.addSeparator()

        act_open_folder = QAction("Klasörde Göster", self)
        act_open_folder.triggered.connect(lambda: self._open_in_explorer(item))
        menu.addAction(act_open_folder)

        menu.exec(self.list_widget.mapToGlobal(pos))

    def _open_in_explorer(self, item: QListWidgetItem) -> None:
        import sys, subprocess
        path = Path(item.data(Qt.ItemDataRole.UserRole)).parent
        if sys.platform == "win32":
            subprocess.run(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])
