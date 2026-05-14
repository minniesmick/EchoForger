# ui/tts_panel.py
"""
EchoForge — TTS Paneli.

Voice Forge MainWindow sınıfından çıkarılmış bağımsız QWidget.
EchoForge'un QTabWidget içindeki "🎙 Ses Üret" sekmesini oluşturur.

Desteklenen motorlar:
    • XTTSv2      (Coqui — lokal CUDA, 57 ses, klonlama)
    • Hume TADA   (bulut API, 7 ses, klonlama yok)

Dışarıdan metin almak (pipeline):
    panel.receive_text(text: str)
        → text_input alanını doldurur, karakter sayacını günceller.

Değişiklikler (Voice Forge → EchoForge):
    - QMainWindow  → QWidget
    - Kendi COLORS/stylesheet yerine ui/styles.py kullanılır
    - REFERENCE_VOICES_DIR / OUTPUT_AUDIO_DIR → core/file_manager
    - QFileSystemWatcher reference_voices/ klasörünü izler
    - tts_engine / workers → tts.* paketinden import edilir
"""
from __future__ import annotations

import datetime
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QFileSystemWatcher, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.file_manager import FileManager
from tts.tts_engine import (
    BaseTTSEngine,
    TTSEngineFactory,
    SUPPORTED_LANGUAGES,
    MODEL_DISPLAY_NAMES,
    MODEL_XTTS,
    MODEL_HUME_TADA,
)
from tts.workers import (
    ModelLoaderWorker,
    ModelUnloaderWorker,
    TTSWorker,
    ChunkedTTSWorker,
)
from ui.styles import COLORS

# Metnin bu karakter sayısını geçmesi durumunda ChunkedTTSWorker kullanılır
from core.settings_manager import SettingsManager
CHUNK_THRESHOLD = SettingsManager.instance().get("chunk_threshold")

