"""
tts_engine.py
=============
TTS motor fabrikası ve tüm motor implementasyonları.

Motorlar:
    XTTSEngine       — Coqui XTTSv2 (lokal, CUDA)
    FishSpeechEngine — Fish Speech V1.5 (lokal, CUDA)
    HumeTADAEngine   — Hume AI TADA (bulut API)

Kullanım:
    engine = TTSEngineFactory.create("xtts")   # veya "fish_speech" / "hume_tada"
    engine.load_model(progress_callback=print)
    engine.generate(text, output_path, language="tr", speaker_name="Craig Gutsy")

VRAM Yönetimi:
    Bir modelden diğerine geçişte eski motoru önce unload_model() ile temizleyin.
    Bu işlem torch.cuda.empty_cache() çağırır ve GPU belleğini serbest bırakır.
"""

import gc
import os
import subprocess

_MODEL_BASE = r"D:\Ses_Modelleri"   # ← ileride settings_manager'a taşınacak
os.environ.setdefault("COQUI_MODEL_PATH", _MODEL_BASE)
os.environ.setdefault("TTS_HOME",         _MODEL_BASE)

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable


# ── Dil Tablosu ───────────────────────────────────────────────────────────────
# XTTSv2 ve Fish Speech'in ortak dil kümesi.
# Hume TADA yalnızca İngilizce + sınırlı dil destekler; generate() bunu yönetir.
SUPPORTED_LANGUAGES: dict[str, str] = {
    "Türkçe":                    "tr",
    "İngilizce":                 "en",
    "Almanca":                   "de",
    "Fransızca":                 "fr",
    "İspanyolca":                "es",
    "İtalyanca":                 "it",
    "Portekizce":                "pt",
    "Rusça":                     "ru",
    "Lehçe":                     "pl",
    "Felemenkçe":                "nl",
    "Çekçe":                     "cs",
    "Arapça":                    "ar",
    "Çince (Basitleştirilmiş)":  "zh",
    "Japonca":                   "ja",
    "Macarca":                   "hu",
    "Korece":                    "ko",
}

# XTTSv2 dahili konuşmacı listesi
DEFAULT_SPEAKERS: list[str] = [
    "Claribel Dervla",   "Daisy Studious",    "Gracie Wise",       "Tammie Ema",
    "Alison Dietlinde",  "Ana Florence",      "Annmarie Nele",     "Asya Anara",
    "Brenda Stern",      "Gitta Nikolina",    "Henriette Usha",    "Sofia Hellen",
    "Tammy Grit",        "Tanja Adelina",     "Vjollca Johnnie",   "Andrew Chipper",
    "Badr Odhiambo",     "Dionisio Schuyler", "Royston Min",       "Viktor Eka",
    "Abrahan Mack",      "Adde Michal",       "Baldur Sanjin",     "Craig Gutsy",
    "Damien Black",      "Gilberto Mathias",  "Ilkin Urbano",      "Kazuhiko Atallah",
    "Ludvig Milivoj",    "Suad Qasim",        "Torcull Diarmuid",  "Viktor Menelaos",
    "Zacharie Aimilios", "Nova Hogarth",      "Maja Ruoho",        "Uta Obando",
    "Lidiya Szekeres",   "Chandra MacFarland","Szofi Granger",     "Camilla Holmström",
    "Lilya Stainthorpe", "Zofija Kendrick",   "Narelle Moon",      "Barbora MacLean",
    "Alexandra Hisakawa","Alma María",        "Rosemary Okafor",   "Ige Behringer",
    "Filip Traverse",    "Damjan Chapman",    "Wulf Carlevaro",    "Aaron Dreschner",
    "Kumar Dahl",        "Eugenio Mataracı",  "Ferran Simen",      "Xavier Hayasaka",
    "Luis Moray",        "Marcos Rudaski",
]

# Model kimlik sabitleri — UI ve Factory'de kullanılır
MODEL_XTTS:      str = "xtts"
MODEL_FISH:      str = "fish_speech"
MODEL_HUME_TADA: str = "hume_tada"

MODEL_DISPLAY_NAMES: dict[str, str] = {
    MODEL_XTTS:      "XTTSv2  (Coqui — Lokal)",
    MODEL_FISH:      "Fish Speech V1.5  (Lokal)",
    MODEL_HUME_TADA: "Hume AI TADA  (Bulut API)",
}


