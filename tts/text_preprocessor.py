"""
text_preprocessor.py
====================
Metin ön işleme ve uzun metin bölme (chunking) modülü.

Sorun:
    XTTSv2 ve Fish Speech ~400–600 token üzerindeki metinlerde ses kalitesi
    düşürür; bazı cümleleri atlar veya bozuk çıktı üretir.

Çözüm:
    Metni cümle sınırlarından küçük parçalara böl → her parçayı ayrı üret
    → pydub ile parçalar arasına kısa sessizlik ekleyerek birleştir.

Kullanım (doğrudan):
    from text_preprocessor import TextPreprocessor

    pre = TextPreprocessor(max_chars=250, silence_ms=400)
    chunks = pre.split("Çok uzun metin...")   # → ['parça1', 'parça2', ...]

    final = pre.merge_audio_files(
        chunk_paths=[Path("c1.wav"), Path("c2.wav")],
        output_path=Path("output/final.wav"),
    )

Bağımlılıklar:
    pip install pydub
    # pydub ses birleştirme için ffmpeg gerektirir:
    # https://ffmpeg.org/download.html  → PATH'e ekleyin
"""

import re
from pathlib import Path


class TextPreprocessor:
    """
    Uzun metinleri TTS dostu parçalara böler ve ses parçalarını birleştirir.

    Args:
        max_chars:  Her parçanın maksimum karakter sayısı (varsayılan: 250).
                    XTTSv2 için 200–300 arası önerilir.
                    Fish Speech için 300–400 arası kullanılabilir.
        silence_ms: Birleştirme sırasında parçalar arasına eklenecek
                    sessizlik süresi milisaniye cinsinden (varsayılan: 400).
    """

    # Nokta, ünlem, soru işareti ve üç nokta sonrası boşluk → cümle sonu
    _SENTENCE_END_RE = re.compile(
        r'(?<=[.!?…؟])\s+',
        re.MULTILINE,
    )

    def __init__(
        self,
        max_chars: int = 250,
        silence_ms: int = 400,
    ) -> None:
        self.max_chars  = max_chars
        self.silence_ms = silence_ms

    # ── Metin Bölme ──────────────────────────────────────────────────────────

    def split(self, text: str) -> list[str]:
        """
        Metni max_chars'ı aşmayan, anlamlı parçalara böler.

        Algoritma:
            1. Metni noktalama işaretlerinden cümlelere ayır.
            2. Cümleleri, toplam uzunluk max_chars'ı geçmeyecek şekilde
               gruplara birleştir.
            3. Tek başına max_chars'ı aşan cümleler virgül/noktalı virgülden,
               gerekirse kelime bazında bölünür (force split).

        Args:
            text: Bölünecek ham metin.

        Returns:
            Boş olmayan metin parçaları listesi. Metin zaten kısaysa
            tek elemanlı liste döner.
        """
        text = text.strip()
        if not text:
            return []

        # Kısa metin zaten bölünmeye gerek yok
        if len(text) <= self.max_chars:
            return [text]

        sentences = self._split_into_sentences(text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Tek cümle limiti aşıyorsa zorla böl
            if len(sentence) > self.max_chars:
                if current:
                    chunks.append(current.strip())
                    current = ""
                chunks.extend(self._force_split(sentence))
                continue

            candidate = f"{current} {sentence}".strip() if current else sentence

            if len(candidate) > self.max_chars:
                # Mevcut parçayı kaydet, yeni parçaya başla
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current = candidate

        if current:
            chunks.append(current.strip())

        return [c for c in chunks if c]

    def _split_into_sentences(self, text: str) -> list[str]:
        """Metni noktalama işaretlerine göre cümlelere ayırır."""
        parts = self._SENTENCE_END_RE.split(text)
        return [p.strip() for p in parts if p.strip()]

    def _force_split(self, text: str) -> list[str]:
        """
        Tek başına max_chars'ı aşan metni önce virgül/noktalı virgülden,
        gerekirse kelime bazında böler.
        """
        chunks: list[str] = []
        sub_parts = re.split(r'(?<=[,;])\s+', text)
        current = ""

        for part in sub_parts:
            candidate = f"{current} {part}".strip() if current else part
            if len(candidate) > self.max_chars and current:
                chunks.append(current.strip())
                current = part
            else:
                current = candidate

        if current:
            if len(current) > self.max_chars:
                chunks.extend(self._word_split(current))
            else:
                chunks.append(current.strip())

        return chunks

    def _word_split(self, text: str) -> list[str]:
        """Son çare: kelime bazında böl."""
        words = text.split()
        chunks: list[str] = []
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip() if current else word
            if len(candidate) > self.max_chars and current:
                chunks.append(current)
                current = word
            else:
                current = candidate

        if current:
            chunks.append(current)

        return chunks

    # ── Ses Birleştirme ───────────────────────────────────────────────────────

    def merge_audio_files(
        self,
        chunk_paths: list[Path],
        output_path: Path,
        progress_callback=None,
    ) -> Path:
        """
        .wav dosyalarını aralarına sessizlik ekleyerek tek dosyada birleştirir.

        Args:
            chunk_paths:       Birleştirilecek .wav dosyaları (sıralı).
            output_path:       Nihai çıktı .wav dosyasının yolu.
            progress_callback: Durum mesajları için opsiyonel callback.

        Returns:
            Birleştirilen dosyanın Path nesnesi.

        Raises:
            ImportError:       pydub kurulu değilse.
            FileNotFoundError: Herhangi bir parça dosyası bulunamazsa.
            ValueError:        chunk_paths boş ise.
        """
        try:
            from pydub import AudioSegment  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "pydub kurulu değil.\n"
                "Kurulum: pip install pydub\n"
                "ffmpeg de gereklidir: https://ffmpeg.org/download.html"
            ) from exc

        if not chunk_paths:
            raise ValueError("Birleştirilecek ses dosyası listesi boş.")

        if progress_callback:
            progress_callback(f"{len(chunk_paths)} ses parçası birleştiriliyor...")

        silence  = AudioSegment.silent(duration=self.silence_ms)
        combined = AudioSegment.empty()

        for i, path in enumerate(chunk_paths):
            if not path.exists():
                raise FileNotFoundError(f"Ses parçası bulunamadı: {path}")

            segment   = AudioSegment.from_wav(str(path))
            combined += segment

            # Son parçadan sonra sessizlik ekleme
            if i < len(chunk_paths) - 1:
                combined += silence

        output_path.parent.mkdir(parents=True, exist_ok=True)
        combined.export(str(output_path), format="wav")

        if progress_callback:
            duration_sec = len(combined) / 1000.0
            progress_callback(
                f"Birleştirme tamamlandı: {output_path.name}  "
                f"({duration_sec:.1f} sn) ✓"
            )

        return output_path

    def cleanup_chunks(self, chunk_paths: list[Path]) -> None:
        """Geçici parça .wav dosyalarını sessizce siler."""
        for path in chunk_paths:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
