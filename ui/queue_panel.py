"""
Toplu işlem kuyruğu paneli.
Dosyaları tabloda listeler; durum, ilerleme ve otomatik kaydetme içerir.
"""
from __future__ import annotations

from pathlib import Path
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QProgressBar, QComboBox, QCheckBox,
    QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QColor

from core.batch_worker import BatchWorker
from core.file_manager import FileManager, SegmentList


class FileStatus(str, Enum):
    WAITING    = "⏳ Bekliyor"
    PROCESSING = "🔄 İşleniyor"
    DONE       = "✅ Tamamlandı"
    ERROR      = "❌ Hata"
    CANCELLED  = "⛔ İptal"


# Sütun indeksleri
COL_NAME   = 0
COL_STATUS = 1
COL_INFO   = 2


class QueuePanel(QWidget):
    """
    Toplu işlem kuyruğunu yöneten panel.

    Sinyaller:
        queue_started()   → işlem başladı
        queue_finished()  → tüm kuyruk bitti
    """

    queue_started  = pyqtSignal()
    queue_finished = pyqtSignal()

    # Durum renkleri
    STATUS_COLORS = {
        FileStatus.WAITING:    "#888888",
        FileStatus.PROCESSING: "#FCD34D",
        FileStatus.DONE:       "#6EE7B7",
        FileStatus.ERROR:      "#F87171",
        FileStatus.CANCELLED:  "#888888",
    }

    MODELS = [
        "tiny", "base", "small", "medium",
        "large-v2", "large-v3", "large-v3-turbo",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._files:   list[Path]                    = []
        self._results: dict[int, tuple[str, SegmentList]] = {}  # idx → (text, segs)
        self._worker:  BatchWorker | None            = None
        self._setup_ui()

    # ── Arayüz ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # ── Başlık ──
        header = QHBoxLayout()
        title = QLabel("TOPLU İŞLEM")
        title.setObjectName("section_label")
        header.addWidget(title)
        header.addStretch()

        # Model seçici
        model_lbl = QLabel("Model:")
        model_lbl.setObjectName("status_label")
        header.addWidget(model_lbl)

        self.model_combo = QComboBox()
        self.model_combo.addItems(self.MODELS)
        self.model_combo.setCurrentText("large-v3-turbo")
        header.addWidget(self.model_combo)
        layout.addLayout(header)

        # ── Otomatik kaydetme seçenekleri ──
        auto_layout = QHBoxLayout()
        auto_lbl = QLabel("Otomatik kaydet:")
        auto_lbl.setObjectName("status_label")
        auto_layout.addWidget(auto_lbl)

        self.auto_txt = QCheckBox("TXT")
        self.auto_srt = QCheckBox("SRT")
        self.auto_vtt = QCheckBox("VTT")
        self.auto_txt.setChecked(True)
        self.auto_srt.setChecked(True)

        for cb in (self.auto_txt, self.auto_srt, self.auto_vtt):
            auto_layout.addWidget(cb)

        auto_layout.addStretch()
        layout.addLayout(auto_layout)

        # ── Tablo ──
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Dosya", "Durum", "Bilgi"])
        self.table.horizontalHeader().setSectionResizeMode(
            COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            COL_STATUS, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            COL_INFO, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # ── Genel ilerleme ──
        self.overall_lbl = QLabel("Kuyruk boş")
        self.overall_lbl.setObjectName("status_label")
        layout.addWidget(self.overall_lbl)

        self.overall_bar = QProgressBar()
        self.overall_bar.setFixedHeight(4)
        self.overall_bar.setVisible(False)
        layout.addWidget(self.overall_bar)

        # ── Butonlar ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton("▶  Kuyruğu Başlat")
        self.start_btn.setObjectName("primary_btn")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_queue)
        btn_layout.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("■  Durdur")
        self.cancel_btn.setObjectName("danger_btn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_queue)
        btn_layout.addWidget(self.cancel_btn)

        self.clear_btn = QPushButton("🗑  Kuyruğu Temizle")
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self._clear_queue)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

    # ── Dışarıdan çağrılan: dosya ekleme ─────────────────────────────

    def add_files(self, paths: list[Path]) -> None:
        """FilePanel'den veya drag&drop'tan yeni dosyalar ekler."""
        added = 0
        for path in paths:
            if path in self._files:
                continue   # Zaten kuyruktaysa atla
            self._files.append(path)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._set_cell(row, COL_NAME,   path.name)
            self._set_cell(row, COL_STATUS, FileStatus.WAITING)
            self._set_cell(row, COL_INFO,   "")
            added += 1

        if added:
            self._update_overall_label()
            self.start_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)

    # ── Kuyruk kontrolü ───────────────────────────────────────────────

    def _start_queue(self) -> None:
        if not self._files:
            return

        # Tablodaki tüm satırları "Bekliyor" durumuna sıfırla
        for row in range(self.table.rowCount()):
            self._set_cell(row, COL_STATUS, FileStatus.WAITING)
            self._set_cell(row, COL_INFO,   "")
        self._results.clear()

        model_size   = self.model_combo.currentText()
        self._worker = BatchWorker(self._files, model_size)

        self._worker.started_file.connect(self._on_file_started)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.file_error.connect(self._on_file_error)
        self._worker.all_done.connect(self._on_all_done)

        total = len(self._files)
        self.overall_bar.setRange(0, total)
        self.overall_bar.setValue(0)
        self.overall_bar.setVisible(True)
        self._update_overall_label(done=0, total=total)

        self._set_busy(True)
        self.queue_started.emit()
        self._worker.start()

    def _cancel_queue(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        # Hâlâ "Bekliyor" olan satırları iptal olarak işaretle
        for row in range(self.table.rowCount()):
            item = self.table.item(row, COL_STATUS)
            if item and item.text() == FileStatus.WAITING:
                self._set_cell(row, COL_STATUS, FileStatus.CANCELLED)
        self._set_busy(False)
        self.overall_lbl.setText("⛔ İşlem iptal edildi.")

    def _clear_queue(self) -> None:
        self._files.clear()
        self._results.clear()
        self.table.setRowCount(0)
        self.overall_bar.setVisible(False)
        self.overall_lbl.setText("Kuyruk boş")
        self.start_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)

    # ── Worker sinyalleri ─────────────────────────────────────────────

    @pyqtSlot(int, Path)
    def _on_file_started(self, idx: int, path: Path) -> None:
        self._set_cell(idx, COL_STATUS, FileStatus.PROCESSING)

    @pyqtSlot(int, Path, str)
    def _on_progress(self, idx: int, path: Path, message: str) -> None:
        if idx < self.table.rowCount():
            self._set_cell(idx, COL_INFO, message)
        self.overall_lbl.setText(message)

    @pyqtSlot(int, Path, str, list)
    def _on_file_done(
        self, idx: int, path: Path, full_text: str, seg_list: list
    ) -> None:
        self._results[idx] = (full_text, seg_list)
        self._set_cell(idx, COL_STATUS, FileStatus.DONE)

        # Otomatik kaydetme
        saved: list[str] = []
        if self.auto_txt.isChecked():
            FileManager.save_transcript(path, full_text)
            saved.append("TXT")
        if self.auto_srt.isChecked():
            FileManager.save_srt(path, seg_list)
            saved.append("SRT")
        if self.auto_vtt.isChecked():
            FileManager.save_vtt(path, seg_list)
            saved.append("VTT")

        info = f"Kaydedildi: {', '.join(saved)}" if saved else "Tamamlandı"
        self._set_cell(idx, COL_INFO, info)

        done = sum(
            1 for r in range(self.table.rowCount())
            if self.table.item(r, COL_STATUS) and
               self.table.item(r, COL_STATUS).text() == FileStatus.DONE
        )
        self.overall_bar.setValue(done)
        self._update_overall_label(done=done, total=len(self._files))

    @pyqtSlot(int, Path, str)
    def _on_file_error(self, idx: int, path: Path, message: str) -> None:
        self._set_cell(idx, COL_STATUS, FileStatus.ERROR)
        self._set_cell(idx, COL_INFO,   message)

    @pyqtSlot()
    def _on_all_done(self) -> None:
        self._set_busy(False)
        done  = sum(
            1 for r in range(self.table.rowCount())
            if self.table.item(r, COL_STATUS) and
               self.table.item(r, COL_STATUS).text() == FileStatus.DONE
        )
        total = len(self._files)
        self.overall_lbl.setText(
            f"🏁 Tamamlandı  |  {done}/{total} dosya başarılı"
        )
        self.queue_finished.emit()

    # ── Yardımcılar ───────────────────────────────────────────────────

    def _set_cell(self, row: int, col: int, value: str | FileStatus) -> None:
        """Hücreyi yazar ve durum sütununa renk uygular."""
        text = value if isinstance(value, str) else value.value
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        if col == COL_STATUS and isinstance(value, FileStatus):
            color = self.STATUS_COLORS.get(value, "#888888")
            item.setForeground(QColor(color))

        self.table.setItem(row, col, item)

    def _update_overall_label(
        self, done: int | None = None, total: int | None = None
    ) -> None:
        t = total if total is not None else len(self._files)
        if done is None:
            self.overall_lbl.setText(f"{t} dosya kuyruğa eklendi")
        else:
            self.overall_lbl.setText(f"İşleniyor…  {done}/{t} tamamlandı")

    def _set_busy(self, busy: bool) -> None:
        self.start_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.clear_btn.setEnabled(not busy)
        self.model_combo.setEnabled(not busy)