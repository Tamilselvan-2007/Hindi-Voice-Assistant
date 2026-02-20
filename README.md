# Hindi Voice Assistant — Niranjan (निरंजन)

An offline, wake-word-activated Hindi voice assistant built for Raspberry Pi. It listens passively for the wake word **"निरंजन"**, processes spoken Hindi commands entirely on-device, and responds using synthesized Hindi speech — no internet connection required.

---

## Table of Contents

- [Project Structure](#project-structure)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Audio Device Configuration](#audio-device-configuration)
- [Running the Assistant](#running-the-assistant)
- [Running Without a Monitor (systemd Service)](#running-without-a-monitor-systemd-service)
- [Wake Word](#wake-word)
- [Supported Commands](#supported-commands)
- [Text-to-Speech Configuration](#text-to-speech-configuration)
- [Model Fine-Tuning Details](#model-fine-tuning-details)
- [Known Limitations](#known-limitations)

---

## Project Structure

```
Hindi_Voice_Assistant_Project/
├── hindi_voice_assistant.py     # Main assistant — wake word detection, command loop
├── assistant_core.py            # Intent detection and response generation
├── hindi_asr_vosk.py            # ASR module with Voice Activity Detection (VAD)
├── wakeword_test.py             # Standalone wake-word detection test
├── stream_test.py               # Audio stream and resampling diagnostic tool
├── models/
│   └── vosk-model-small-hi-0.22/   # Vosk offline Hindi ASR model
└── asr-env/                         # Python virtual environment
```

---

## System Requirements

**Hardware**

- Raspberry Pi 3B+ or newer
- USB microphone or compatible audio input device
- Speaker or 3.5mm audio output

**Operating System**

- Raspberry Pi OS (Debian-based), 32-bit or 64-bit

**System Packages**

```bash
sudo apt update
sudo apt install espeak-ng portaudio19-dev python3-venv
```

**Python**

- Python 3.8 or higher

**Python Dependencies**

| Package | Purpose |
|---|---|
| `vosk` | Offline Hindi speech recognition |
| `sounddevice` | Audio input/output handling |
| `numpy` | Audio data processing |
| `webrtcvad` | Voice Activity Detection |
| `samplerate` | Audio resampling (48kHz to 16kHz) |

---

## Installation

**Step 1 — Navigate to the project directory**

```bash
cd Hindi_Voice_Assistant_Project
```

**Step 2 — Create and activate the virtual environment**

```bash
python3 -m venv asr-env
source asr-env/bin/activate
```

**Step 3 — Install Python dependencies**

```bash
pip install vosk sounddevice numpy webrtcvad samplerate
```

**Step 4 — Download the Vosk Hindi model**

Download `vosk-model-small-hi-0.22` from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) and place it under:

```
Hindi_Voice_Assistant_Project/models/vosk-model-small-hi-0.22/
```

---

## Audio Device Configuration

To find the correct audio input device ID for your microphone, run the following in Python:

```python
import sounddevice as sd
print(sd.query_devices())
```

Update the `DEVICE_ID` variable in `hindi_voice_assistant.py` to match your microphone's index.

The following audio parameters can also be adjusted based on your hardware:

| Parameter | Default | Description |
|---|---|---|
| `MIC_RATE` | 48000 | Raw microphone sample rate (Hz) |
| `VOSK_RATE` | 16000 | Vosk model input rate (Hz) |
| `FRAME_SIZE` | 4000 | Audio frame block size |
| `DEVICE_ID` | 1 | Audio input device index |
| `WAIT_AFTER_WAKE` | 5 | Seconds to wait for a command after wake word |

---

## Running the Assistant

Activate the virtual environment and launch the main script:

```bash
source asr-env/bin/activate
python hindi_voice_assistant.py
```

On startup, the assistant plays two confirmation tones and speaks **"मॉडल तैयार है"** to confirm it is ready. From that point, it continuously monitors audio for the wake word.

---

## Running Without a Monitor (systemd Service)

To run the assistant automatically at boot on a headless Raspberry Pi (no monitor, no login session), set it up as a systemd service.

**Step 1 — Create the service file**

```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

Paste the following content:

```ini
[Unit]
Description=Hindi Voice Assistant
After=network.target sound.target

[Service]
Type=simple
WorkingDirectory=/home/voice-assistant
ExecStart=/home/voice-assistant/asr-env/bin/python /home/voice-assistant/hindi_voice_assistant.py
Restart=always
User=voice-assistant

[Install]
WantedBy=multi-user.target
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

**Step 2 — Reload systemd and enable the service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service
```

**Useful service management commands**

```bash
# Check service status
sudo systemctl status voice-assistant.service

# View live logs
journalctl -u voice-assistant.service -f

# Stop the service
sudo systemctl stop voice-assistant.service

# Restart the service
sudo systemctl restart voice-assistant.service
```

---

## Wake Word

The assistant listens continuously for the wake word **"निरंजन"**. Once detected, it responds with **"हाँ, बताइए"** and enters command-listening mode.

Recognized wake word variants (to account for ASR variation):

- निरंजन
- निरञ्जन
- हे निरंजन
- निरंतर

After a command is processed, the assistant enters a **10-second continuous conversation window**, allowing follow-up questions without repeating the wake word. If no further input is received within that window, it returns to passive listening.

---

## Supported Commands

**General Knowledge**

| Spoken Query (approximate) | Response |
|---|---|
| ताजमहल | ताजमहल आगरा में स्थित है |
| प्रधानमंत्री | भारत के प्रधानमंत्री नरेंद्र मोदी हैं |
| राजधानी | भारत की राजधानी नई दिल्ली है |
| आज़ादी | भारत को आज़ादी पंद्रह अगस्त उन्नीस सौ सैंतालीस को मिली |
| जनसंख्या | भारत की जनसंख्या लगभग एक सौ चालीस करोड़ है |
| चाँद पर पहला इंसान | नील आर्मस्ट्रांग |

**Date and Time**

| Query | Response |
|---|---|
| समय | Current system time |
| तारीख | Today's date in Hindi |
| कौन सा दिन | Current day of the week |
| अगला रविवार | Date of the upcoming Sunday |

**Unit Conversions**

| Query | Response |
|---|---|
| एक दिन में घंटे | चौबीस घंटे |
| एक मिनट में सेकंड | साठ सेकंड |
| किलोमीटर में मीटर | एक हज़ार मीटर |
| किलो में ग्राम | एक हज़ार ग्राम |
| लीटर में मिलीलीटर | एक हज़ार मिलीलीटर |
| डॉलर | सौ डॉलर लगभग आठ हज़ार तीन सौ रुपये |

**Government Schemes**

| Query | Response |
|---|---|
| सरकारी योजना | उज्ज्वला योजना, जन धन योजना, आयुष्मान भारत |
| किसान योजना | पीएम किसान सम्मान निधि |

**Self-Identification**

Asking **"कौन हो"** returns: _"मैं निरंजन हूँ, मैं आपकी सहायता के लिए बना हूँ"_

---

## Text-to-Speech Configuration

The assistant uses **eSpeak-NG** for Hindi voice output. The following parameters have been tuned for clarity on small speakers:

```bash
espeak-ng -v hi -s 135 -p 55 -a 120 "नमस्ते, मैं आपकी सहायता कर सकता हूँ।"
```

| Parameter | Value | Meaning |
|---|---|---|
| `-v hi` | hi | Hindi voice selection |
| `-s 135` | 135 | Speech speed (words per minute) |
| `-p 55` | 55 | Pitch level |
| `-a 120` | 120 | Volume amplitude |

This configuration produces clear pronunciation at a natural pace, audible on low-power speakers typically paired with Raspberry Pi setups.

---

## Model Fine-Tuning Details

**Objective**

Optimize the assistant for natural Hindi conversation, reliable wake-word activation, fast response generation, and low-latency operation on Raspberry Pi hardware.

**Customizations Applied**

- Adjusted speech recognition sensitivity for Hindi phonetics
- Reduced background noise threshold using WebRTC VAD at sensitivity level 2 (balanced)
- Set a 10-second continuous conversation timeout to allow natural follow-up queries
- Integrated multi-variant wake-word matching to handle ASR inconsistencies with "निरंजन"
- Tuned eSpeak-NG speed, pitch, and amplitude for comfortable listening on small speakers
- Implemented audio queue flushing after each TTS response to prevent stale audio from being misidentified as a new command

---

## Known Limitations

- Live weather, hotel search, diesel/gold prices, and other real-time queries require an internet connection and are not supported in the current offline build.
- Currency conversion rates (e.g., USD to INR) are hardcoded and not updated dynamically.
- The assistant recognizes a fixed set of commands. Unrecognized queries receive a fallback response asking the user to repeat.
- ASR accuracy may vary depending on microphone quality, background noise, and speaker accent.

---

## Module Overview

| File | Role |
|---|---|
| `hindi_voice_assistant.py` | Entry point — manages wake word loop, command dispatch, and audio I/O |
| `assistant_core.py` | Keyword-based intent detection and static response generation |
| `hindi_asr_vosk.py` | Standalone ASR module with VAD for speech boundary detection |
| `wakeword_test.py` | Test script for validating wake-word detection pipeline |
| `stream_test.py` | Diagnostic script to verify audio input and resampling |

---

*Built for offline, low-resource Hindi voice interaction on Raspberry Pi.*
