# Bark TTS Generator 🎙️

Text-to-speech generator using Suno Bark with intelligent chunking, expressive narration, and automatic MP3 export.

---

## Features

- AI voice generation using Bark
- Intelligent sentence chunking
- Expressive narration mode
- Automatic WAV merging
- MP3 export (LAME encoder)
- Retry system for robustness

---

## Project Structure


bark-tts-generator/
├── src/bark_tts.py
├── input/input.txt
├── outputs/
├── requirements.txt
└── README.md


---

## Installation

```bash
pip install -r requirements.txt
Usage
Put your text inside:
input/input.txt
Run:
python src/bark_tts.py
Output:
outputs/audio_generated.mp3
Requirements
Python 3.9+
FFmpeg recommended
GPU optional (faster generation)
How it works
Splits text into sentences
Groups into safe chunks
Generates audio per chunk with Bark
Applies expressive style
Merges audio segments
Exports final MP3
Future improvements
Voice selection UI
Batch processing
Subtitle generation (SRT sync)
Web API (FastAPI)
Real-time streaming TTS
License

MIT


---

# 🚫 .gitignore

```txt
outputs/
__pycache__/
*.wav
*.mp3
bark_cache/