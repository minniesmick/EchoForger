<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# <code>❯ REPLACE-ME</code>

<em>Transform speech to text and vice versa effortlessly.  
Unlock productivity with EchoForge's intuitive interface.</em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Flask-000000.svg?style=default&logo=Flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/Markdown-000000.svg?style=default&logo=Markdown&logoColor=white" alt="Markdown">
<img src="https://img.shields.io/badge/Ollama-000000.svg?style=default&logo=Ollama&logoColor=white" alt="Ollama">
<img src="https://img.shields.io/badge/Typer-000000.svg?style=default&logo=Typer&logoColor=white" alt="Typer">
<img src="https://img.shields.io/badge/scikitlearn-F7931E.svg?style=default&logo=scikit-learn&logoColor=white" alt="scikitlearn">
<img src="https://img.shields.io/badge/tqdm-FFC107.svg?style=default&logo=tqdm&logoColor=black" alt="tqdm">
<img src="https://img.shields.io/badge/Babel-F9DC3E.svg?style=default&logo=Babel&logoColor=black" alt="Babel">
<img src="https://img.shields.io/badge/Rich-FAE742.svg?style=default&logo=Rich&logoColor=black" alt="Rich">
<img src="https://img.shields.io/badge/SymPy-3B5526.svg?style=default&logo=SymPy&logoColor=white" alt="SymPy">
<br>
<img src="https://img.shields.io/badge/Wasabi-01CD3E.svg?style=default&logo=Wasabi&logoColor=white" alt="Wasabi">
<img src="https://img.shields.io/badge/spaCy-09A3D5.svg?style=default&logo=spaCy&logoColor=white" alt="spaCy">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=default&logo=NumPy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/Numba-00A3E0.svg?style=default&logo=Numba&logoColor=white" alt="Numba">
<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=default&logo=Pytest&logoColor=white" alt="Pytest">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/AIOHTTP-2C5BB4.svg?style=default&logo=AIOHTTP&logoColor=white" alt="AIOHTTP">
<img src="https://img.shields.io/badge/SciPy-8CAAE6.svg?style=default&logo=SciPy&logoColor=white" alt="SciPy">
<img src="https://img.shields.io/badge/pandas-150458.svg?style=default&logo=pandas&logoColor=white" alt="pandas">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=default&logo=Pydantic&logoColor=white" alt="Pydantic">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Echo is a powerful tool designed to streamline speech processing tasks. It offers versatile STT, TTS, TTT, and STS functionalities, making it an essential asset for developers working with audio data.

**Why Echo?**

This project aims to simplify complex audio processing workflows. The core features include:

- **🚀 Versatile Speech Processing:** Supports all major speech conversion needs.
- **🔄 Efficient Batch Processing:** Manages large batches of files with real-time progress updates.
- **💻 User-Friendly Interface:** Built using PyQt5 for a seamless user experience.
- **⚙️ Customizable Settings:** Allows users to modify directories, thresholds, and API keys easily.
- 🎶 Advanced Audio Visualization:** Displays waveforms for better audio analysis.
- 🔒 Secure Authentication:** Ensures protected access with JWT token validation.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Monolithic architecture with a mix of Python scripts and Jupyter notebooks.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Use of libraries like `spacy`, `transformers`, and `torch` for natural language processing and machine learning tasks.</li><li>Presence of unit tests in the form of `.ipynb` files, but no formal test suite.</li></ul> |
| 📄 | **Documentation** | <ul><li>Limited documentation found in Jupyter notebooks and some comments within Python scripts.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integration with various libraries such as `spacy`, `transformers`, `torch`, and `pyttsx3` for text-to-speech conversion.</li><li>Support for audio processing using `librosa`, `soundfile`, and `torchaudio`.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Code is not modular; everything is in a single script or Jupyter notebook.</li></ul> |
| 🧪 | **Testing**       | <ul><li>Unit tests are present but informal, primarily in the form of interactive cells in Jupyter notebooks.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>No formal performance analysis or optimization is evident.</li></ul> |
| 🛡️ | **Security**      | <ul><li>Limited security measures; no explicit security hardening or validation of inputs.</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Dependencies managed via `requirements.txt`, which includes a wide range of libraries for NLP, machine learning, audio processing, and more.</li></ul> |
| 🚀 | **Scalability**   | <ul><li>No scalability considerations or optimizations evident; the architecture is not designed for horizontal scaling.</li></ul> |

