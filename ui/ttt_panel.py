# ui/ttt_panel.py
"""
EchoForge — Metin → Metin (TTT) Paneli.
Ollama üzerinden LLM ile metin işleme, çeviri ve serbest mod.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSlot, QThread
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton, QComboBox,
    QGroupBox, QScrollArea, QFrame, QSizePolicy,
)

from core.ollama_client import (
    ModelFetchWorker, ModelSwitchWorker, GenerateWorker,
)
from ui.styles import COLORS

# ── Hızlı işlem tanımları ─────────────────────────────────────────────────────
QUICK_ACTIONS: list[dict] = [
    {
        "label":  "✅ Yazım Kontrol",
        "prompt": (
            "Aşağıdaki metni incele. Yazım, noktalama ve gramer hatalarını düzelt. "
            "Eğer hata yoksa metni olduğu gibi döndür, hiçbir ek açıklama yapma.\n\nMetin:\n{text}"
        ),
    },
    {
        "label":  "📝 Özetle",
        "prompt": "Aşağıdaki metni kısa ve öz şekilde özetle:\n\n{text}",
    },
    {
        "label":  "🔤 Biçimlendir",
        "prompt": (
            "Aşağıdaki metni düzgün paragraflar ve cümleler halinde yeniden biçimlendir. "
            "İçeriği değiştirme:\n\n{text}"
        ),
    },
]

TRANSLATION_LANGUAGES: list[str] = [
    "Türkçe", "İngilizce", "Almanca", "Fransızca",
    "İspanyolca", "İtalyanca", "Portekizce", "Rusça",
    "Arapça", "Japonca", "Çince", "Korece",
    "Hollandaca", "Lehçe", "İsveççe", "Norveççe",
]


class TTTPanel(QWidget):
    """
    Metin → Metin paneli.

    Dışarıdan metin almak için:
        panel.receive_text(text: str)
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._current_model: str | None  = None
        self._fetch_worker:  ModelFetchWorker  | None = None
        self._switch_worker: ModelSwitchWorker | None = None
        self._gen_worker:    GenerateWorker    | None = None

        self._setup_ui()

    # ══════════════════════════════════════════════════════════════════
    #  UI Kurulum
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_model_bar())

        # Log şeridi (model yükleme mesajları)
        self.log_lbl = QLabel("")
        self.log_lbl.setObjectName("status_label")
        self.log_lbl.setContentsMargins(16, 4, 16, 4)
        self.log_lbl.setStyleSheet(f"color: {COLORS['accent_tts']}; font-size: 12px;")
        root.addWidget(self.log_lbl)

        # Ana içerik
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 16)
        content_layout.setSpacing(12)

        # Metin alanları
        content_layout.addWidget(self._build_text_area(), stretch=1)

        # Hızlı işlemler
        content_layout.addWidget(self._build_quick_actions())

        # Serbest mod
        content_layout.addWidget(self._build_free_mode())

        root.addWidget(content, stretch=1)

    # ── Model çubuğu ──────────────────────────────────────────────────

    def _build_model_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(
            f"background-color: {COLORS['bg_secondary']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        lbl = QLabel("Model:")
        lbl.setObjectName("status_label")
        layout.addWidget(lbl)

        backend_lbl = QLabel("Motor:")
        backend_lbl.setObjectName("status_label")
        layout.addWidget(backend_lbl)

        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["Ollama", "Gemini"])
        self.backend_combo.currentTextChanged.connect(self._on_backend_changed)
        layout.addWidget(self.backend_combo)

        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(220)
        self.model_combo.setPlaceholderText("— model listesi yükleniyor —")
        self.model_combo.currentTextChanged.connect(self._on_model_combo_changed)
        layout.addWidget(self.model_combo)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setFixedWidth(36)
        self.btn_refresh.setToolTip("Model listesini yenile")
        self.btn_refresh.clicked.connect(self._fetch_models)
        layout.addWidget(self.btn_refresh)

        self.btn_load = QPushButton("⚡  Modeli Yükle")
        self.btn_load.setObjectName("btn_primary")
        self.btn_load.setMinimumWidth(140)
        self.btn_load.setEnabled(False)
        self.btn_load.clicked.connect(self._on_load_model)
        layout.addWidget(self.btn_load)

        layout.addStretch()

        self.status_lbl = QLabel("● Bağlı değil")
        self.status_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # Başlangıçta modelleri çek
        self._fetch_models()

        return bar

    def _on_backend_changed(self, backend: str) -> None:
        self._current_model = None
        self.btn_load.setEnabled(True)
        self.btn_load.setText("⚡  Modeli Yükle")
        self.btn_send.setEnabled(False)
        self.status_lbl.setText("● Bağlı değil")
        self.status_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 12px;"
        )
        self._fetch_models()

    def _get_backend(self) -> str:
        return self.backend_combo.currentText().lower()  # "ollama" | "gemini"

    # ── Metin alanları ────────────────────────────────────────────────

    def _build_text_area(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Sol — giriş
        left = QGroupBox("GİRİŞ METNİ")
        ll   = QVBoxLayout(left)
        ll.setContentsMargins(8, 8, 8, 8)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText(
            "İşlenecek metni buraya yazın ya da\n"
            "Transkripsiyon / TTS panelinden pipeline ile gönderin."
        )
        ll.addWidget(self.input_edit)

        btn_clear = QPushButton("🗑  Temizle")
        btn_clear.clicked.connect(self.input_edit.clear)
        ll.addWidget(btn_clear)

        splitter.addWidget(left)

        # Sağ — çıktı
        right = QGroupBox("ÇIKTI")
        rl    = QVBoxLayout(right)
        rl.setContentsMargins(8, 8, 8, 8)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Sonuç burada akış olarak görünecek…")
        rl.addWidget(self.output_edit)

        btn_row = QHBoxLayout()
        btn_copy = QPushButton("⎘  Kopyala")
        btn_copy.clicked.connect(self._copy_output)
        btn_row.addWidget(btn_copy)

        btn_to_input = QPushButton("→ Girişe Taşı")
        btn_to_input.setToolTip("Çıktıyı giriş alanına kopyalar (zincirleme işlem)")
        btn_to_input.clicked.connect(self._output_to_input)
        btn_row.addWidget(btn_to_input)

        rl.addLayout(btn_row)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        return splitter

    # ── Hızlı işlemler ────────────────────────────────────────────────

    def _build_quick_actions(self) -> QGroupBox:
        group = QGroupBox("HIZLI İŞLEMLER")
        outer = QVBoxLayout(group)
        outer.setContentsMargins(12, 8, 12, 8)
        outer.setSpacing(8)

        # ── Sabit aksiyonlar ──
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        for action in QUICK_ACTIONS:
            btn = QPushButton(action["label"])
            btn.setProperty("prompt_template", action["prompt"])
            btn.clicked.connect(
                lambda checked, a=action: self._run_quick(a["prompt"])
            )
            action_row.addWidget(btn)

        action_row.addStretch()

        self.btn_stop = QPushButton("■  Durdur")
        self.btn_stop.setObjectName("danger_btn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_generation)
        action_row.addWidget(self.btn_stop)
        outer.addLayout(action_row)

        # ── Çeviri satırı ──
        trans_row = QHBoxLayout()
        trans_row.setSpacing(8)

        trans_lbl = QLabel("🌐 Çeviri hedefi:")
        trans_lbl.setObjectName("status_label")
        trans_row.addWidget(trans_lbl)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(TRANSLATION_LANGUAGES)
        self.lang_combo.setMinimumWidth(140)
        trans_row.addWidget(self.lang_combo)

        btn_translate = QPushButton("🌐  Çevir")
        btn_translate.setProperty("prompt_template", "translate")
        btn_translate.clicked.connect(self._run_translate)
        trans_row.addWidget(btn_translate)

        trans_row.addStretch()

        # ── Süre göstergesi ──
        self.timing_lbl = QLabel("")
        self.timing_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 11px;"
        )
        trans_row.addWidget(self.timing_lbl)

        outer.addLayout(trans_row)
        return group


    def _run_translate(self) -> None:
        text = self.input_edit.toPlainText().strip()
        if not text:
            self._log("⚠️ Giriş metni boş.", error=True)
            return
        hedef = self.lang_combo.currentText()
        prompt = (
            f"Aşağıdaki metni {hedef} diline çevir. "
            f"Sadece çeviriyi yaz, açıklama ekleme:\n\n{text}"
        )
        self._start_generation(prompt)

    # ── Serbest mod ───────────────────────────────────────────────────

    def _build_free_mode(self) -> QGroupBox:
        group = QGroupBox("SERBEST MOD")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.free_input = QTextEdit()
        self.free_input.setFixedHeight(64)
        self.free_input.setPlaceholderText(
            "Prompt girin… {text} yazdığınız yere giriş metni otomatik eklenir.\n"
            "Örnek: '{text}' metnini daha resmi bir dile çevir."
        )
        layout.addWidget(self.free_input, stretch=1)

        self.btn_send = QPushButton("▶  Gönder")
        self.btn_send.setObjectName("btn_primary")
        self.btn_send.setFixedWidth(110)
        self.btn_send.setEnabled(False)
        self.btn_send.clicked.connect(self._run_free)
        layout.addWidget(self.btn_send)

        return group

    # ══════════════════════════════════════════════════════════════════
    #  Model işlemleri
    # ══════════════════════════════════════════════════════════════════

    def _fetch_models(self) -> None:
        self.btn_refresh.setEnabled(False)
        self.model_combo.setEnabled(False)
        if self._get_backend() == "gemini":
            from core.gemini_client import ModelFetchWorker as GeminiFetch
            self._fetch_worker = GeminiFetch()
        else:
            from core.ollama_client import ModelFetchWorker
            self._fetch_worker = ModelFetchWorker()
        self._fetch_worker.finished.connect(self._on_models_fetched)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    @pyqtSlot(list)
    def _on_models_fetched(self, models: list) -> None:
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(models)

        # aya-expanse'i varsayılan seç
        for i, m in enumerate(models):
            if "aya" in m.lower():
                self.model_combo.setCurrentIndex(i)
                break

        self.model_combo.blockSignals(False)
        self.model_combo.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self.btn_load.setEnabled(True)
        self._log(f"{len(models)} model bulundu.")

    @pyqtSlot(str)
    def _on_fetch_error(self, msg: str) -> None:
        self.btn_refresh.setEnabled(True)
        self.model_combo.setEnabled(True)
        self._log(f"❌ {msg}", error=True)
        self.status_lbl.setText("● Ollama bağlantısı yok")
        self.status_lbl.setStyleSheet(f"color: {COLORS['error']}; font-size: 12px;")

    def _on_model_combo_changed(self, _: str) -> None:
        # Seçim değişince load butonu tekrar aktif
        self.btn_load.setEnabled(True)
        self.btn_load.setText("⚡  Modeli Yükle")

    def _on_load_model(self) -> None:
        new_model = self.model_combo.currentText()
        if not new_model:
            return

        self._set_busy(True)
        if self._get_backend() == "gemini":
            from core.gemini_client import ModelSwitchWorker as GeminiSwitch
            self._switch_worker = GeminiSwitch(self._current_model, new_model)
        else:
            from core.ollama_client import ModelSwitchWorker
            self._switch_worker = ModelSwitchWorker(self._current_model, new_model)
        self._switch_worker.progress.connect(self._log)
        self._switch_worker.finished.connect(
            lambda: self._on_model_ready(new_model)
        )
        self._switch_worker.error.connect(self._on_switch_error)
        self._switch_worker.start()

    def _on_model_ready(self, model_name: str) -> None:
        self._current_model = model_name
        self._set_busy(False)
        self.btn_load.setText("✓  Yüklendi")
        self.btn_load.setEnabled(False)
        self.btn_send.setEnabled(True)
        self.status_lbl.setText(f"● {model_name}")
        self.status_lbl.setStyleSheet(
            f"color: {COLORS['success']}; font-size: 12px;"
        )

    def _on_switch_error(self, msg: str) -> None:
        self._set_busy(False)
        self._log(f"❌ {msg}", error=True)

    # ══════════════════════════════════════════════════════════════════
    #  Üretim
    # ══════════════════════════════════════════════════════════════════

    def _run_quick(self, template: str) -> None:
        text = self.input_edit.toPlainText().strip()
        if not text:
            self._log("⚠️ Giriş metni boş.", error=True)
            return
        prompt = template.format(text=text)
        self._start_generation(prompt)

    def _run_free(self) -> None:
        template = self.free_input.toPlainText().strip()
        if not template:
            return
        text   = self.input_edit.toPlainText().strip()
        prompt = template.replace("{text}", text) if "{text}" in template else \
                 f"{template}\n\n{text}" if text else template
        self._start_generation(prompt)

    def _start_generation(self, prompt: str) -> None:
        if not self._current_model:
            self._log("⚠️ Önce bir model yükleyin.", error=True)
            return

        self.output_edit.clear()
        self._set_generating(True)

        self.timing_lbl.setText("⏱ Bekleniyor…")
        if self._get_backend() == "gemini":
            from core.gemini_client import GenerateWorker as GeminiGen
            self._gen_worker = GeminiGen(self._current_model, prompt)
        else:
            from core.ollama_client import GenerateWorker
            self._gen_worker = GenerateWorker(self._current_model, prompt)
        self._gen_worker.token.connect(self._on_token)
        self._gen_worker.first_token.connect(self._on_first_token)
        self._gen_worker.finished.connect(self._on_generation_done)
        self._gen_worker.error.connect(self._on_generation_error)
        self._gen_worker.start()

    @pyqtSlot(float)
    def _on_first_token(self, delay: float) -> None:
        """İlk token geldiğinde süreyi göster."""
        self.timing_lbl.setText(f"⏱ İlk token: {delay:.2f} sn")

    @pyqtSlot(str)
    def _on_token(self, token: str) -> None:
        cursor = self.output_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS["text_primary"]))
        cursor.insertText(token, fmt)
        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    @pyqtSlot(str)
    def _on_generation_done(self, _: str) -> None:
        self._set_generating(False)
        self._log("✅ Tamamlandı.")

    @pyqtSlot(str)
    def _on_generation_error(self, msg: str) -> None:
        self._set_generating(False)
        self._log(f"❌ {msg}", error=True)

    def _stop_generation(self) -> None:
        if self._gen_worker:
            self._gen_worker.cancel()
        self._set_generating(False)
        self._log("⛔ Durduruldu.")

    # ══════════════════════════════════════════════════════════════════
    #  Pipeline slot
    # ══════════════════════════════════════════════════════════════════

    @pyqtSlot(str)
    def receive_text(self, text: str) -> None:
        """TranscriptionPanel veya dışarıdan metin alır."""
        self.input_edit.setPlainText(text)
        self._log("📋 Metin giriş alanına aktarıldı.")

    # ══════════════════════════════════════════════════════════════════
    #  Yardımcılar
    # ══════════════════════════════════════════════════════════════════

    def _copy_output(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.output_edit.toPlainText())
        self._log("📋 Çıktı kopyalandı.")

    def _output_to_input(self) -> None:
        text = self.output_edit.toPlainText().strip()
        if text:
            self.input_edit.setPlainText(text)
            self.output_edit.clear()

    def _log(self, msg: str, error: bool = False) -> None:
        color = COLORS["error"] if error else COLORS["accent_tts"]
        self.log_lbl.setStyleSheet(f"color: {color}; font-size: 12px; padding: 0 16px;")
        self.log_lbl.setText(msg)

    def _set_busy(self, busy: bool) -> None:
        self.model_combo.setEnabled(not busy)
        self.btn_refresh.setEnabled(not busy)
        self.btn_load.setEnabled(not busy)

    def _set_generating(self, generating: bool) -> None:
        self.btn_stop.setEnabled(generating)
        self.btn_send.setEnabled(not generating and self._current_model is not None)
        for btn in self.findChildren(QPushButton):
            if btn.property("prompt_template") is not None:
                btn.setEnabled(not generating)
