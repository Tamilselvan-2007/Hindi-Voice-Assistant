import pvporcupine
import sounddevice as sd
import numpy as np

porcupine = pvporcupine.create(keywords=["alexa"])  # temporary

def audio_callback(indata, frames, time, status):
    pcm = (indata[:, 0] * 32768).astype(np.int16)
    keyword_index = porcupine.process(pcm)
    if keyword_index >= 0:
        print("Wake word detected")

with sd.InputStream(
    samplerate=porcupine.sample_rate,
    channels=1,
    dtype="float32",
    blocksize=porcupine.frame_length,
    callback=audio_callback,
):
    print("Listening for wake word...")
    while True:
        pass
