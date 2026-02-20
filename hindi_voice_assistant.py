import queue
import sys
import sounddevice as sd
import vosk
import json
import os
import datetime
import numpy as np
import time
from vosk import Model, KaldiRecognizer


# =========================
# GLOBAL FLAGS
# =========================
is_speaking = False

# =========================
# SOUND EFFECTS
# =========================
def play_tone(frequency,duration=0.15):
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(tone.astype(np.float32), samplerate=sample_rate, blocking=True)


    
def play_listen_end_sound():
    play_tone(600)

def play_done_sound():
    play_tone(400)

# =========================
# AUDIO SETTINGS
# =========================
MIC_RATE = 48000
VOSK_RATE = 16000
FRAME_SIZE = 4000
DEVICE_ID = 1

WAKE_WORDS = [
    "निरंजन",
    "निरञ्जन",
    "निरंजन",
    "हे निरंजन","निरंतर"]
WAIT_AFTER_WAKE = 5

q = queue.Queue(maxsize=30)

# =========================
# LOAD VOSK MODEL
# =========================
model_path = "models/vosk-model-small-hi-0.22"
model = Model(model_path)

# =========================
# CLEAR AUDIO QUEUE
# =========================
def clear_audio_queue():
    while not q.empty():
        q.get()

# =========================
# HINDI DATE FORMATTER
# =========================
def get_hindi_date():
    months = {
        "January": "जनवरी", "February": "फ़रवरी", "March": "मार्च",
        "April": "अप्रैल", "May": "मई", "June": "जून",
        "July": "जुलाई", "August": "अगस्त", "September": "सितंबर",
        "October": "अक्टूबर", "November": "नवंबर", "December": "दिसंबर"
    }
    day = time.strftime("%d")
    month_en = time.strftime("%B")
    year = time.strftime("%Y")
    month_hi = months.get(month_en, month_en)
    return f"{day} {month_hi} {year}"

# =========================
# SPEAK FUNCTION
# =========================
def speak(text):
    global is_speaking
    is_speaking = True
    print("🤖 जवाब:", text)
    os.system(f'espeak-ng -v hi -s 135 -p 55 -a 120 "{text}"')
    play_done_sound()
    clear_audio_queue()
    is_speaking = False

# =========================
# COMMAND PROCESSOR (Improved)
# =========================
def process_command(text):

    # Simple one-keyword commands dictionary
    COMMANDS = {
        "ताजमहल": "ताजमहल आगरा में स्थित है",
        "प्रधानमंत्री": "भारत के प्रधानमंत्री नरेंद्र मोदी हैं",
        "राजधानी": "भारत की राजधानी नई दिल्ली है",
        "राष्ट्रीय खेल": "भारत का कोई आधिकारिक राष्ट्रीय खेल नहीं है",
        "सबसे लंबी नदी": "दुनिया की सबसे लंबी नदी नील नदी है",
        "आज़ादी": "भारत को आज़ादी पंद्रह अगस्त उन्नीस सौ सैंतालीस को मिली थी",
        "जनसंख्या": "भारत की जनसंख्या लगभग एक सौ चालीस करोड़ है",
        "मौसम": "माफ़ कीजिए, लाइव मौसम जानकारी के लिए इंटरनेट कनेक्शन आवश्यक है",
        "होटल": "पास के होटल की जानकारी के लिए इंटरनेट कनेक्शन आवश्यक है",
        "सोने का रेट": "सोने का आज का रेट जानने के लिए इंटरनेट आवश्यक है",
        "डीजल": "डीजल का वर्तमान दाम जानने के लिए इंटरनेट आवश्यक है",
        "सरकारी योजना": "भारत सरकार की कई योजनाएँ हैं जैसे उज्ज्वला योजना, जन धन योजना और आयुष्मान भारत",
        "किसान योजना": "प्रधानमंत्री किसान सम्मान निधि योजना के तहत किसानों को आर्थिक सहायता दी जाती है",
        "मोटिवेशन": "सफलता उन्हीं को मिलती है जो मेहनत करने से नहीं डरते"
    }

    # Check dictionary-based commands
    for key, response in COMMANDS.items():
        if key in text:
            speak(response)
            return

    # Multi-condition commands (kept as original logic)
    if "चाँद" in text and "पहला" in text:
        speak("चाँद पर पहला इंसान नील आर्मस्ट्रांग थे")
        
    elif "कौन हो" in text:
        speak("मैं निरंजन हूँ, मैं आपकी सहायता के लिए बना हूँ")

    elif "एक दिन" in text and "घंटे" in text:
        speak("एक दिन में चौबीस घंटे होते हैं")

    elif "एक मिनट" in text and "सेकंड" in text:
        speak("एक मिनट में साठ सेकंड होते हैं")

    elif "किलोमीटर" in text and "मीटर" in text:
        speak("एक किलोमीटर में एक हज़ार मीटर होते हैं")

    elif "किलो" in text and "ग्राम" in text:
        speak("एक किलो में एक हज़ार ग्राम होते हैं")

    elif "लीटर" in text and "मिलीलीटर" in text:
        speak("एक लीटर में एक हज़ार मिलीलीटर होते हैं")

    elif "समय" in text:
        current_time = time.strftime("%H:%M")
        speak(f"अभी समय है {current_time}")

    elif "तारीख" in text:
        speak(f"आज की तारीख है {get_hindi_date()}")

    elif "कौन सा दिन" in text:
        today_day = time.strftime("%A")
        speak(f"आज {today_day} है")

    elif "अगला रविवार" in text:
        today = time.localtime()
        days_ahead = 6 - today.tm_wday
        if days_ahead <= 0:
            days_ahead += 7
        next_sunday = time.strftime("%d %B %Y", time.localtime(time.time() + days_ahead * 86400))
        speak(f"अगला रविवार {next_sunday} को है")

    elif "100 डॉलर" in text or "डॉलर" in text:
        speak("सौ डॉलर लगभग आठ हज़ार तीन सौ रुपये होते हैं")

    else:
       speak("माफ़ कीजिए, क्या आप फिर से कह सकते हैं?")

