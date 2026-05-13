# ui/settings_panel.py
"""
EchoForge — Ayarlar Paneli.
SettingsManager üzerinden tüm ayarları UI'dan değiştirmeye izin verir.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton,
    QGroupBox, QFileDialog, QMessageBox,
)

from core.settings_manager import SettingsManager
from ui.styles import COLORS


class SettingsPanel(QWidget):
    """Ayarlar sekmesi."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._sm = SettingsManager.instance()
        self._setup_ui()
        self._load_values()

    # ── Arayüz ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(24)

        title = QLabel("AYARLAR")
        title.setObjectName("section_label")
        root.addWidget(title)

        root.addWidget(self._build_stt_group())
        root.addWidget(self._build_tts_group())
        root.addWidget(self._build_general_group())
        root.addStretch()
        root.addWidget(self._build_buttons())

    def _build_stt_group(self) -> QGroupBox:
        group = QGroupBox("STT — Transkripsiyon")
        form  = QFormLayout(group)
        form.setContentsMargins(16, 12, 16, 12)
        form.setSpacing(10)

        self.hf_cache_edit = self._line_edit_with_browse(
            "hf_cache_dir", "HuggingFace Cache Dizini"
        )
        form.addRow("Cache Dizini:", self.hf_cache_edit)

        return group

    def _build_tts_group(self) -> QGroupBox:
        group = QGroupBox("TTS — Ses Üretimi")
        form  = QFormLayout(group)
        form.setContentsMargins(16, 12, 16, 12)
        form.setSpacing(10)

        self.model_dir_edit = self._line_edit_with_browse(
            "tts_model_dir", "Model Dizini"
        )
        form.addRow("Model Dizini:", self.model_dir_edit)

        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(50, 1000)
        self.chunk_spin.setSuffix("  karakter")
        self.chunk_spin.setToolTip(
            "Bu sınırı aşan metinler otomatik parçalanır.\n"
            "XTTSv2 için 200–300 önerilir."
        )
        form.addRow("Chunk Eşiği:", self.chunk_spin)

        self.silence_spin = QSpinBox()
        self.silence_spin.setRange(0, 2000)
        self.silence_spin.setSuffix("  ms")
        self.silence_spin.setToolTip("Ses parçaları arasındaki sessizlik süresi.")
        form.addRow("Parça Arası Sessizlik:", self.silence_spin)

        return group

    def _build_general_group(self) -> QGroupBox:
        group = QGroupBox("Genel")
        form  = QFormLayout(group)
        form.setContentsMargins(16, 12, 16, 12)
        form.setSpacing(10)

        self.output_dir_edit = self._line_edit_with_browse(
            "output_dir", "Çıktı Dizini"
        )
        self.output_dir_edit.setPlaceholderText("Boş = varsayılan (proje/output/)")
        form.addRow("Çıktı Dizini:", self.output_dir_edit)
        self.gemini_key_edit = QLineEdit()
        self.gemini_key_edit.setPlaceholderText("AIza...")
        self.gemini_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Gemini API Key:", self.gemini_key_edit)

        return group

    def _build_buttons(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()

        btn_reset = QPushButton("↺  Varsayılanlara Dön")
        btn_reset.clicked.connect(self._on_reset)
        layout.addWidget(btn_reset)

        btn_save = QPushButton("💾  Kaydet")
        btn_save.setObjectName("primary_btn")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        return row

    # ── Yardımcı: satır + gözat butonu ────────────────────────────────

    def _line_edit_with_browse(self, key: str, title: str) -> QLineEdit:
        """QLineEdit döndürür; dışarıda form'a eklenir."""
        edit = QLineEdit()
        edit.setProperty("settings_key", key)
        edit.setMinimumWidth(320)

        # Gözat butonu edit'e eklersek form bozulur,
        # bu yüzden browse fonksiyonunu doğrudan edit üzerinden tetikleriz.
        # Alternatif: dışarıda QHBoxLayout sarmalayıcı kullanılabilir,
        # ancak FormLayout ile uyum için şimdilik sadece edit dönüyoruz.
        return edit

    # ── Değer yükleme / kaydetme ───────────────────────────────────────

    def _load_values(self) -> None:
        self.hf_cache_edit.setText(self._sm.get("hf_cache_dir"))
        self.model_dir_edit.setText(self._sm.get("tts_model_dir"))
        self.output_dir_edit.setText(self._sm.get("output_dir"))
        self.chunk_spin.setValue(int(self._sm.get("chunk_threshold")))
        self.silence_spin.setValue(int(self._sm.get("silence_ms")))
        self.gemini_key_edit.setText(self._sm.get("gemini_api_key", ""))

    def _on_save(self) -> None:
        self._sm.set_many({
            "hf_cache_dir":    self.hf_cache_edit.text().strip(),
            "tts_model_dir":   self.model_dir_edit.text().strip(),
            "output_dir":      self.output_dir_edit.text().strip(),
            "chunk_threshold": self.chunk_spin.value(),
            "silence_ms":      self.silence_spin.value(),
            "gemini_api_key": self.gemini_key_edit.text().strip(),
        })
        QMessageBox.information(self, "Ayarlar", "Ayarlar kaydedildi. ✓")

    def _on_reset(self) -> None:
        reply = QMessageBox.question(
            self, "Sıfırla",
            "Tüm ayarlar varsayılana döndürülecek. Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._sm.reset()
            self._load_values()