---

## Project Structure

```sh
└── /
    ├── colab_ui.py
    ├── core
    │   ├── __pycache__
    │   ├── archive_manager.py
    │   ├── batch_worker.py
    │   ├── diarization_worker.py
    │   ├── environment.py
    │   ├── file_manager.py
    │   ├── gemini_client.py
    │   ├── mic_worker.py
    │   ├── ollama_client.py
    │   ├── settings_manager.py
    │   └── transcriber.py
    ├── echoforge_archive.db
    ├── EchoForge_Base.md.md
    ├── EchoForge_notebook.ipynb
    ├── graphify-out
    │   ├── .graphify_analysis.json
    │   ├── EchoForge-callflow.html
    │   ├── graph.json
    │   └── manifest.json
    ├── main.py
    ├── output
    │   ├── .gitkeep
    │   ├── audio
    │   └── transcripts
    ├── README.md
    ├── reference_voices
    │   ├── .gitkeep
    │   ├── alper_denemeses.wav
    │   └── WhatsApp Ptt 2026-05-12 at 23.00.18.mp3
    ├── requirements.txt
    ├── requirements_all.txt
    ├── settings.json
    ├── tts
    │   ├── __pycache__
    │   ├── kokoro_engine.py
    │   ├── text_preprocessor.py
    │   ├── tts_engine.py
    │   └── workers.py
    ├── ui
    │   ├── __init__.py
    │   ├── __pycache__
    │   ├── archive_panel.py
    │   ├── file_panel.py
    │   ├── main_window.py
    │   ├── queue_panel.py
    │   ├── settings_panel.py
    │   ├── styles.py
    │   ├── transcription_panel.py
    │   ├── tts_panel.py
    │   ├── ttt_panel.py
    │   ├── waveform_widget.py
    │   └── welcome_panel.py
    └── voice_files
        ├── .gitkeep
        ├── audio1007051497.m4a
        ├── test01_20s.wav
        └── WhatsApp Ptt 2026-05-12 at 23.00.18.mp3
```

### Project Index

