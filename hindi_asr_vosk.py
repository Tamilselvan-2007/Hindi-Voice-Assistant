import sounddevice as sd
import queue
import json
import webrtcvad
from vosk import Model, KaldiRecognizer
import collections

SAMPLE_RATE = 48000
FRAME_DURATION = 30  # ms (10, 20, 30 allowed)
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)

vad = webrtcvad.Vad(2)  # 0–3 (2 is balanced)

model = Model("models/vosk-model-small-hi-0.22")
rec = KaldiRecognizer(model, SAMPLE_RATE)

audio_q = queue.Queue()
ring_buffer = collections.deque(maxlen=10)

def callback(indata, frames, time, status):
    audio_q.put(bytes(indata))

def is_speech(frame):
    return vad.is_speech(frame, SAMPLE_RATE)

with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=FRAME_SIZE,
    dtype="int16",
    channels=1,
    callback=callback
):
    print("🎤 बोलिए... (VAD enabled)")
    voiced = False

    while True:
        frame = audio_q.get()

        if is_speech(frame):
            ring_buffer.append(frame)
            voiced = True
            rec.AcceptWaveform(frame)
        else:
            if voiced:
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("📝 पहचाना गया:", text)
                voiced = False
                ring_buffer.clear()