class TTSPanel(QWidget):
    """
    Ses üretimi paneli.

    Dışarıdan bağlanılacak slot:
        receive_text(str)  → TranscriptionPanel'den pipeline ile metin alır.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # ── Motor durumu ──────────────────────────────────────────────
        self._current_model_id: str              = MODEL_XTTS
        self.engine:            BaseTTSEngine | None = None

        # ── Worker referansları (GC'den korunmak için) ────────────────
        self.loader_worker:   ModelLoaderWorker   | None = None
        self.unloader_worker: ModelUnloaderWorker | None = None
        self.tts_worker:      TTSWorker           | None = None
        self.chunked_worker:  ChunkedTTSWorker    | None = None

        # ── Klasörleri garantile ──────────────────────────────────────
        FileManager.ensure_directories()

        self._setup_ui()
        self._setup_watcher()

    # ══════════════════════════════════════════════════════════════════
    #  Arayüz kurulumu
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Üst model çubuğu ─────────────────────────────────────────
        root.addWidget(self._build_model_bar())

        # ── İçerik bölgesi (splitter) ─────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, stretch=1)

        # ── Alt ilerleme çubuğu ───────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("tts_progress")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        root.addWidget(self.progress_bar)

    # ── Model çubuğu ──────────────────────────────────────────────────

    def _build_model_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        model_lbl = QLabel("Motor:")
        model_lbl.setObjectName("status_label")
        layout.addWidget(model_lbl)

        self.model_combo = QComboBox()
        for model_id, display_name in MODEL_DISPLAY_NAMES.items():
            self.model_combo.addItem(display_name, userData=model_id)
        self.model_combo.currentIndexChanged.connect(self._on_model_combo_changed)
        layout.addWidget(self.model_combo)

        layout.addStretch()

        self.btn_load_model = QPushButton("  ⚡  Modeli Yükle")
        self.btn_load_model.setObjectName("btn_primary")
        self.btn_load_model.setMinimumWidth(160)
        self.btn_load_model.clicked.connect(self._on_load_model)
        layout.addWidget(self.btn_load_model)

        return bar

    # ── Sol kontrol paneli ────────────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 16, 20)
        layout.setSpacing(16)

        # Dil seçimi
        layout.addWidget(self._build_language_group())

        # Ses kaynağı
        layout.addWidget(self._build_voice_source_group())

        # Metin girişi
        layout.addWidget(self._build_text_group(), stretch=1)

        # Üret butonu
        layout.addWidget(self._build_generate_row())

        return panel

    def _build_language_group(self) -> QGroupBox:
        group = QGroupBox("DİL")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(12, 8, 12, 8)

        self.lang_combo = QComboBox()
        for lang_name in SUPPORTED_LANGUAGES:
            self.lang_combo.addItem(lang_name)
        # Türkçe varsayılan
        tr_index = self.lang_combo.findText("Türkçe")
        if tr_index >= 0:
            self.lang_combo.setCurrentIndex(tr_index)

        layout.addWidget(self.lang_combo)
        return group

    def _build_voice_source_group(self) -> QGroupBox:
        group = QGroupBox("SES KAYNAĞI")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(10)

        btn_group = QButtonGroup(self)

        # ── Dahili ses ────────────────────────────────────────────────
        self.radio_default = QRadioButton("Dahili Ses")
        self.radio_default.setChecked(True)
        btn_group.addButton(self.radio_default)
        layout.addWidget(self.radio_default)

        speaker_row = QHBoxLayout()
        speaker_row.setContentsMargins(20, 0, 0, 0)
        self.speaker_combo = QComboBox()
        self.speaker_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        speaker_row.addWidget(self.speaker_combo)
        layout.addLayout(speaker_row)

        # ── Ses klonlama ──────────────────────────────────────────────
        self.radio_clone = QRadioButton("Ses Klonlama")
        btn_group.addButton(self.radio_clone)
        layout.addWidget(self.radio_clone)

        clone_row = QHBoxLayout()
        clone_row.setContentsMargins(20, 0, 0, 0)
        clone_row.setSpacing(6)

        self.voice_file_combo = QComboBox()
        self.voice_file_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        clone_row.addWidget(self.voice_file_combo)

        self.btn_refresh_voices = QPushButton("↻")
        self.btn_refresh_voices.setFixedWidth(36)
        self.btn_refresh_voices.setToolTip("Referans ses listesini yenile")
        self.btn_refresh_voices.clicked.connect(self._refresh_voice_files)
        clone_row.addWidget(self.btn_refresh_voices)

        self.btn_open_ref_dir = QPushButton("📂")
        self.btn_open_ref_dir.setFixedWidth(36)
        self.btn_open_ref_dir.setToolTip("reference_voices/ klasörünü aç")
        self.btn_open_ref_dir.clicked.connect(self._open_reference_voices_dir)
        clone_row.addWidget(self.btn_open_ref_dir)

        layout.addLayout(clone_row)

        # Radio değişimini dinle
        self.radio_default.toggled.connect(self._on_voice_source_changed)

        # İlk doldurmayı yap
        self._refresh_voice_files()
        self._update_voice_source_ui()

        return group

    def _build_text_group(self) -> QGroupBox:
        group = QGroupBox("METİN")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        self.text_input = QTextEdit()
        self.text_input.setObjectName("tts_text_input")
        self.text_input.setPlaceholderText(
            "Sese dönüştürülecek metni buraya yazın…\n\n"
            f"İpucu: {CHUNK_THRESHOLD} karakteri aşan metinler otomatik olarak\n"
            "parçalara bölünür ve birleştirilerek üretilir."
        )
        self.text_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_input, stretch=1)

        self.char_count_lbl = QLabel("0 karakter")
        self.char_count_lbl.setObjectName("status_label")
        self.char_count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.char_count_lbl)

        return group

    def _build_generate_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.btn_generate = QPushButton("  ▶  Ses Üret")
        self.btn_generate.setObjectName("btn_primary")
        self.btn_generate.setMinimumHeight(44)
        self.btn_generate.setEnabled(False)
        self.btn_generate.clicked.connect(self._on_generate)
        layout.addWidget(self.btn_generate, stretch=1)

        self.btn_open_output = QPushButton("📂 Çıktı")
        self.btn_open_output.setToolTip("output/audio/ klasörünü aç")
        self.btn_open_output.clicked.connect(self._open_audio_dir)
        layout.addWidget(self.btn_open_output)

        return row

    # ── Sağ log paneli ────────────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 20, 20, 20)
        layout.setSpacing(10)

        log_lbl = QLabel("DURUM / LOG")
        log_lbl.setObjectName("section_label")
        layout.addWidget(log_lbl)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlaceholderText(
            "İşlem adımları burada görünür.\n\n"
            "• Modeli yükleyin\n"
            "• Metin girin\n"
            "• Ses Üret'e basın"
        )
        layout.addWidget(self.log_edit, stretch=1)

        # Logu temizle
        btn_clear = QPushButton("🗑  Logu Temizle")
        btn_clear.clicked.connect(self.log_edit.clear)
        layout.addWidget(btn_clear)

        return panel

    # ══════════════════════════════════════════════════════════════════
    #  QFileSystemWatcher — reference_voices/ otomatik güncelleme
    # ══════════════════════════════════════════════════════════════════

    def _setup_watcher(self) -> None:
        ref_dir = FileManager.get_reference_voices_dir()
        self._watcher = QFileSystemWatcher([str(ref_dir)])
        self._watcher.directoryChanged.connect(
            lambda _: self._refresh_voice_files()
        )

    # ══════════════════════════════════════════════════════════════════
    #  Pipeline slot — TranscriptionPanel'den metin alır
    # ══════════════════════════════════════════════════════════════════

    @pyqtSlot(str)
    def receive_text(self, text: str) -> None:
        """
        Transkripsiyon panelinden "→ TTS'e Gönder" sinyaliyle tetiklenir.
        Mevcut text_input içeriğini temizler ve gelen metni yazar.
        """
        self.text_input.setPlainText(text)
        # İmleci başa al
        cursor = self.text_input.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.text_input.setTextCursor(cursor)
        self._log(
            "📋 Transkripsiyon metni TTS giriş alanına aktarıldı.",
            COLORS["accent_stt"],
        )

    # ══════════════════════════════════════════════════════════════════
    #  Ses kaynağı UI güncelleme
    # ══════════════════════════════════════════════════════════════════

    def _on_voice_source_changed(self) -> None:
        self._update_voice_source_ui()

    def _update_voice_source_ui(self) -> None:
        """Radio seçimine göre speaker_combo / voice_file_combo aktif eder."""
        default_on = self.radio_default.isChecked()
        self.speaker_combo.setEnabled(
            default_on and self.radio_default.isEnabled()
        )
        self.voice_file_combo.setEnabled(
            not default_on and self.radio_clone.isEnabled()
        )
        self.btn_refresh_voices.setEnabled(
            not default_on and self.radio_clone.isEnabled()
        )

    def _update_voice_ui_for_model(
        self,
        model_id: str,
        engine: BaseTTSEngine | None,
    ) -> None:
        """
        Seçili motor kapasitelerine göre ses kaynağı UI'ını günceller.
        engine=None → motor yüklenmedi, her iki seçenek de devre dışı.
        """
        supports_default = engine is not None and engine.supports_default_speakers
        supports_clone   = engine is not None and engine.supports_voice_cloning

        self.radio_default.setEnabled(supports_default)
        self.radio_clone.setEnabled(supports_clone)

        # Konuşmacı listesini güncelle
        self.speaker_combo.clear()
        if supports_default and engine is not None:
            self.speaker_combo.addItems(engine.default_speakers)
            craig_index = self.speaker_combo.findText("Craig Gutsy")
            if craig_index >= 0:
                self.speaker_combo.setCurrentIndex(craig_index)

        # Geçerli seçimi düzelt
        if supports_default:
            self.radio_default.setChecked(True)
        elif supports_clone:
            self.radio_clone.setChecked(True)

        self._update_voice_source_ui()

    def _refresh_voice_files(self) -> None:
        """reference_voices/ klasöründeki .wav listesini yeniler."""
        current_data = self.voice_file_combo.currentData()
        self.voice_file_combo.clear()

        files = FileManager.get_reference_voices()
        for wav_path in files:
            self.voice_file_combo.addItem(wav_path.name, userData=wav_path)

        # Önceki seçimi koru
        if current_data is not None:
            for i in range(self.voice_file_combo.count()):
                if self.voice_file_combo.itemData(i) == current_data:
                    self.voice_file_combo.setCurrentIndex(i)
                    break

        count = self.voice_file_combo.count()
        if count == 0:
            self.voice_file_combo.addItem("— referans ses bulunamadı —")

    # ══════════════════════════════════════════════════════════════════
    #  Slot: Model değiştirme
    # ══════════════════════════════════════════════════════════════════

    def _on_model_combo_changed(self, index: int) -> None:
        new_model_id: str = self.model_combo.itemData(index)
        if new_model_id == self._current_model_id:
            return

        if self.engine is not None and self.engine.is_loaded:
            reply = QMessageBox.question(
                self,
                "Motor Değiştir",
                "Yüklü model GPU'dan kaldırılacak.\nDevam etmek istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply != QMessageBox.StandardButton.Yes:
                old_index = self.model_combo.findData(self._current_model_id)
                self.model_combo.blockSignals(True)
                self.model_combo.setCurrentIndex(old_index)
                self.model_combo.blockSignals(False)
                return

            self._log(
                f"Eski motor kaldırılıyor: "
                f"{MODEL_DISPLAY_NAMES.get(self._current_model_id, '')}...",
                COLORS["warning"],
            )
            self._set_busy(True)
            self.unloader_worker = ModelUnloaderWorker(self.engine)
            self.unloader_worker.progress.connect(
                lambda msg: self._log(f"  ↳ {msg}")
            )
            self.unloader_worker.finished.connect(
                lambda: self._on_model_unloaded(new_model_id)
            )
            self.unloader_worker.error.connect(self._on_unload_error)
            self.unloader_worker.start()
        else:
            self._apply_model_switch(new_model_id)

    def _on_model_unloaded(self, new_model_id: str) -> None:
        self._log("✅ Eski motor başarıyla kaldırıldı.", COLORS["success"])
        self._apply_model_switch(new_model_id)
        self._set_busy(False)

    def _on_unload_error(self, error_msg: str) -> None:
        self._set_busy(False)
        self._log(f"⚠️ Motor kaldırma hatası: {error_msg}", COLORS["warning"])

    def _apply_model_switch(self, new_model_id: str) -> None:
        self._current_model_id = new_model_id
        self.engine = None
        self.btn_load_model.setText("  ⚡  Modeli Yükle")
        self.btn_load_model.setEnabled(True)
        self.btn_generate.setEnabled(False)
        self._update_voice_ui_for_model(new_model_id, engine=None)
        display = MODEL_DISPLAY_NAMES.get(new_model_id, new_model_id)
        self._log(f"Motor seçildi: {display}", COLORS["accent_tts"])

    # ══════════════════════════════════════════════════════════════════
    #  Slot: Model yükleme
    # ══════════════════════════════════════════════════════════════════

    def _on_load_model(self) -> None:
        if self.engine is not None and self.engine.is_loaded:
            return

        try:
            self.engine = TTSEngineFactory.create(self._current_model_id)
        except ValueError as exc:
            self._log(f"❌ {exc}", COLORS["error"])
            return

        display = MODEL_DISPLAY_NAMES.get(self._current_model_id, self._current_model_id)
        self._set_busy(True)
        self._log(f"Model yükleme başlatıldı: {display}", COLORS["accent_tts"])

        self.loader_worker = ModelLoaderWorker(self.engine)
        self.loader_worker.progress.connect(lambda msg: self._log(f"  ↳ {msg}"))
        self.loader_worker.finished.connect(self._on_model_loaded)
        self.loader_worker.error.connect(self._on_model_error)
        self.loader_worker.start()

    def _on_model_loaded(self) -> None:
        self._set_busy(False)
        self._update_voice_ui_for_model(self._current_model_id, self.engine)
        self.btn_generate.setEnabled(True)
        self.btn_load_model.setText("  ✓  Model Yüklendi")
        self.btn_load_model.setEnabled(False)

        # Kokoro seçildiyse dil combo'sunu Kokoro dilleriyle güncelle
        if self._current_model_id == "kokoro":
            self._set_kokoro_languages()
        else:
            self._restore_default_languages()
        display = MODEL_DISPLAY_NAMES.get(self._current_model_id, self._current_model_id)
        self._log(f"✅ {display} başarıyla yüklendi.", COLORS["success"])

    def _on_model_error(self, error_msg: str) -> None:
        self._set_busy(False)
        self.engine = None
        self._log(f"❌ Model Hatası: {error_msg}", COLORS["error"])
        QMessageBox.critical(self, "Model Yükleme Hatası", error_msg)

    def _set_kokoro_languages(self) -> None:
        from tts.kokoro_engine import KOKORO_LANGUAGES
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        for name in KOKORO_LANGUAGES:
            self.lang_combo.addItem(name)
        self.lang_combo.blockSignals(False)

    def _restore_default_languages(self) -> None:
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        for lang_name in SUPPORTED_LANGUAGES:
            self.lang_combo.addItem(lang_name)
        tr_index = self.lang_combo.findText("Türkçe")
        if tr_index >= 0:
            self.lang_combo.setCurrentIndex(tr_index)
        self.lang_combo.blockSignals(False)
    # ══════════════════════════════════════════════════════════════════
    #  Slot: Ses üretimi
    # ══════════════════════════════════════════════════════════════════

    def _on_generate(self) -> None:
        if self.engine is None or not self.engine.is_loaded:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir model yükleyin.")
            return

        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir metin girin.")
            return

        lang_name = self.lang_combo.currentText()
        if self._current_model_id == "kokoro":
            from tts.kokoro_engine import KOKORO_LANGUAGES
            language = KOKORO_LANGUAGES.get(lang_name, "en-us")
        else:
            language = SUPPORTED_LANGUAGES.get(lang_name, "tr")

        speaker_name: str | None  = None
        speaker_wav:  Path | None = None

        if self.radio_default.isChecked() and self.radio_default.isEnabled():
            speaker_name = self.speaker_combo.currentText() or None
        elif self.radio_clone.isChecked() and self.radio_clone.isEnabled():
            wav_data = self.voice_file_combo.currentData()
            if wav_data is None or not isinstance(wav_data, Path):
                QMessageBox.warning(
                    self, "Uyarı",
                    "Referans ses dosyası seçilmedi.\n"
                    "reference_voices/ klasörüne .wav dosyası ekleyin."
                )
                return
            speaker_wav = wav_data

        # Çıktı path'i
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.radio_clone.isChecked() and speaker_wav:
            voice_tag = f"ref_{speaker_wav.stem}"
        else:
            voice_tag = speaker_name.replace(" ", "_") if speaker_name else "unknown"

        output_path = FileManager.get_audio_output_path(
            f"xtts_{voice_tag}_{timestamp}.wav"
        )

        self._set_busy(True)
        self._log(
            f"⏳ Üretim başladı  ·  Dil: {lang_name}  ·  Çıktı: {output_path.name}",
            COLORS["accent_tts"],
        )

        use_chunked = len(text) > CHUNK_THRESHOLD

        if use_chunked:
            self._log(
                f"📦 Uzun metin ({len(text):,} karakter) → "
                f"otomatik bölme aktif (eşik: {CHUNK_THRESHOLD}).",
                COLORS["warning"],
            )
            self.chunked_worker = ChunkedTTSWorker(
                engine=self.engine,
                text=text,
                output_path=output_path,
                language=language,
                speaker_name=speaker_name,
                speaker_wav=speaker_wav,
                max_chars=CHUNK_THRESHOLD,
                silence_ms=400,
            )
            self.chunked_worker.progress.connect(
                lambda msg: self._log(f"  ↳ {msg}")
            )
            self.chunked_worker.chunk_done.connect(
                lambda done, total: self._log(f"  ✓ Parça {done}/{total} tamamlandı.")
            )
            self.chunked_worker.finished.connect(self._on_generation_finished)
            self.chunked_worker.error.connect(self._on_generation_error)
            self.chunked_worker.start()
        else:
            self.tts_worker = TTSWorker(
                engine=self.engine,
                text=text,
                output_path=output_path,
                language=language,
                speaker_name=speaker_name,
                speaker_wav=speaker_wav,
            )
            self.tts_worker.progress.connect(lambda msg: self._log(f"  ↳ {msg}"))
            self.tts_worker.finished.connect(self._on_generation_finished)
            self.tts_worker.error.connect(self._on_generation_error)
            self.tts_worker.start()

    def _on_generation_finished(self, file_path: str) -> None:
        self._set_busy(False)
        name = Path(file_path).name
        self._log(f"✅ Ses oluşturuldu: {name}", COLORS["success"])

        reply = QMessageBox.question(
            self,
            "Ses Üretildi",
            f"Dosya oluşturuldu:\n{file_path}\n\nÇıktı klasörünü açmak ister misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._open_audio_dir()

    def _on_generation_error(self, error_msg: str) -> None:
        self._set_busy(False)
        self._log(f"❌ Üretim Hatası: {error_msg}", COLORS["error"])
        QMessageBox.critical(self, "Ses Üretim Hatası", error_msg)

    # ══════════════════════════════════════════════════════════════════
    #  Metin değişim slot
    # ══════════════════════════════════════════════════════════════════

    def _on_text_changed(self) -> None:
        count = len(self.text_input.toPlainText())
        if count > CHUNK_THRESHOLD:
            self.char_count_lbl.setText(
                f"{count:,} karakter  "
                f"(otomatik bölme: ~{count // CHUNK_THRESHOLD + 1} parça)"
            )
            self.char_count_lbl.setStyleSheet(
                f"color: {COLORS['warning']};"
            )
        else:
            self.char_count_lbl.setText(f"{count} karakter")
            self.char_count_lbl.setStyleSheet(
                f"color: {COLORS['text_secondary']};"
            )

    # ══════════════════════════════════════════════════════════════════
    #  Klasör açma
    # ══════════════════════════════════════════════════════════════════

    def _open_audio_dir(self) -> None:
        self._open_folder(FileManager.get_audio_dir())

    def _open_reference_voices_dir(self) -> None:
        self._open_folder(FileManager.get_reference_voices_dir())

    @staticmethod
    def _open_folder(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.run(["explorer", str(path)], check=False)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)

    # ══════════════════════════════════════════════════════════════════
    #  Log yardımcıları
    # ══════════════════════════════════════════════════════════════════

    def _log(self, message: str, color: str = "") -> None:
        """Log alanına renkli mesaj ekler, otomatik kaydırır."""
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        from PyQt6.QtGui import QTextCharFormat
        fmt = QTextCharFormat()
        if color:
            fmt.setForeground(QColor(color))
        else:
            fmt.setForeground(QColor(COLORS["text_secondary"]))

        cursor.insertText(message + "\n", fmt)
        self.log_edit.setTextCursor(cursor)
        self.log_edit.ensureCursorVisible()

    # ══════════════════════════════════════════════════════════════════
    #  Busy durumu
    # ══════════════════════════════════════════════════════════════════

    def _set_busy(self, busy: bool) -> None:
        self.progress_bar.setVisible(busy)
        self.btn_generate.setEnabled(not busy and self.engine is not None
                                     and self.engine.is_loaded)
        self.btn_load_model.setEnabled(
            not busy
            and (self.engine is None or not self.engine.is_loaded)
        )
        self.model_combo.setEnabled(not busy)
        self.lang_combo.setEnabled(not busy)