# ══════════════════════════════════════════════════════════════════════════════
#  Soyut Temel Sınıf
# ══════════════════════════════════════════════════════════════════════════════

class BaseTTSEngine(ABC):
    """
    Tüm TTS motorlarının implement etmesi gereken arayüz.

    Alt sınıf sorumlulukları:
        • load_model()         — modeli GPU/CPU'ya yükle, is_loaded=True yap
        • generate()           — metni sese çevir, Path döndür
        • unload_model()       — kendi kaynaklarını serbest bırak, super() çağır
        • supports_*           — kapasite özelliklerini doğru şekilde dön
    """

    def __init__(self) -> None:
        self.is_loaded: bool = False

    # ── Zorunlu Metotlar ──────────────────────────────────────────────────────

    @abstractmethod
    def load_model(
        self,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Modeli yükler. Hata durumunda RuntimeError fırlatır."""

    @abstractmethod
    def generate(
        self,
        text: str,
        output_path: str | Path,
        language: str = "tr",
        speaker_name: str | None = None,
        speaker_wav: str | Path | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> Path:
        """
        Metni sese çevirir ve dosyaya yazar.

        Args:
            text:           Sese dönüştürülecek metin.
            output_path:    Çıktı .wav dosyasının tam yolu.
            language:       Dil kodu (örn. "tr", "en").
            speaker_name:   Dahili konuşmacı adı (supports_default_speakers=True gerekir).
            speaker_wav:    Klonlama için referans .wav yolu (supports_voice_cloning=True gerekir).
            progress_callback: Durum mesajları için callback.

        Returns:
            Oluşturulan dosyanın Path nesnesi.
        """

    # ── Kapasite Özellikleri ──────────────────────────────────────────────────

    @property
    @abstractmethod
    def supports_default_speakers(self) -> bool:
        """Motor dahili (isimli) konuşmacıları destekliyor mu?"""

    @property
    @abstractmethod
    def supports_voice_cloning(self) -> bool:
        """Motor referans wav ile ses klonlamayı destekliyor mu?"""

    @property
    def default_speakers(self) -> list[str]:
        """Dahili konuşmacı listesi. supports_default_speakers=False ise boş döner."""
        return []

    # ── VRAM / Bellek Temizleme ───────────────────────────────────────────────

    def unload_model(
        self,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        """
        GPU önbelleğini ve Python GC'yi çalıştırır.
        Alt sınıflar kendi model nesnelerini None yaptıktan SONRA super() çağırmalı.
        """
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError:
            pass

        gc.collect()
        self.is_loaded = False

        if progress_callback:
            progress_callback("GPU önbelleği temizlendi. ✓")


# ══════════════════════════════════════════════════════════════════════════════
#  Motor 1 — Coqui XTTSv2
# ══════════════════════════════════════════════════════════════════════════════

class XTTSEngine(BaseTTSEngine):
    """
    Coqui XTTSv2 — lokal CUDA çıkarımı.

    Özellikler:
        • 16 dil desteği
        • 57 dahili konuşmacı
        • Ses klonlama (referans .wav gerekli)
        • VRAM kullanımı: ~3–4 GB (RTX 3060 Ti ile uyumlu)

    İlk çalıştırmada model D:\\Ses_Modelleri dizinine (~2 GB) indirilir.
    """

    MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

    def __init__(self) -> None:
        super().__init__()
        self._tts = None   # TTS nesnesi; yüklendikten sonra atanır

    # ── Kapasite ─────────────────────────────────────────────────────────────

    @property
    def supports_default_speakers(self) -> bool:
        return True

    @property
    def supports_voice_cloning(self) -> bool:
        return True

    @property
    def default_speakers(self) -> list[str]:
        return DEFAULT_SPEAKERS

    # ── Model Yükleme ─────────────────────────────────────────────────────────

    def load_model(self, progress_callback=None) -> None:
        import torch
        os.environ["COQUI_MODEL_PATH"] = r"D:\Ses_Modelleri"

        if progress_callback:
            progress_callback("XTTSv2 — PyTorch ve CUDA kontrol ediliyor...")

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA bulunamadı! CUDA destekli PyTorch kurun:\n"
                "pip install torch --index-url https://download.pytorch.org/whl/cu121"
            )

        if progress_callback:
            progress_callback(f"GPU algılandı: {torch.cuda.get_device_name(0)}")
            progress_callback("XTTSv2 modeli yükleniyor (ilk açılışta indirme olabilir)...")

        from TTS.api import TTS  # type: ignore
        self._tts = TTS(model_name=self.MODEL_NAME, progress_bar=False).to("cuda")
        self.is_loaded = True

        if progress_callback:
            progress_callback("XTTSv2 başarıyla yüklendi! ✓")

    # ── Model Kaldırma ────────────────────────────────────────────────────────

    def unload_model(self, progress_callback=None) -> None:
        if progress_callback:
            progress_callback("XTTSv2 GPU'dan kaldırılıyor...")
        self._tts = None
        super().unload_model(progress_callback)

    # ── Ses Üretimi ───────────────────────────────────────────────────────────

    def generate(
        self,
        text: str,
        output_path: str | Path,
        language: str = "tr",
        speaker_name: str | None = None,
        speaker_wav: str | Path | None = None,
        progress_callback=None,
    ) -> Path:
        if not self.is_loaded or self._tts is None:
            raise RuntimeError("Model yüklenmedi. Önce load_model() çağrın.")
        if not speaker_name and not speaker_wav:
            raise ValueError("Ses kaynağı belirtilmedi: dahili ses veya referans dosyası gerekli.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            mode = "Klonlama" if speaker_wav else "Dahili Ses"
            progress_callback(f"XTTSv2 üretiyor (Mod: {mode})...")

        if speaker_wav:
            self._tts.tts_to_file(
                text=text,
                speaker_wav=str(speaker_wav),
                language=language,
                file_path=str(output_path),
            )
        else:
            self._tts.tts_to_file(
                text=text,
                speaker=speaker_name,
                language=language,
                file_path=str(output_path),
            )

        if progress_callback:
            progress_callback(f"Kaydedildi: {output_path.name} ✓")

        return output_path


# ══════════════════════════════════════════════════════════════════════════════
#  Motor 2 — Fish Speech V1.5
# ══════════════════════════════════════════════════════════════════════════════

class FishSpeechEngine(BaseTTSEngine):
    """
    Fish Speech V1.5 — lokal CUDA çıkarımı (Subprocess Modu).

    Kurulum:
        D:\AI_Ortak_Venv\Venv_Forge_Fish_v2 içindeki izole venv'i kullanır.
        Bu sayede Torch versiyon çakışmaları engellenir ve VRAM her üretim
        sonrası otomatik temizlenir.

    Model dosyaları:
        D:\Ses_Modelleri\fish-speech-1.5\
    """

    MODEL_DIR = Path(r"D:\Ses_Modelleri\fish-speech-1.5")
    
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    FISH_PYTHON   = str(_PROJECT_ROOT / ".venv_fish" / "Scripts" / "python.exe")

    def __init__(self) -> None:
        super().__init__()
        # Subprocess modunda yerel model nesnesi tutulmaz
        self._model = None

    # ── Kapasite ─────────────────────────────────────────────────────────────

    @property
    def supports_default_speakers(self) -> bool:
        return False   # Fish Speech dahili isimli konuşmacı sunmaz

    @property
    def supports_voice_cloning(self) -> bool:
        return True

    # ── Model Yükleme (Doğrulama) ─────────────────────────────────────────────

    def load_model(self, progress_callback=None) -> None:
        """
        Modeli ana sürece yüklemek yerine, uydu venv ve Python yolunu doğrular.
       
        """
        if progress_callback:
            progress_callback("Fish Speech (Satellite) — Bağlantı kontrol ediliyor...")

        # Python yolunun varlığını kontrol et
        if not os.path.exists(self.FISH_PYTHON):
            raise RuntimeError(
                f"Fish Speech venv bulunamadı!\nBeklenen: {self.FISH_PYTHON}\n"
                "Lütfen junction bağlantısını ve venv kurulumunu kontrol edin."
            )

        if progress_callback:
            import torch
            gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "GPU Bilinmiyor"
            progress_callback(f"Fish Speech Köprüsü Hazır — GPU: {gpu_name}")
            progress_callback("Üretim sırasında izole süreç (subprocess) kullanılacak. ✓")

        self.is_loaded = True

    # ── Model Kaldırma ────────────────────────────────────────────────────────

    def unload_model(self, progress_callback=None) -> None:
        """
        Subprocess her üretimden sonra kapandığı için VRAM zaten boşalır.
        Sadece durumu sıfırlıyoruz.
        """
        if progress_callback:
            progress_callback("Fish Speech durumu sıfırlandı.")
        self._model = None
        super().unload_model(progress_callback)

    # ── Ses Üretimi (Subprocess) ──────────────────────────────────────────────

    def generate(
        self,
        text: str,
        output_path: str | Path,
        language: str = "tr",
        speaker_name: str | None = None,
        speaker_wav: str | Path | None = None,
        progress_callback=None,
    ) -> Path:
        """
        Metni sese çevirmek için .venv_fish içindeki Python'ı çağırır.
       
        """
        if not self.is_loaded:
            raise RuntimeError("Model 'yüklenmedi'. Önce butona basın.")
            
        if not speaker_wav:
            raise ValueError(
                "Fish Speech ses klonlama gerektirir.\n"
                "Lütfen reference_voices/ klasöründen bir .wav dosyası seçin."
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback("Fish venv başlatılıyor (İzole üretim)...")

        # CLI Komutu: Fish Speech inference modülünü dışarıdan çalıştır
        # Not: Fish Speech 2.0 CLI parametre yapısına uygun düzenlenmiştir.
        command = [
            self.FISH_PYTHON, 
            "-m", "fish_speech.inference",
            "--text", text,
            "--reference_audio", str(speaker_wav),
            "--output", str(output_path),
            "--checkpoint_path", str(self.MODEL_DIR)
        ]

        try:
            # Süreci başlat ve bitmesini bekle
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            
            if progress_callback:
                progress_callback("Fish venv üretimi tamamladı ve VRAM'i serbest bıraktı. ✓")
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Bilinmeyen subprocess hatası."
            raise RuntimeError(f"Fish Speech Subprocess Hatası:\n{error_msg}")

        if progress_callback:
            progress_callback(f"Kaydedildi: {output_path.name} ✓")

        return output_path


# ══════════════════════════════════════════════════════════════════════════════
#  Motor 3 — Hume AI TADA
# ══════════════════════════════════════════════════════════════════════════════

class HumeTADAEngine(BaseTTSEngine):
    """
    Hume AI TADA — bulut tabanlı duygusal TTS API.

    Kurulum:
        pip install hume-tada

    API Anahtarı (zorunlu):
        Windows Komut İstemi:
            set HUME_API_KEY=your_api_key_here
        Kalıcı ayar için Windows Ortam Değişkenleri panelini kullanın.
        Hesap oluşturmak için: https://platform.hume.ai

    Özellikler:
        • İnternet bağlantısı gerektirir
        • 7 ön tanımlı ses (ITO, KORA, DACHER, AURA, FINN, STELLA, WHIMSY)
        • Duygusal ifade ve tonlama desteği
        • Ses klonlama TADA V1'de desteklenmez
        • GPU kullanmaz; VRAM tüketimi yoktur

    NOT: hume-tada paketinin Python API'si değişebilir.
         Güncel dokümantasyon: https://dev.hume.ai/docs/empathic-voice-interface-evi/tts
    """

    # Hume AI TADA'nın ön tanımlı sesleri
    HUME_SPEAKERS: list[str] = [
        "ITO",
        "KORA",
        "DACHER",
        "AURA",
        "FINN",
        "STELLA",
        "WHIMSY",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client = None
        self._api_key: str | None = None

    # ── Kapasite ─────────────────────────────────────────────────────────────

    @property
    def supports_default_speakers(self) -> bool:
        return True

    @property
    def supports_voice_cloning(self) -> bool:
        return False   # TADA mevcut sürümde klonlama yapmaz

    @property
    def default_speakers(self) -> list[str]:
        return self.HUME_SPEAKERS

    # ── Model Yükleme (API bağlantısı) ────────────────────────────────────────

    def load_model(self, progress_callback=None) -> None:
        api_key = os.environ.get("HUME_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "HUME_API_KEY ortam değişkeni bulunamadı!\n"
                "Windows CMD: set HUME_API_KEY=your_api_key\n"
                "Hesap: https://platform.hume.ai"
            )

        if progress_callback:
            progress_callback("Hume AI TADA — API anahtarı doğrulanıyor...")

        try:
            from hume_tada import HumeTADAClient  # type: ignore

            self._client = HumeTADAClient(api_key=api_key)
            # Bağlantıyı doğrulamak için hafif bir test isteği
            self._client.ping()

        except ImportError as exc:
            raise RuntimeError(
                "hume-tada paketi bulunamadı.\n"
                "Kurulum: pip install hume-tada\n"
                f"Detay: {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Hume AI bağlantı hatası: {exc}") from exc

        self._api_key = api_key
        self.is_loaded = True

        if progress_callback:
            progress_callback("Hume AI TADA bağlantısı kuruldu! ✓")

    # ── Model Kaldırma ────────────────────────────────────────────────────────

    def unload_model(self, progress_callback=None) -> None:
        if progress_callback:
            progress_callback("Hume AI TADA bağlantısı kapatılıyor...")
        self._client = None
        self._api_key = None
        # Hume bulut tabanlı; GPU temizlemesi gerekmez; sadece durumu sıfırla.
        self.is_loaded = False
        if progress_callback:
            progress_callback("Hume AI TADA bağlantısı kapatıldı. ✓")

    # ── Ses Üretimi ───────────────────────────────────────────────────────────

    def generate(
        self,
        text: str,
        output_path: str | Path,
        language: str = "tr",
        speaker_name: str | None = None,
        speaker_wav: str | Path | None = None,
        progress_callback=None,
    ) -> Path:
        if not self.is_loaded or self._client is None:
            raise RuntimeError("Bağlantı yok. Önce load_model() çağrın.")

        # Ses seçilmediyse ilk sesi varsayılan yap
        if not speaker_name or speaker_name not in self.HUME_SPEAKERS:
            speaker_name = self.HUME_SPEAKERS[0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(f"Hume TADA ile üretiliyor (Ses: {speaker_name})...")

        # hume-tada API çağrısı; sürüme göre parametre adları değişebilir.
        audio_bytes: bytes = self._client.synthesize(
            text=text,
            voice=speaker_name,
            language=language,
        )
        output_path.write_bytes(audio_bytes)

        if progress_callback:
            progress_callback(f"Kaydedildi: {output_path.name} ✓")

        return output_path


# ══════════════════════════════════════════════════════════════════════════════
#  Factory
# ══════════════════════════════════════════════════════════════════════════════

class TTSEngineFactory:
    """
    Model kimliğine göre doğru motor örneğini oluşturan fabrika sınıfı.

    Kullanım:
        engine = TTSEngineFactory.create(MODEL_XTTS)
        engine = TTSEngineFactory.create(MODEL_FISH)
        engine = TTSEngineFactory.create(MODEL_HUME_TADA)

        available = TTSEngineFactory.available_models()
        # → {"xtts": "XTTSv2 (Coqui — Lokal)", "fish_speech": ..., "hume_tada": ...}
    """

    _registry: dict[str, type[BaseTTSEngine]] = {
        MODEL_XTTS:      XTTSEngine,
        MODEL_FISH:      FishSpeechEngine,
        MODEL_HUME_TADA: HumeTADAEngine,
    }

    @classmethod
    def create(cls, model_id: str) -> BaseTTSEngine:
        """
        Belirtilen model kimliği için yeni, yüklenmemiş bir motor örneği döndürür.

        Args:
            model_id: MODEL_XTTS | MODEL_FISH | MODEL_HUME_TADA

        Returns:
            is_loaded=False durumunda bir BaseTTSEngine örneği.

        Raises:
            ValueError: Bilinmeyen model_id girilirse.
        """
        if model_id not in cls._registry:
            raise ValueError(
                f"Bilinmeyen model kimliği: '{model_id}'.\n"
                f"Geçerli seçenekler: {list(cls._registry)}"
            )
        return cls._registry[model_id]()

    @classmethod
    def available_models(cls) -> dict[str, str]:
        """Model kimliği → görünen ad eşlemesi."""
        return MODEL_DISPLAY_NAMES.copy()


# Geriye dönük uyumluluk — eski kodun TTSEngine ismini import etmesi durumunda
TTSEngine = XTTSEngine