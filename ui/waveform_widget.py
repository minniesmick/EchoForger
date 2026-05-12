"""
Ses dosyasının dalga formunu (waveform) gösteren widget.
pyqtgraph kullanır — matplotlib'den çok daha performanslı ve Qt-native.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


# pyqtgraph global tema ayarı — koyu arka plan
pg.setConfigOption("background", "#1E1E1E")
pg.setConfigOption("foreground", "#888888")
pg.setConfigOption("antialias", True)


class WaveformWidget(QWidget):
    """
    Bir ses dosyasının stereo/mono dalga formunu çizen widget.

    Kullanım:
        widget.load(path)   → dosyayı yükle ve çiz
        widget.clear()      → temizle, boş duruma dön
    """

    # Görsel sabitler
    WAVEFORM_COLOR     = "#6EE7B7"   # Accent mint
    WAVEFORM_COLOR_DIM = "#1E5C48"   # Dolu alan rengi (fill)
    MAX_SAMPLES        = 200_000     # Performans için downsample eşiği

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    # ── Arayüz kurulumu ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Dosya bilgisi etiketi
        self.info_lbl = QLabel("")
        self.info_lbl.setObjectName("status_label")
        self.info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_lbl)

        # pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setFixedHeight(110)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideButtons()
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)

        # Eksenleri gizle
        self.plot_widget.getAxis("left").hide()
        self.plot_widget.getAxis("bottom").hide()

        # Çerçeve
        self.plot_widget.setStyleSheet(
            "border: 1px solid #2C2C2C; border-radius: 8px;"
        )

        layout.addWidget(self.plot_widget)

        # Boş durum etiketi (dosya yüklenmeden önce gösterilir)
        self.empty_lbl = QLabel("Dalga formu burada görünecek")
        self.empty_lbl.setObjectName("status_label")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #555555; padding: 8px;")
        layout.addWidget(self.empty_lbl)

        self._show_empty(True)

    # ── Genel arayüz ─────────────────────────────────────────────────

    def load(self, path: Path) -> None:
        """Ses dosyasını okur ve dalga formunu çizer."""
        try:
            samples, sample_rate = sf.read(str(path), always_2d=True, dtype="float32")
        except Exception:  # noqa: BLE001
            self.clear()
            self.info_lbl.setText("⚠️  Dalga formu okunamadı")
            return

        # Mono'ya indir (stereo → ortalama)
        mono = samples.mean(axis=1)

        # Downsample — çok uzun dosyalarda pyqtgraph yavaşlar
        mono = self._downsample(mono, self.MAX_SAMPLES)

        duration_s  = len(samples) / sample_rate
        channel_txt = "Stereo" if samples.shape[1] == 2 else "Mono"
        self.info_lbl.setText(
            f"{path.name}  ·  {duration_s:.1f}s  ·  "
            f"{sample_rate // 1000}kHz  ·  {channel_txt}"
        )

        self._draw(mono)
        self._show_empty(False)

    def clear(self) -> None:
        """Widget'ı boş duruma getirir."""
        self.plot_widget.clear()
        self.info_lbl.setText("")
        self._show_empty(True)

    # ── Çizim ────────────────────────────────────────────────────────

    def _draw(self, mono: np.ndarray) -> None:
        """Verilen mono numpy dizisini çizer."""
        self.plot_widget.clear()

        x = np.arange(len(mono), dtype=np.float32)

        # Dolu alan (fill between 0 ve dalga formu)
        fill = pg.FillBetweenItem(
            pg.PlotDataItem(x, mono,  pen=None),
            pg.PlotDataItem(x, np.zeros_like(mono), pen=None),
            brush=pg.mkBrush(self.WAVEFORM_COLOR_DIM),
        )
        self.plot_widget.addItem(fill)

        # Ana çizgi
        pen = pg.mkPen(color=self.WAVEFORM_COLOR, width=1)
        self.plot_widget.plot(x, mono, pen=pen)

        # Y eksenini simetrik yap
        peak = float(np.abs(mono).max()) or 1.0
        self.plot_widget.setYRange(-peak, peak, padding=0.05)
        self.plot_widget.setXRange(0, len(mono), padding=0)

    # ── Yardımcılar ───────────────────────────────────────────────────

    @staticmethod
    def _downsample(data: np.ndarray, max_samples: int) -> np.ndarray:
        """
        Performans için veriyi max_samples altına indirir.
        Her bloktaki min/max çiftini alır — tepe noktaları kaybolmaz.
        """
        if len(data) <= max_samples:
            return data

        block = len(data) // (max_samples // 2)
        trimmed = data[: (len(data) // block) * block]
        blocks = trimmed.reshape(-1, block)

        mins = blocks.min(axis=1)
        maxs = blocks.max(axis=1)

        # min/max çiftlerini sırayla birleştir
        interleaved = np.empty(len(mins) * 2, dtype=data.dtype)
        interleaved[0::2] = mins
        interleaved[1::2] = maxs
        return interleaved
    # ── Yardımcılar ───────────────────────────────────────────────────

    def _show_empty(self, is_empty: bool) -> None:
        """
        Görünürlüğü dosya varlığına göre değiştirir.
        is_empty=True  -> 'Dalga formu burada görünecek' yazar, grafik gizlenir.
        is_empty=False -> Grafik gösterilir, yazı gizlenir.
        """
        self.empty_lbl.setVisible(is_empty)
        self.plot_widget.setVisible(not is_empty)
        # Dosya bilgisi etiketi de sadece dosya varken anlamlı
        if is_empty:
            self.info_lbl.hide()
        else:
            self.info_lbl.show()