# ui/archive_panel.py
"""
EchoForge — Transkript Arşivi Paneli.

Kayıtlı transkriptleri listeler, keyword ve semantic arama yapar.
Seçilen kaydı TTS veya TTT paneline gönderebilir.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSplitter, QAbstractItemView,
    QRadioButton, QButtonGroup, QMessageBox,
)
from PyQt6.QtGui import QColor

from ui.styles import COLORS
import core.archive_manager as am


# ── Arama worker (UI bloklamaz) ───────────────────────────────────────────────

class SearchWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, query: str, mode: str) -> None:
        super().__init__()
        self.query = query
        self.mode  = mode   # "keyword" | "semantic"

    def run(self) -> None:
        try:
            if self.mode == "semantic":
                results = am.semantic_search(self.query, top_k=20)
            else:
                results = am.keyword_search(self.query, limit=50)
            self.finished.emit(results)
        except Exception as exc:
            self.error.emit(str(exc))


# ── Panel ─────────────────────────────────────────────────────────────────────

class ArchivePanel(QWidget):
    """
    Transkript arşivi sekmesi.

    Sinyaller:
        text_sent_to_tts(str)
        text_sent_to_ttt(str)
    """

    text_sent_to_tts = pyqtSignal(str)
    text_sent_to_ttt = pyqtSignal(str)

    COL_ID   = 0
    COL_FILE = 1
    COL_LANG = 2
    COL_DUR  = 3
    COL_DATE = 4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._records:      list[dict] = []
        self._search_worker: SearchWorker | None = None
        self._setup_ui()
        self._load_all()

    # ══════════════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # ── Başlık + istatistik ───────────────────────────────────────
        header = QHBoxLayout()
        title  = QLabel("TRANSKRİPT ARŞİVİ")
        title.setObjectName("section_label")
        header.addWidget(title)
        header.addStretch()
        self.stats_lbl = QLabel("")
        self.stats_lbl.setObjectName("status_label")
        header.addWidget(self.stats_lbl)
        root.addLayout(header)

        # ── Arama çubuğu ──────────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Ara… (Enter ile çalıştır)")
        self.search_edit.returnPressed.connect(self._on_search)
        search_row.addWidget(self.search_edit, stretch=1)

        # Arama modu
        self.radio_keyword  = QRadioButton("Kelime")
        self.radio_semantic = QRadioButton("Semantik")
        self.radio_keyword.setChecked(True)
        self.radio_semantic.setToolTip(
            "nomic-embed-text ile anlam bazlı arama.\n"
            "Ollama çalışıyor olmalı."
        )
        bg = QButtonGroup(self)
        bg.addButton(self.radio_keyword)
        bg.addButton(self.radio_semantic)
        search_row.addWidget(self.radio_keyword)
        search_row.addWidget(self.radio_semantic)

        btn_search = QPushButton("🔍  Ara")
        btn_search.setObjectName("primary_btn")
        btn_search.clicked.connect(self._on_search)
        search_row.addWidget(btn_search)

        btn_all = QPushButton("↺  Tümünü Göster")
        btn_all.clicked.connect(self._load_all)
        search_row.addWidget(btn_all)

        root.addLayout(search_row)

        # ── İçerik splitter ───────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Sol — liste
        left = QWidget()
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(6)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Dosya", "Dil", "Süre", "Tarih"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_FILE, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_DATE, QHeaderView.ResizeMode.ResizeToContents
        )
        for col in (self.COL_ID, self.COL_LANG, self.COL_DUR):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.verticalHeader().setVisible(False)
        self.table.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        ll.addWidget(self.table)

        # Silme butonu
        btn_delete = QPushButton("🗑  Seçili Kaydı Sil")
        btn_delete.setObjectName("danger_btn")
        btn_delete.clicked.connect(self._on_delete)
        ll.addWidget(btn_delete)

        splitter.addWidget(left)

        # Sağ — önizleme + aksiyonlar
        right = QWidget()
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)

        preview_lbl = QLabel("ÖNİZLEME")
        preview_lbl.setObjectName("section_label")
        rl.addWidget(preview_lbl)

        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText("Bir kayıt seçin…")
        rl.addWidget(self.preview_edit, stretch=1)

        # Aksiyon butonları
        btn_tts = QPushButton("🔊  TTS'e Gönder")
        btn_tts.setObjectName("btn_primary")
        btn_tts.clicked.connect(self._send_to_tts)
        rl.addWidget(btn_tts)

        btn_ttt = QPushButton("✏️  TTT'ye Gönder")
        btn_ttt.clicked.connect(self._send_to_ttt)
        rl.addWidget(btn_ttt)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, stretch=1)

        # ── Durum ─────────────────────────────────────────────────────
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("status_label")
        root.addWidget(self.status_lbl)

    # ══════════════════════════════════════════════════════════════════
    #  Veri
    # ══════════════════════════════════════════════════════════════════

    def _load_all(self) -> None:
        records = am.get_all()
        self._populate(records)
        self._update_stats()

    def _populate(self, records: list[dict]) -> None:
        self._records = records
        self.table.setRowCount(0)

        for r in records:
            row = self.table.rowCount()
            self.table.insertRow(row)

            dur_s = r.get("duration", 0) or 0
            dur   = f"{int(dur_s)//60:02d}:{int(dur_s)%60:02d}"

            for col, val in [
                (self.COL_ID,   str(r["id"])),
                (self.COL_FILE, r["filename"]),
                (self.COL_LANG, r.get("language", "")),
                (self.COL_DUR,  dur),
                (self.COL_DATE, r["created_at"][:16]),
            ]:
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                self.table.setItem(row, col, item)

        self.status_lbl.setText(f"{len(records)} kayıt")

    def _update_stats(self) -> None:
        s   = am.stats()
        dur = s["total_duration"]
        self.stats_lbl.setText(
            f"Toplam: {s['total']} kayıt  ·  "
            f"{int(dur)//3600}s {(int(dur)%3600)//60}d  ·  "
            f"Embedding: {s['with_embedding']}"
        )

    # ══════════════════════════════════════════════════════════════════
    #  Arama
    # ══════════════════════════════════════════════════════════════════

    def _on_search(self) -> None:
        query = self.search_edit.text().strip()
        if not query:
            self._load_all()
            return

        mode = "semantic" if self.radio_semantic.isChecked() else "keyword"
        self.status_lbl.setText("🔍 Aranıyor…")

        self._search_worker = SearchWorker(query, mode)
        self._search_worker.finished.connect(self._on_search_done)
        self._search_worker.error.connect(
            lambda e: self.status_lbl.setText(f"❌ {e}")
        )
        self._search_worker.start()

    @pyqtSlot(list)
    def _on_search_done(self, results: list) -> None:
        self._populate(results)
        mode = "semantik" if self.radio_semantic.isChecked() else "kelime"
        self.status_lbl.setText(f"{len(results)} sonuç ({mode} arama)")

    # ══════════════════════════════════════════════════════════════════
    #  Seçim / Önizleme
    # ══════════════════════════════════════════════════════════════════

    def _on_selection_changed(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.preview_edit.clear()
            return
        row = rows[0].row()
        if row >= len(self._records):
            return
        record = self._records[row]
        # Tam metni getir
        full = am.get_by_id(record["id"])
        if full:
            self.preview_edit.setPlainText(full["text"])

    def _selected_text(self) -> str | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        if row >= len(self._records):
            return None
        full = am.get_by_id(self._records[row]["id"])
        return full["text"] if full else None

    # ══════════════════════════════════════════════════════════════════
    #  Aksiyonlar
    # ══════════════════════════════════════════════════════════════════

    def _send_to_tts(self) -> None:
        text = self._selected_text()
        if text:
            self.text_sent_to_tts.emit(text)
            self.status_lbl.setText("📤 TTS'e gönderildi.")

    def _send_to_ttt(self) -> None:
        text = self._selected_text()
        if text:
            self.text_sent_to_ttt.emit(text)
            self.status_lbl.setText("📤 TTT'ye gönderildi.")

    def _on_delete(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row    = rows[0].row()
        record = self._records[row]
        reply  = QMessageBox.question(
            self, "Sil",
            f"'{record['filename']}' kaydı silinsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            am.delete_by_id(record["id"])
            self._load_all()

    # ══════════════════════════════════════════════════════════════════
    #  Dışarıdan kayıt ekleme
    # ══════════════════════════════════════════════════════════════════

    def add_record(
        self,
        filename: str,
        text:     str,
        filepath: str  = "",
        language: str  = "",
        duration: float = 0.0,
        segments: list  = None,
    ) -> None:
        """
        TranscriptionPanel veya BatchWorker'dan çağrılır.
        Transkripsiyon bitince otomatik arşivler.
        """
        am.save_transcript(
            filename=filename,
            text=text,
            filepath=filepath,
            language=language,
            duration=duration,
            segments=segments or [],
        )
        self._load_all()
