import sounddevice as sd
import numpy as np
import queue
import samplerate

# Queues
audio_q = queue.Queue()

# Get mic info
device_info = sd.query_devices(kind='input')
MIC_RATE = int(device_info['default_samplerate'])
TARGET_RATE = 16000

print("Mic sample rate:", MIC_RATE)
print("Target rate:", TARGET_RATE)

# Resampler
resampler = samplerate.Resampler('sinc_fastest', channels=1)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_q.put(indata.copy())

with sd.InputStream(
    samplerate=MIC_RATE,
    channels=1,
    callback=audio_callback
):
    print("🎤 Listening... Press Ctrl+C to stop")

    while True:
        data = audio_q.get()

        # Resample 48k → 16k
        data_16k = resampler.process(data, TARGET_RATE / MIC_RATE)

        # Just show that data is flowing
        print("Received chunk:", data_16k.shape)
