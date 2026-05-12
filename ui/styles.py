# ui/styles.py
"""
EchoForge — Birleşik tema.
Whisper GUI (teal / monospace) + Voice Forge (purple / sans-serif) kombinasyonu.

Accent renkleri:
    accent_stt  →  #6EE7B7  (mint teal)   — transkripsiyon / STT
    accent_tts  →  #6C63FF  (indigo)      — ses üretimi   / TTS
    accent      →  accent_stt             — genel varsayılan

Widget kapsamı:
    Whisper GUI: QListWidget, QTableWidget, QCheckBox, QFrame#left_panel
    Voice Forge: QGroupBox, QRadioButton, QPushButton#btn_primary
    Ortak:       QPushButton, QComboBox, QTextEdit, QProgressBar,
                 QScrollBar, QSplitter, QTabWidget, QToolTip, QLabel
"""

COLORS: dict[str, str] = {
    # ── Arka planlar ──────────────────────────────────────────────────
    "bg_primary":     "#0D0D0D",   # En derin arka plan
    "bg_secondary":   "#141414",   # Panel / sidebar
    "bg_tertiary":    "#1A1A1A",   # Input / card arka planı
    "bg_card":        "#1E1E1E",   # Widget kartları
    "bg_hover":       "#262626",   # Hover durumu

    # ── Metin ─────────────────────────────────────────────────────────
    "text_primary":   "#F0F0F0",
    "text_secondary": "#888888",
    "text_muted":     "#484848",

    # ── Kenarlık ──────────────────────────────────────────────────────
    "border":         "#242424",
    "border_focus":   "#6C63FF",   # Focus'ta TTS moru

    # ── STT aksanı (Transkripsiyon) ───────────────────────────────────
    "accent_stt":     "#6EE7B7",   # Mint teal
    "accent_stt_dim": "#34D399",   # Koyu teal
    "accent_stt_glow":"rgba(110,231,183,0.12)",

    # ── TTS aksanı (Ses Üretimi) ──────────────────────────────────────
    "accent_tts":     "#6C63FF",   # İndigo / mor
    "accent_tts_hover":"#8078FF",
    "accent_tts_dim": "#3D3875",
    "accent_tts_glow":"rgba(108,99,255,0.12)",

    # ── Genel aksant (varsayılan = STT teal) ─────────────────────────
    "accent":         "#6EE7B7",
    "accent_dim":     "#34D399",
    "accent_glow":    "rgba(110,231,183,0.12)",

    # ── Durum renkleri ────────────────────────────────────────────────
    "success":        "#6EE7B7",
    "warning":        "#FCD34D",
    "error":          "#F87171",
}

