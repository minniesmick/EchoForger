# main.py
"""
EchoForge — Giriş noktası.

Başlatma sırası:
    1. Qt uygulaması oluştur (High-DPI + platform ayarları)
    2. App meta-verilerini set et
    3. Ana pencereyi aç
    4. Olay döngüsünü başlat

Hata yakalama:
    Beklenmeyen istisnalar QMessageBox ile gösterilir,
    raw traceback'i kullanıcıya açık etmez.
"""
from __future__ import annotations

import sys
import traceback

from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication, QMessageBox


# ── Qt uygulama örneği — widget'lardan önce oluşturulmalı ─────────────────────
def _create_app() -> QApplication:
    # High-DPI: Qt6'da varsayılan açık, ancak Windows'ta bazen elle tetiklenir
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("EchoForge")
    app.setApplicationDisplayName("EchoForge")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EchoForge")

    return app


def _show_fatal_error(exc: BaseException) -> None:
    """İlk pencere açılmadan çöküşlerde basit bir hata kutusu gösterir."""
    msg = QMessageBox()
    msg.setWindowTitle("EchoForge — Başlatma Hatası")
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("Uygulama başlatılırken beklenmeyen bir hata oluştu.")
    msg.setDetailedText(traceback.format_exc())
    msg.exec()


def main() -> int:
    app = _create_app()

    try:
        from ui.main_window import MainWindow   # geç import — Qt hazır olduktan sonra
        window = MainWindow()
        window.show()
    except Exception:                           # noqa: BLE001
        _show_fatal_error(sys.exc_info()[1])
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())