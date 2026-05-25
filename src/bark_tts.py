import os
import re
import time
from pathlib import Path

import numpy as np
from bark import generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from pydub import AudioSegment, effects
import lameenc


# =================================================
# CONFIGURATION
# =================================================

INPUT_FILE = Path("input/input.txt")
OUTPUT_FOLDER = Path("outputs")
BASE_NAME = "audio_generated"

VOICE = "v2/en_speaker_6"
SAMPLE_RATE = 24000
DEFAULT_TEMP = 0.65

NARRATOR_STYLE = (
    "<excited> As an energetic and enthusiastic narrator and professor, explain clearly and engagingly: "
)

# Cache (Windows friendly)
os.environ["XDG_CACHE_HOME"] = str(Path.home() / "bark_cache")
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)


# =================================================
# MODEL LOADING
# =================================================

print("Loading Bark models...")
preload_models()


# =================================================
# UTILITIES
# =================================================

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def segment_sentences(text: str):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def safe_chunk(sentences, max_len=180):
    chunks, current = [], ""

    for s in sentences:
        if len(current) + len(s) <= max_len:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks


# =================================================
# AUDIO PROCESSING
# =================================================

def merge_wavs(wavs, output_path):
    combined = AudioSegment.silent(duration=0)

    for w in wavs:
        audio = AudioSegment.from_wav(w)
        audio = effects.normalize(audio)
        audio = effects.compress_dynamic_range(audio)
        combined += audio

    combined.export(output_path, format="wav")


def wav_to_mp3(input_wav, output_mp3, bitrate=192):
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(SAMPLE_RATE)
    encoder.set_channels(1)
    encoder.set_quality(2)

    with open(input_wav, "rb") as f:
        wav_data = f.read()

    mp3_data = encoder.encode(wav_data)
    mp3_data += encoder.flush()

    with open(output_mp3, "wb") as f:
        f.write(mp3_data)


# =================================================
# STYLE ENGINE
# =================================================

def apply_expressive_markup(text):
    return f"<excited> {text} </excited>" if "!" in text else text


def get_dynamic_temps(text):
    return (0.95, 1.05) if "!" in text else (DEFAULT_TEMP, DEFAULT_TEMP)


# =================================================
# BARK GENERATION
# =================================================

def generate_chunk(text, idx):
    text = NARRATOR_STYLE + text
    text = apply_expressive_markup(text)

    text_temp, waveform_temp = get_dynamic_temps(text)

    for attempt in range(3):
        try:
            print(f"Generating chunk {idx} (attempt {attempt + 1})")

            audio = generate_audio(
                text,
                history_prompt=VOICE,
                text_temp=text_temp,
                waveform_temp=waveform_temp
            )

            if audio is None or len(audio) < 2000:
                raise ValueError("Audio too short")

            audio = np.nan_to_num(audio)
            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

            return audio

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

    raise RuntimeError(f"Failed chunk {idx}")


# =================================================
# MAIN PIPELINE
# =================================================

def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    print("Reading input text...")
    text = load_text(INPUT_FILE)

    print("Splitting sentences...")
    sentences = segment_sentences(text)

    print("Creating chunks...")
    chunks = safe_chunk(sentences)

    print(f"Total chunks: {len(chunks)}")

    wav_files = []

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}/{len(chunks)}")

        audio = generate_chunk(chunk, i + 1)

        wav_path = OUTPUT_FOLDER / f"chunk_{i}.wav"
        write_wav(wav_path, SAMPLE_RATE, audio)

        wav_files.append(str(wav_path))

    print("\nMerging audio...")
    final_wav = OUTPUT_FOLDER / "temp.wav"
    merge_wavs(wav_files, final_wav)

    print("Converting to MP3...")
    final_mp3 = OUTPUT_FOLDER / f"{BASE_NAME}.mp3"
    wav_to_mp3(final_wav, final_mp3)

    print("Cleaning temp files...")
    for w in wav_files:
        os.remove(w)
    os.remove(final_wav)

    print("\nDONE:")
    print(final_mp3)


if __name__ == "__main__":
    main()