MAIN_STYLESHEET = f"""

/* ══════════════════════════════════════════════════
   TEMEL
══════════════════════════════════════════════════ */

QMainWindow, QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
    font-size: 13px;
}}

/* ══════════════════════════════════════════════════
   BAŞLIK / ETİKETLER
══════════════════════════════════════════════════ */

QLabel#app_title {{
    font-size: 20px;
    font-weight: 700;
    color: {COLORS['accent_stt']};
    letter-spacing: 3px;
}}

QLabel#app_subtitle {{
    font-size: 11px;
    color: {COLORS['text_muted']};
    letter-spacing: 1px;
}}

QLabel#subtitle {{
    font-size: 11px;
    color: {COLORS['text_muted']};
    letter-spacing: 1px;
}}

QLabel#section_label {{
    color: {COLORS['text_muted']};
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 600;
}}

QLabel#status_label {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    padding: 2px 0;
}}

/* ══════════════════════════════════════════════════
   SOL PANEL (FilePanel)
══════════════════════════════════════════════════ */

QFrame#left_panel {{
    background-color: {COLORS['bg_secondary']};
    border-right: 1px solid {COLORS['border']};
}}

/* ══════════════════════════════════════════════════
   DOSYA LİSTESİ
══════════════════════════════════════════════════ */

QListWidget {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 9px 12px;
    border-radius: 6px;
    color: {COLORS['text_secondary']};
    margin: 1px 0;
    font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent_stt_glow']};
    color: {COLORS['accent_stt']};
    border: 1px solid {COLORS['accent_stt_dim']};
}}

/* ══════════════════════════════════════════════════
   BUTONLAR
══════════════════════════════════════════════════ */

QPushButton {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['text_muted']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_primary']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border']};
}}

/* STT birincil buton — teal */
QPushButton#primary_btn,
QPushButton#stt_primary_btn {{
    background-color: {COLORS['accent_stt']};
    color: #0D0D0D;
    border: none;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QPushButton#primary_btn:hover,
QPushButton#stt_primary_btn:hover {{
    background-color: {COLORS['accent_stt_dim']};
}}

QPushButton#primary_btn:disabled,
QPushButton#stt_primary_btn:disabled {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_muted']};
}}

/* TTS birincil buton — mor */
QPushButton#btn_primary,
QPushButton#tts_primary_btn {{
    background-color: {COLORS['accent_tts']};
    color: white;
    border: none;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
}}

QPushButton#btn_primary:hover,
QPushButton#tts_primary_btn:hover {{
    background-color: {COLORS['accent_tts_hover']};
}}

QPushButton#btn_primary:disabled,
QPushButton#tts_primary_btn:disabled {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_muted']};
}}

/* Pipeline köprü butonu (Transkript → TTS) */
QPushButton#pipeline_btn {{
    background-color: {COLORS['accent_tts_dim']};
    color: {COLORS['accent_tts_hover']};
    border: 1px solid {COLORS['accent_tts']};
    font-weight: 600;
    border-radius: 8px;
}}

QPushButton#pipeline_btn:hover {{
    background-color: {COLORS['accent_tts_glow']};
    color: white;
    border-color: {COLORS['accent_tts_hover']};
}}

QPushButton#pipeline_btn:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border']};
}}

/* Tehlike butonu */
QPushButton#danger_btn {{
    color: {COLORS['error']};
    border-color: {COLORS['error']};
    background-color: transparent;
}}

QPushButton#danger_btn:hover {{
    background-color: rgba(248,113,113,0.10);
}}

QPushButton#danger_btn:disabled {{
    color: {COLORS['text_muted']};
    border-color: {COLORS['border']};
}}

/* ══════════════════════════════════════════════════
   METİN ALANLARI
══════════════════════════════════════════════════ */

QTextEdit {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: {COLORS['accent_stt_glow']};
}}

QTextEdit:focus {{
    border-color: {COLORS['accent_tts']};
}}

/* TTS metin giriş alanı — biraz daha geniş */
QTextEdit#tts_text_input {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    border-color: {COLORS['border']};
    line-height: 1.7;
}}

QTextEdit#tts_text_input:focus {{
    border-color: {COLORS['accent_tts']};
}}

/* ══════════════════════════════════════════════════
   COMBO BOX
══════════════════════════════════════════════════ */

QComboBox {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1.5px solid {COLORS['border']};
    border-radius: 7px;
    padding: 7px 12px;
    font-size: 13px;
    min-height: 32px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent_tts']};
}}

QComboBox:focus {{
    border-color: {COLORS['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
    width: 24px;
}}

QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 7px;
    selection-background-color: {COLORS['bg_hover']};
    padding: 4px;
    outline: none;
}}

/* ══════════════════════════════════════════════════
   RADIO BUTTON  (Voice Forge'dan)
══════════════════════════════════════════════════ */

QRadioButton {{
    color: {COLORS['text_primary']};
    spacing: 8px;
    font-size: 13px;
    padding: 4px 0;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_tertiary']};
}}

QRadioButton::indicator:checked {{
    border-color: {COLORS['accent_tts']};
    background-color: {COLORS['accent_tts']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['accent_tts_hover']};
}}

QRadioButton:disabled {{
    color: {COLORS['text_muted']};
}}

/* ══════════════════════════════════════════════════
   GROUP BOX  (Voice Forge'dan)
══════════════════════════════════════════════════ */

QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    margin-top: 18px;
    padding: 14px 10px 10px 10px;
    font-size: 11px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
    letter-spacing: 1px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    top: 2px;
    color: {COLORS['accent_tts']};
}}

/* ══════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════ */

QProgressBar {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    height: 4px;
    text-align: center;
    font-size: 0px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent_stt']};
    border-radius: 4px;
}}

QProgressBar#tts_progress::chunk {{
    background-color: {COLORS['accent_tts']};
}}

/* ══════════════════════════════════════════════════
   SEKME (QTabWidget)
══════════════════════════════════════════════════ */

QTabWidget::pane {{
    border: none;
    background-color: {COLORS['bg_primary']};
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 28px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.5px;
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_hover']};
}}

/* STT sekmesi — teal */
QTabBar::tab:selected#tab_stt {{
    color: {COLORS['accent_stt']};
    border-bottom: 2px solid {COLORS['accent_stt']};
    background-color: {COLORS['bg_primary']};
}}

/* Genel seçili sekme — teal (varsayılan) */
QTabBar::tab:selected {{
    color: {COLORS['accent_stt']};
    border-bottom: 2px solid {COLORS['accent_stt']};
    background-color: {COLORS['bg_primary']};
}}

/* ══════════════════════════════════════════════════
   TABLO (QueuePanel)
══════════════════════════════════════════════════ */

QTableWidget {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    outline: none;
    font-family: 'SF Mono', 'JetBrains Mono', Consolas, monospace;
    font-size: 12px;
}}

QTableWidget::item {{
    padding: 8px 12px;
    color: {COLORS['text_secondary']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['accent_stt_glow']};
    color: {COLORS['text_primary']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border: none;
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px 12px;
    font-size: 10px;
    letter-spacing: 1.5px;
    font-weight: 600;
}}

/* ══════════════════════════════════════════════════
   CHECKBOX
══════════════════════════════════════════════════ */

QCheckBox {{
    color: {COLORS['text_secondary']};
    spacing: 6px;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    background-color: {COLORS['bg_card']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_stt']};
    border-color: {COLORS['accent_stt']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent_stt_dim']};
}}

/* ══════════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['bg_hover']};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_muted']};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 6px;
    border-radius: 3px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['bg_hover']};
    border-radius: 3px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['text_muted']};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ══════════════════════════════════════════════════
   SPLITTER
══════════════════════════════════════════════════ */

QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* ══════════════════════════════════════════════════
   STATUS BAR
══════════════════════════════════════════════════ */

QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
    font-size: 12px;
    padding: 2px 8px;
}}

/* ══════════════════════════════════════════════════
   TOOLTIP
══════════════════════════════════════════════════ */

QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ══════════════════════════════════════════════════
   MENU (Kopyala/Kaydet dropdown'ları)
══════════════════════════════════════════════════ */

QMenu {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 20px;
    border-radius: 5px;
}}

QMenu::item:selected {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QMenu::separator {{
    height: 1px;
    background: {COLORS['border']};
    margin: 4px 10px;
}}

/* ══════════════════════════════════════════════════
   MESSAGE BOX
══════════════════════════════════════════════════ */

QMessageBox {{
    background-color: {COLORS['bg_card']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
    font-size: 13px;
}}

"""