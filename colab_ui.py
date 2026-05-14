# colab_ui.py
"""
EchoForge — Google Colab / Gradio Arayüzü.

PyQt6 yerine Gradio kullanılır.
MacBook veya başka bir cihazdan tarayıcıyla erişilebilir.

Başlatma:
    python main.py --colab
    veya Colab notebook'ta:
        from colab_ui import launch_gradio
        launch_gradio()

Sekmeler:
    STT  — Ses → Metin   (faster-whisper)
    TTS  — Metin → Ses   (XTTSv2)
    TTT  — Metin → Metin (Ollama veya Gemini)
    STS  — Ses → Ses     (STT + TTS pipeline)
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from core.environment import Environment
from core.file_manager import FileManager, AUDIO_DIR, TRANSCRIPTS_DIR


# ══════════════════════════════════════════════════════════════════════════════
#  STT — Ses → Metin
# ══════════════════════════════════════════════════════════════════════════════

def transcribe(audio_path: str, model_size: str) -> tuple[str, str]:
    """
    Returns: (transkript metni, durum mesajı)
    """
    from faster_whisper import WhisperModel
    import torch

    device       = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    model    = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )

    parts = [seg.text.strip() for seg in segments if seg.text.strip()]
    text  = " ".join(parts)

    # Transkripti kaydet
    audio_file = Path(audio_path)
    out_path   = FileManager.save_transcript(audio_file, text)

    status = (
        f"✅ Tamamlandı | Dil: {info.language.upper()} "
        f"({info.language_probability:.0%}) | {len(parts)} segment | "
        f"Kaydedildi: {out_path.name}"
    )
    return text, status


# ══════════════════════════════════════════════════════════════════════════════
#  TTS — Metin → Ses
# ══════════════════════════════════════════════════════════════════════════════
_tts_engine_cache: dict = {}
def synthesize(
    text: str,
    speaker_name: str,
    language: str,
    reference_wav: str | None,
) -> tuple[str, str]:
    """
    Returns: (çıktı wav yolu, durum mesajı)
    """
    import datetime
    from tts.tts_engine import TTSEngineFactory, MODEL_XTTS

    if MODEL_XTTS not in _tts_engine_cache:
        engine = TTSEngineFactory.create(MODEL_XTTS)
        engine.load_model()
        _tts_engine_cache[MODEL_XTTS] = engine
    engine = _tts_engine_cache[MODEL_XTTS]

    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = FileManager.get_audio_output_path(f"tts_{timestamp}.wav")

    speaker_wav = Path(reference_wav) if reference_wav else None

    engine.generate(
        text         = text,
        output_path  = output_path,
        language     = language,
        speaker_name = speaker_name if not speaker_wav else None,
        speaker_wav  = speaker_wav,
    )

    return str(output_path), f"✅ Kaydedildi: {output_path.name}"


# ══════════════════════════════════════════════════════════════════════════════
#  TTT — Metin → Metin
# ══════════════════════════════════════════════════════════════════════════════

def process_text(
    text: str,
    prompt_template: str,
    model_name: str,
    backend: str,
) -> str:
    """
    backend: "ollama" | "gemini"
    """
    prompt = prompt_template.replace("{text}", text) if "{text}" in prompt_template \
             else f"{prompt_template}\n\n{text}"

    result_tokens: list[str] = []

    if backend.lower() == "gemini":
        from core.gemini_client import generate_stream
    else:
        from core.ollama_client import generate_stream

    generate_stream(
        model_name      = model_name,
        prompt          = prompt,
        stream_callback = result_tokens.append,
    )

    return "".join(result_tokens)


# ══════════════════════════════════════════════════════════════════════════════
#  STS — Ses → Ses
# ══════════════════════════════════════════════════════════════════════════════

def speech_to_speech(
    audio_path: str,
    whisper_model: str,
    tts_speaker: str,
    tts_language: str,
    reference_wav: str | None,
    translate_first: bool,
    translate_model: str,
    translate_backend: str,
) -> tuple[str, str, str]:
    """
    Pipeline: STT → (opsiyonel TTT çevirisi) → TTS

    Returns: (transkript, çıktı_wav_yolu, durum)
    """
    # 1 — STT
    transcript, stt_status = transcribe(audio_path, whisper_model)

    # 2 — Opsiyonel çeviri
    processed = transcript
    if translate_first and translate_model:
        prompt = (
            f"Aşağıdaki metni {tts_language} diline çevir. "
            f"Sadece çeviriyi yaz:\n\n{{text}}"
        )
        processed = process_text(transcript, prompt, translate_model, translate_backend)

    # 3 — TTS
    wav_path, tts_status = synthesize(processed, tts_speaker, tts_language, reference_wav)

    status = f"STT: {stt_status}\nTTS: {tts_status}"
    return transcript, wav_path, status


# ══════════════════════════════════════════════════════════════════════════════
#  Gradio Arayüzü
# ══════════════════════════════════════════════════════════════════════════════

def launch_gradio(share: bool = True) -> None:
    """
    Gradio arayüzünü başlatır.
    share=True → public URL üretir (MacBook'tan erişim için)
    """
    try:
        import gradio as gr
    except ImportError:
        raise ImportError(
            "Gradio kurulu değil.\n"
            "Kurulum: pip install gradio"
        )

    from tts.tts_engine import DEFAULT_SPEAKERS, SUPPORTED_LANGUAGES

    env = Environment.instance()
    env.ensure_drive_mounted()
    env.ensure_colab_dirs()
    FileManager.ensure_directories()

    # Referans sesleri
    ref_voices     = [str(p) for p in FileManager.get_reference_voices()]
    ref_voices_opt = ["— Yok (dahili ses) —"] + ref_voices

    whisper_models = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"]
    lang_names     = list(SUPPORTED_LANGUAGES.keys())

    # ── Ollama model listesi ──
    try:
        from core.ollama_client import fetch_models
        ollama_models = fetch_models() or ["aya-expanse:latest"]
    except Exception:
        ollama_models = ["aya-expanse:latest"]

    # ── Gemini modelleri ──
    from core.gemini_client import GEMINI_MODELS

    with gr.Blocks(title="EchoForge", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🎙 EchoForge\n"
            f"**Ortam:** {env.runtime_label()} &nbsp;|&nbsp; "
            f"**GPU:** {'✅ CUDA' if _cuda_available() else '❌ CPU'}"
        )

        with gr.Tab("🎙 STT — Ses → Metin"):
            with gr.Row():
                stt_audio   = gr.Audio(type="filepath", label="Ses Dosyası")
                stt_model   = gr.Dropdown(whisper_models, value="large-v3-turbo",
                                          label="Whisper Modeli")
            stt_btn    = gr.Button("▶ Transkribe Et", variant="primary")
            stt_out    = gr.Textbox(label="Transkript", lines=10)
            stt_status = gr.Textbox(label="Durum", interactive=False)
            stt_btn.click(
                fn=transcribe,
                inputs=[stt_audio, stt_model],
                outputs=[stt_out, stt_status],
            )

        with gr.Tab("🔊 TTS — Metin → Ses"):
            tts_text     = gr.Textbox(label="Metin", lines=6,
                                       placeholder="Sese dönüştürülecek metin…")
            with gr.Row():
                tts_speaker  = gr.Dropdown(DEFAULT_SPEAKERS, value="Craig Gutsy",
                                            label="Dahili Ses")
                tts_lang     = gr.Dropdown(lang_names, value="Türkçe", label="Dil")
            tts_ref      = gr.Dropdown(ref_voices_opt,
                                        value=ref_voices_opt[0],
                                        label="Referans Ses (Klonlama)")
            tts_btn      = gr.Button("▶ Ses Üret", variant="primary")
            tts_audio    = gr.Audio(label="Çıktı")
            tts_status   = gr.Textbox(label="Durum", interactive=False)

            def _tts_wrap(text, speaker, lang, ref):
                ref_path = None if ref == ref_voices_opt[0] else ref
                from tts.tts_engine import SUPPORTED_LANGUAGES
                lang_code = SUPPORTED_LANGUAGES.get(lang, "tr")
                wav, status = synthesize(text, speaker, lang_code, ref_path)
                return wav, status

            tts_btn.click(
                fn=_tts_wrap,
                inputs=[tts_text, tts_speaker, tts_lang, tts_ref],
                outputs=[tts_audio, tts_status],
            )

        with gr.Tab("✏️ TTT — Metin → Metin"):
            with gr.Row():
                ttt_backend = gr.Radio(["Ollama", "Gemini"], value="Ollama",
                                        label="Motor")
                ttt_model   = gr.Dropdown(ollama_models, label="Model")
            ttt_input   = gr.Textbox(label="Giriş Metni", lines=6)
            ttt_prompt  = gr.Textbox(
                label="Prompt ({text} → giriş metni)",
                value="Aşağıdaki metni Türkçeye çevir:\n\n{text}",
                lines=3,
            )
            ttt_btn     = gr.Button("▶ İşle", variant="primary")
            ttt_output  = gr.Textbox(label="Çıktı", lines=8)

            def _ttt_model_update(backend):
                models = GEMINI_MODELS if backend == "Gemini" else ollama_models
                return gr.Dropdown(choices=models, value=models[0])

            ttt_backend.change(_ttt_model_update, ttt_backend, ttt_model)
            ttt_btn.click(
                fn=process_text,
                inputs=[ttt_input, ttt_prompt, ttt_model, ttt_backend],
                outputs=ttt_output,
            )

        with gr.Tab("🔄 STS — Ses → Ses"):
            sts_audio   = gr.Audio(type="filepath", label="Kaynak Ses")
            with gr.Row():
                sts_wmodel  = gr.Dropdown(whisper_models, value="large-v3-turbo",
                                           label="Whisper Modeli")
                sts_speaker = gr.Dropdown(DEFAULT_SPEAKERS, value="Craig Gutsy",
                                           label="Hedef Ses")
                sts_lang    = gr.Dropdown(lang_names, value="Türkçe", label="Dil")
            sts_ref     = gr.Dropdown(ref_voices_opt, value=ref_voices_opt[0],
                                       label="Referans Ses")
            with gr.Row():
                sts_translate = gr.Checkbox(label="Önce Çevir", value=False)
                sts_tmodel    = gr.Dropdown(ollama_models, label="Çeviri Modeli")
                sts_tbackend  = gr.Radio(["Ollama", "Gemini"], value="Ollama",
                                          label="Çeviri Motoru")
            sts_btn       = gr.Button("▶ Dönüştür", variant="primary")
            sts_transcript = gr.Textbox(label="Transkript", lines=4)
            sts_out_audio  = gr.Audio(label="Çıktı Ses")
            sts_status     = gr.Textbox(label="Durum", interactive=False)

            def _sts_wrap(audio, wm, spk, lang, ref, translate, tmodel, tbackend):
                ref_path = None if ref == ref_voices_opt[0] else ref
                from tts.tts_engine import SUPPORTED_LANGUAGES
                lang_code = SUPPORTED_LANGUAGES.get(lang, "tr")
                return speech_to_speech(
                    audio, wm, spk, lang_code, ref_path,
                    translate, tmodel, tbackend,
                )

            sts_btn.click(
                fn=_sts_wrap,
                inputs=[sts_audio, sts_wmodel, sts_speaker, sts_lang,
                        sts_ref, sts_translate, sts_tmodel, sts_tbackend],
                outputs=[sts_transcript, sts_out_audio, sts_status],
            )

    demo.launch(share=share, server_name="0.0.0.0")


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False
