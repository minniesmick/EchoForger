# ui/welcome_panel.py
"""
EchoForge — Karşılama / Mod Seçim Ekranı.

Uygulama açılışında gösterilir.
Kullanıcı bir mod seçtiğinde mode_selected(str) sinyali yayınlanır.
MainWindow bu sinyali dinleyerek ilgili sekmeye geçer.

Modlar:
    "stt"  — Ses → Metin
    "tts"  — Metin → Ses
    "ttt"  — Metin → Metin (Çeviri / Düzenleme)
    "sts"  — Ses → Ses (Farklı sesle aynı içerik)
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
)

from ui.styles import COLORS


class ModeCard(QWidget):
    """Tek bir mod kartı."""

    clicked = pyqtSignal(str)   # mode_id

    def __init__(
        self,
        mode_id: str,
        icon: str,
        title: str,
        description: str,
        accent: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.mode_id = mode_id
        self._accent = accent
        self._setup_ui(icon, title, description, accent)

    def _setup_ui(self, icon, title, description, accent) -> None:
        self.setFixedSize(220, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 38px; background: transparent;")
        layout.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(
            f"font-size: 15px; font-weight: 700; "
            f"color: {accent}; background: transparent;"
        )
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            f"font-size: 11px; color: {COLORS['text_secondary']}; "
            f"background: transparent;"
        )
        layout.addWidget(desc_lbl)

        self._apply_style(False)

    def _apply_style(self, hovered: bool) -> None:
        bg = COLORS['bg_hover'] if hovered else COLORS['bg_card']
        self.setStyleSheet(
            f"""
            ModeCard {{
                background-color: {bg};
                border: 1px solid {self._accent if hovered else COLORS['border']};
                border-radius: 14px;
            }}
            """
        )

    def enterEvent(self, event) -> None:
        self._apply_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._apply_style(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.mode_id)
        super().mousePressEvent(event)


class WelcomePanel(QWidget):
    """
    Açılış ekranı — 4 mod kartı gösterir.

    Sinyaller:
        mode_selected(str): "stt" | "tts" | "ttt" | "sts"
    """

    mode_selected = pyqtSignal(str)

    MODES = [
        {
            "id":          "stt",
            "icon":        "🎙️",
            "title":       "Ses → Metin",
            "description": "Ses dosyasını yazıya dönüştür\n(Whisper)",
            "accent":      COLORS["accent_stt"],
        },
        {
            "id":          "tts",
            "icon":        "🔊",
            "title":       "Metin → Ses",
            "description": "Metni doğal sesle seslendirin\n(XTTSv2)",
            "accent":      COLORS["accent_tts"],
        },
        {
            "id":          "ttt",
            "icon":        "✏️",
            "title":       "Metin → Metin",
            "description": "Çeviri veya metin düzenleme\n(Ollama)",
            "accent":      COLORS["warning"],
        },
        {
            "id":          "sts",
            "icon":        "🔄",
            "title":       "Ses → Ses",
            "description": "Farklı sesle aynı içerik\n(STT + TTS pipeline)",
            "accent":      "#C084FC",
        },
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # İç konteyner
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(40)
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Başlık
        title = QLabel("Ne yapmak istiyorsunuz?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 26px; font-weight: 700; "
            f"color: {COLORS['text_primary']}; letter-spacing: 1px;"
        )
        inner_layout.addWidget(title)

        sub = QLabel("Bir mod seçin — dilediğiniz zaman sekmelerden değiştirebilirsiniz.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            f"font-size: 13px; color: {COLORS['text_secondary']};"
        )
        inner_layout.addWidget(sub)

        # Kart satırı
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)
        cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for mode in self.MODES:
            card = ModeCard(
                mode_id=mode["id"],
                icon=mode["icon"],
                title=mode["title"],
                description=mode["description"],
                accent=mode["accent"],
            )
            card.clicked.connect(self.mode_selected.emit)
            cards_row.addWidget(card)

        inner_layout.addLayout(cards_row)
        layout.addWidget(inner)