# =========================
# AUDIO CALLBACK
# =========================
def callback(indata, frames, time_info, status):
    if status:
        print("⚠", status)

    audio_data = np.frombuffer(indata, dtype=np.int16)
    audio_data = audio_data[::3]
    q.put(audio_data.tobytes())

# =========================
# LISTEN WITH TIMEOUT
# =========================
def listen_with_timeout(seconds):

    recognizer = KaldiRecognizer(model, VOSK_RATE)
    start_time = time.time()

    while True:
        if time.time() - start_time > seconds:
            return None

        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                return text

# =========================
# MAIN LOOP (UNCHANGED)
# =========================
# =========================
# MAIN LOOP (UNCHANGED)
# =========================
print("🎤 Hindi Voice Assistant Started...")
print("Wake word:निरंजन ")

play_tone(700, duration=0.3)
time.sleep(0.1)
play_tone(900, duration=0.3)
speak("मॉडल तैयार है")

with sd.RawInputStream(
    samplerate=MIC_RATE,
    blocksize=FRAME_SIZE,
    dtype="int16",
    channels=1,
    callback=callback,
    device=DEVICE_ID,
    latency='high'
):

    recognizer = KaldiRecognizer(model, VOSK_RATE)

    while True:

        if is_speaking:
            continue

        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                print("📝 पहचाना गया:", text)

                if any(word in text for word in WAKE_WORDS):

                    print("👂 Wake word detected... waiting for command")
                    speak("हाँ, बताइए।")
                    clear_audio_queue()

                    command = listen_with_timeout(WAIT_AFTER_WAKE)

                    if command:
                        print("🗣 Command:", command)
                        play_listen_end_sound()
                        process_command(command)

                        # 🔁 Continuous conversation mode (10 seconds)
                        while True:
                            clear_audio_queue()
                            next_command = listen_with_timeout(10)

                            if next_command:
                                print("🗣 Next Command:", next_command)
                                play_listen_end_sound()
                                process_command(next_command)
                            else:
                                play_done_sound()  # beep and exit
                                break

                    else:
                        speak("जी बताइए")

                        clear_audio_queue()
                        command = listen_with_timeout(5)

                        if command:
                            print("🗣 Command:", command)
                            play_listen_end_sound()
                            process_command(command)
                        else:
                            print("No Response, Waiting for Keyword")
                            play_listen_end_sound()