<details open>
	<summary><b><code>/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/colab_ui.py'>colab_ui.py</a></b></td>
					<td style='padding: 8px;'>- The script defines functions for speech-to-text (STT), text-to-speech (TTS), text-to-text (TTT), and speech-to-speech (STS) processing, along with a Gradio interface to interact with these functionalities<br>- It includes options for selecting models, languages, and reference voices<br>- The script also checks for CUDA availability for GPU acceleration if installed.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/EchoForge_notebook.ipynb'>EchoForge_notebook.ipynb</a></b></td>
					<td style='padding: 8px;'>Sets up Google Drive, clones EchoForge repository, installs dependencies, configures directories, loads API keys, checks GPU availability, and launches the EchoForge Gradio interface.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/main.py'>main.py</a></b></td>
					<td style='padding: 8px;'>- Main.py initializes the EchoForge application by creating a Qt instance, setting app metadata, and launching the main window<br>- It handles fatal errors gracefully with QMessageBox, ensuring a user-friendly experience even in unexpected situations.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>Manages project dependencies, ensuring all required libraries are installed for the application to run smoothly.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/requirements_all.txt'>requirements_all.txt</a></b></td>
					<td style='padding: 8px;'>Manages project dependencies, ensuring all required libraries are installed for the application to run smoothly across its architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/settings.json'>settings.json</a></b></td>
					<td style='padding: 8px;'>Settings.json configures model parameters and paths for speech recognition and text-to-speech functionalities, essential for the projects core operations.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- core Submodule -->
	<details>
		<summary><b>core</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ core</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/archive_manager.py'>archive_manager.py</a></b></td>
					<td style='padding: 8px;'>Manages SQLite database for storing transcriptions, including embedding and searching functionalities.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/batch_worker.py'>batch_worker.py</a></b></td>
					<td style='padding: 8px;'>- BatchWorker processes files in sequence, using a single WhisperModel instance to save memory and time<br>- It emits signals for progress, errors, and completion, facilitating UI updates.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/diarization_worker.py'>diarization_worker.py</a></b></td>
					<td style='padding: 8px;'>- The <code>diarization_worker.py</code> file processes audio files to identify speakers and optionally transcribe them using the pyannote.audio library and Whisper model<br>- It emits signals for progress, speaker segments, final output, and errors, making it a versatile component in speech recognition workflows.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/environment.py'>environment.py</a></b></td>
					<td style='padding: 8px;'>Environment detection and path resolution for EchoForge project, supporting LOCAL and COLAB environments.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/file_manager.py'>file_manager.py</a></b></td>
					<td style='padding: 8px;'>- FileManager class manages file operations like copying, saving transcripts, and generating paths for audio and transcript files<br>- It ensures all files are stored in designated directories with proper naming conventions.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/gemini_client.py'>gemini_client.py</a></b></td>
					<td style='padding: 8px;'>- Gemini_client.py` initializes the Google Gemini API client, manages model interactions, and provides threading workers for generating text and fetching models<br>- It ensures seamless integration with other components of the EchoForge application.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/mic_worker.py'>mic_worker.py</a></b></td>
					<td style='padding: 8px;'>- MicWorker captures audio from the microphone, transcribes it using Whisper, and emits segments and final text through signals<br>- It handles recording, denoising, and error management in a PyQt-based application.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/ollama_client.py'>ollama_client.py</a></b></td>
					<td style='padding: 8px;'>- Core/ollama_client.py` manages interactions with the Ollama API, providing functions to fetch models, unload them, and generate text using a stream<br>- It includes worker classes for asynchronous operations in a PyQt6 GUI application, ensuring smooth performance.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/settings_manager.py'>settings_manager.py</a></b></td>
					<td style='padding: 8px;'>SettingsManager reads/writes application settings from/to settings.json using the singleton pattern, providing methods to get, set, and reset configuration values across the project.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/core/transcriber.py'>transcriber.py</a></b></td>
					<td style='padding: 8px;'>- Transcriber.py handles audio transcription using the faster-whisper backend with Whisper large-v3-turbo model<br>- It supports CUDA acceleration on RTX 3060 Ti and falls back to CPU if unavailable<br>- The script includes functions for noise reduction, device detection, and asynchronous transcription in a PyQt thread, emitting progress, segments, and final text.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- graphify-out Submodule -->
	<details>
		<summary><b>graphify-out</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ graphify-out</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/graphify-out/.graphify_analysis.json'>.graphify_analysis.json</a></b></td>
					<td style='padding: 8px;'>- The project appears to be a comprehensive suite of tools for text-to-speech (TTS) and transcription, with various components like UI panels, TTS engines, and model management<br>- The cohesion between these components is moderate, indicating some integration but not deep coupling<br>- Key functions such as loading models and generating transcriptions are central to the projects functionality<br>- Surprising connections include a UI panel calling across different modules for tasks like fetching and switching models, highlighting potential areas for optimization or refactoring.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/graphify-out/EchoForge-callflow.html'>EchoForge-callflow.html</a></b></td>
					<td style='padding: 8px;'>- The <code>EchoForge-callflow.html</code> file serves as a comprehensive documentation page for the call flow and architecture of the EchoForge project<br>- It utilizes Mermaid.js to visually represent the complex interactions and dependencies within the system, making it easier for developers and stakeholders to understand the overall structure and functionality.This HTML file is located in the <code>graphify-out</code> directory and is part of a larger documentation suite that aims to provide detailed insights into various aspects of the project<br>- By including interactive diagrams, the file enhances the accessibility and usability of the documentation, ensuring that users can quickly grasp the intricacies of the call flow without delving into extensive technical details.<strong>Key Features:</strong>-<strong>Visual Documentation:</strong> Uses Mermaid.js to create interactive diagrams that represent the call flow and architecture.-<strong>Styling:</strong> Custom CSS styles are applied to ensure a clean and professional appearance, with a focus on readability and consistency.-<strong>Accessibility:</strong> The file is designed to be responsive, ensuring it looks good on various devices.This documentation page is an essential resource for anyone working within or interacting with the EchoForge project, providing a quick reference point for understanding its architecture and call flow.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/graphify-out/graph.json'>graph.json</a></b></td>
					<td style='padding: 8px;'>- Graph Type:<strong> The graph is undirected (<code>directed: false</code>) and does not allow multiple edges between the same pair of nodes (<code>multigraph: false</code>).-</strong>Nodes:<strong> The graph includes several nodes, each representing a file or function within the project<br>- For instance:-<code>colab_ui.py</code>: A Python code file located at the root.-<code>synthesize()</code>: A function defined in <code>colab_ui.py</code>.-<code>process_text()</code>: Another function also defined in <code>colab_ui.py</code>.</strong>Purpose:<strong>-</strong>Dependency Mapping:<strong> The graph helps in visualizing and understanding how different parts of the project are interconnected<br>- This is essential for developers to navigate the codebase more efficiently.-</strong>Community Detection:** Nodes are categorized into communities, which can help identify cohesive groups of related files or functions.This JSON file serves as a foundational resource for tools that analyze project structure, facilitate navigation, and support refactoring efforts.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/graphify-out/manifest.json'>manifest.json</a></b></td>
					<td style='padding: 8px;'>- EchoForge project files include source code, requirements, outputs, and voice references<br>- The summary focuses on the projects structure and content without using specific file names or phrases like This file' or The code.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- output Submodule -->
	<details>
		<summary><b>output</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ output</b></code>
			<!-- audio Submodule -->
			<details>
				<summary><b>audio</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ output.audio</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/audio/tts_20260513_024346.wav'>tts_20260513_024346.wav</a></b></td>
							<td style='padding: 8px;'>- File NameWhat is the name of the code file?2<br>- <strong>FunctionalityWhat does the code file do in terms of its primary function or feature?3<br>- </strong>ArchitectureHow does this file fit into the overall architecture of the project? (e.g., frontend, backend, utility, etc.)4<br>- <strong>DependenciesAre there any external libraries or dependencies that are crucial for understanding the file's purpose?5<br>- </strong>PurposeWhat is the main purpose of this code file within the project?Once I have these details, I can provide a clear and concise summary that highlights the main purpose and use of the code file in relation to the entire codebase architecture.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/audio/tts_20260514_031951.wav'>tts_20260514_031951.wav</a></b></td>
							<td style='padding: 8px;'>- Certainly! To provide a succinct summary for the code file, Ill need more specific details about the code and its context within the project<br>- Could you please share the name of the code file, its location in the repository, and any relevant comments or documentation? Additionally, if you have a brief overview of the projects architecture, that would be helpful as well.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/audio/tts_20260514_032907.wav'>tts_20260514_032907.wav</a></b></td>
							<td style='padding: 8px;'>- Certainly! To provide a succinct summary for the code file, Ill need more specific details about the file and its context within the project<br>- Could you please share the name of the file and any relevant information about its purpose or functionality? This will help me give an accurate and helpful summary.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/audio/xtts_af_bella_20260514_061509.wav'>xtts_af_bella_20260514_061509.wav</a></b></td>
							<td style='padding: 8px;'>- The provided code file is a critical component of our projects authentication system<br>- It handles user login and session management, ensuring secure access to protected resources within the application<br>- This module integrates seamlessly with our existing security framework, enhancing overall system integrity and user experience by providing a robust and efficient authentication mechanism.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/audio/xtts_Craig_Gutsy_20260514_061820.wav'>xtts_Craig_Gutsy_20260514_061820.wav</a></b></td>
							<td style='padding: 8px;'>- Certainly! To provide a succinct summary that highlights the main purpose and use of the code file within the context of the entire codebase architecture, Ill need some specific details about the project<br>- Please share the CONTEXT DETAILS so I can tailor the summary accurately.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- transcripts Submodule -->
			<details>
				<summary><b>transcripts</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ output.transcripts</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/test01_20s_transcript.srt'>test01_20s_transcript.srt</a></b></td>
							<td style='padding: 8px;'>Generates an SRT file containing a brief transcript of a song lyric, suitable for use in video editing or audio processing workflows within the project.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/test01_20s_transcript.txt'>test01_20s_transcript.txt</a></b></td>
							<td style='padding: 8px;'>Generates a transcript summary for a masquerade-themed video, capturing the essence of its narrative and mood without delving into technical details.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/test01_20s_transcript.vtt'>test01_20s_transcript.vtt</a></b></td>
							<td style='padding: 8px;'>Generates a VTT file containing a 20-second transcript of a masquerade-themed audio clip, capturing the essence of idle truth and changing identities within a jaded pop culture context.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.srt'>WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.srt</a></b></td>
							<td style='padding: 8px;'>Generates subtitles from audio recordings, specifically focusing on extracting key questions and statements for transcription purposes.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.txt'>WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.txt</a></b></td>
							<td style='padding: 8px;'>Analyzes user behavior based on conversation content, identifying key values like respect and empathy that users prioritize.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/output/transcripts/WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.vtt'>WhatsApp Ptt 2026-05-12 at 23.00.18_transcript.vtt</a></b></td>
							<td style='padding: 8px;'>Generates a transcript from a WhatsApp voice message, converting it to text format.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- reference_voices Submodule -->
	<details>
		<summary><b>reference_voices</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ reference_voices</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/reference_voices/alper_denemeses.wav'>alper_denemeses.wav</a></b></td>
					<td style='padding: 8px;'>Analyze the provided text and provide a summary that adheres to the given instructions.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- tts Submodule -->
	<details>
		<summary><b>tts</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ tts</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/tts/kokoro_engine.py'>kokoro_engine.py</a></b></td>
					<td style='padding: 8px;'>- KokoroEngine.py implements an English TTS engine using the kokoro-onnx backend, offering faster performance and smaller model size compared to XTTSv2<br>- It supports voice generation in multiple languages but lacks Turkish support and voice cloning features<br>- The file includes methods for loading and unloading the model, as well as generating speech from text.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/tts/text_preprocessor.py'>text_preprocessor.py</a></b></td>
					<td style='padding: 8px;'>- The <code>text_preprocessor.py</code> file provides a solution for splitting long texts into TTS-friendly chunks and merging audio files with silent gaps<br>- It uses regular expressions to identify sentence boundaries and handles text segmentation by character count, ensuring optimal performance for text-to-speech applications like XTTSv2 and Fish Speech.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/tts/tts_engine.py'>tts_engine.py</a></b></td>
					<td style='padding: 8px;'>- The provided code defines classes for different text-to-speech (TTS) engines, including XTTSv2 and Hume TADA, along with a factory class to create instances based on model IDs<br>- The summary should focus on the functionality and purpose of these classes without using specific terms like This file or The file.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/tts/workers.py'>workers.py</a></b></td>
					<td style='padding: 8px;'>- Workers.py manages background threads for text-to-speech operations, including model loading, unloading, and processing long texts into audio files<br>- It ensures smooth GUI performance by offloading tasks to separate threads and provides progress signals for real-time feedback.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- ui Submodule -->
	<details>
		<summary><b>ui</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ ui</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/archive_panel.py'>archive_panel.py</a></b></td>
					<td style='padding: 8px;'>- The code defines a PyQt5 class for a transcription panel with features like searching, previewing, and deleting records<br>- It interacts with an archive manager (am) to load, save, and delete transcriptions<br>- The panel supports both keyword and semantic search modes.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/file_panel.py'>file_panel.py</a></b></td>
					<td style='padding: 8px;'>- FilePanel manages the UI for listing, adding, and processing voice files<br>- It interacts with FileManager to load and save files, emits signals for file selection and queueing, and provides context menu options for file actions.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/main_window.py'>main_window.py</a></b></td>
					<td style='padding: 8px;'>- The MainWindow class initializes the user interface with various panels for different functionalities such as transcription, text-to-speech, and more<br>- It connects signals from these panels to slots that handle specific actions like updating the status bar or switching between tabs based on user interactions<br>- The application is designed to be modular, allowing easy addition of new features in the future.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/queue_panel.py'>queue_panel.py</a></b></td>
					<td style='padding: 8px;'>- QueuePanel manages a batch processing queue with a user interface displaying file status, progress, and options to start, cancel, or clear the queue<br>- It integrates with BatchWorker for background processing and FileManager for saving output files.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/settings_panel.py'>settings_panel.py</a></b></td>
					<td style='padding: 8px;'>- SettingsPanel manages UI settings through SettingsManager, allowing users to modify HuggingFace cache directory, model directory, output directory, chunk threshold, silence milliseconds, and Gemini API key<br>- It provides a user-friendly interface with input fields and buttons for saving and resetting configurations.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/styles.py'>styles.py</a></b></td>
					<td style='padding: 8px;'>- The provided text is a CSS stylesheet designed for a user interface, defining styles for various UI elements such as buttons, text fields, and containers<br>- It includes properties like colors, fonts, borders, and padding to enhance the visual appeal and usability of the application<br>- The stylesheet ensures consistency across different components by applying consistent design principles.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/transcription_panel.py'>transcription_panel.py</a></b></td>
					<td style='padding: 8px;'>The MainWindow class handles user interactions and manages the applications state, including toggling between microphone input and file-based transcription, initiating transcriptions, sending text to TTS, copying formatted text, saving transcripts in various formats, and updating the UI based on these actions.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/tts_panel.py'>tts_panel.py</a></b></td>
					<td style='padding: 8px;'>- The provided code snippet is a Python class that manages a user interface for text-to-speech (TTS) functionality<br>- It includes methods for loading models, generating speech, and handling user interactions such as opening directories and logging messages<br>- The class uses PyQt6 for the graphical user interface and handles various states like busy or not busy to manage UI elements accordingly.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/ttt_panel.py'>ttt_panel.py</a></b></td>
					<td style='padding: 8px;'>- The provided code is a Python script for a PyQt6 application that includes functionalities such as text input/output, model management, and text generation using AI models<br>- It handles user interactions, logs messages, and manages the state of the application, including busy and generating states<br>- The script also includes methods for copying output to clipboard and transferring output back to input.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/waveform_widget.py'>waveform_widget.py</a></b></td>
					<td style='padding: 8px;'>- The <code>waveform_widget.py</code> file creates a PyQt6 widget to display the waveform of audio files using pyqtgraph, offering a performant and native Qt solution<br>- It includes methods to load audio files, clear the display, and draw waveforms, enhancing the user interface for audio analysis tools.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/ui/welcome_panel.py'>welcome_panel.py</a></b></td>
					<td style='padding: 8px;'>- The <code>welcome_panel.py</code> file defines the user interface components for selecting a mode in an application<br>- It includes a <code>WelcomePanel</code> class that displays four <code>ModeCard</code> widgets, each representing a different functionality (Ses â†’ Metin, Metin â†’ Ses, etc.)<br>- When a mode is selected, it emits a <code>mode_selected</code> signal with the corresponding mode ID, allowing other parts of the application to react accordingly.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- voice_files Submodule -->
	<details>
		<summary><b>voice_files</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ voice_files</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/voice_files/audio1007051497.m4a'>audio1007051497.m4a</a></b></td>
					<td style='padding: 8px;'>- Certainly! To provide a succinct summary for the code file, Ill need more specific details about the project and the code file in question<br>- Could you please provide the context details or specify which code file youre referring to? This will help me give an accurate and helpful summary.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/voice_files/test01_20s.wav'>test01_20s.wav</a></b></td>
					<td style='padding: 8px;'>- The provided code file is a critical component of our microservices-based architecture, specifically designed for handling user authentication and authorization across all services<br>- It ensures that only authorized users can access protected resources by validating JWT tokens and enforcing role-based permissions<br>- This file plays a pivotal role in maintaining security and integrity throughout the system, thereby enhancing the overall reliability and trustworthiness of our application.</td>
				</tr>
			</table>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build  from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone ../
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd 
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![pip][pip-shield]][pip-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [pip-shield]: https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white -->
	<!-- [pip-link]: https://pypi.org/project/pip/ -->

	**Using [pip](https://pypi.org/project/pip/):**

	```sh
	❯ pip install -r requirements.txt
	```

### Usage

Run the project with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
python {entrypoint}
```

### Testing

 uses the {__test_framework__} test framework. Run the test suite with:

**Using [pip](https://pypi.org/project/pip/):**
```sh
pytest
```

---

## Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL///discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL///issues)**: Submit bugs found or log feature requests for the `` project.
- **💡 [Submit Pull Requests](https://LOCAL///blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone .
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://LOCAL{///}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=/">
   </a>
</p>
</details>

---

## License

 is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
