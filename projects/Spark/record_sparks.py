import os
import time
import serial
import numpy as np
from scipy.io import wavfile

# ================= Configuration =================
SERIAL_PORT = 'COM3'      # تأكد من رقم المنفذ في جهازك
BAUD_RATE = 921600
SAMPLE_RATE = 16000
SAMPLE_DURATION = 1.0     # مدة كل عينة (ثانية واحدة)
# =================================================

BYTES_PER_SAMPLE = int(SAMPLE_RATE * SAMPLE_DURATION * 2)

# تثبيت المسار دائماً داخل مجلد السكربت الحالي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    time.sleep(2)
    print(f"[CONNECTED] Connected to ESP32 on {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Could not open {SERIAL_PORT}: {e}")
    exit()

# اختيار الفئة وعدد العينات
category = input("Enter category (spark / noise): ").strip().lower()
target_count = int(input("How many 1-second samples to record? (e.g. 50): ").strip())

TARGET_DIR = os.path.join(BASE_DIR, "dataset", category)
os.makedirs(TARGET_DIR, exist_ok=True)

print("\n" + "=" * 60)
print(f"Target: [{category}] | Samples to capture: {target_count}")
if category == "noise":
    print("Action: Make continuous background noises (talking, typing, fan, clapping).")
else:
    print("Action: Keep generating sparks repeatedly throughout the countdown.")
print("=" * 60)

input("Press [ENTER] to start recording...")

# العد التنازلي للتحضير
for i in range(3, 0, -1):
    print(f"Starting in {i}...", end="\r")
    time.sleep(1)

print("\n>>> RECORDING STARTED! Keep making sounds... <<<")

# تفريغ أي بيانات قديمة متراكمة في المنفذ
ser.reset_input_buffer()

saved_count = 0
session_id = int(time.time())

for i in range(target_count):
    raw_audio = bytearray()
    
    # سحب عينة ثانية واحدة بالضبط
    while len(raw_audio) < BYTES_PER_SAMPLE:
        chunk = ser.read(BYTES_PER_SAMPLE - len(raw_audio))
        if not chunk:
            break
        raw_audio.extend(chunk)

    if len(raw_audio) % 2 != 0:
        raw_audio = raw_audio[:-1]

    if len(raw_audio) < BYTES_PER_SAMPLE * 0.9:
        print(f"[SKIP] Incomplete sample at #{i+1}")
        continue

    audio_array = np.frombuffer(raw_audio, dtype=np.int16)
    
    file_path = os.path.join(TARGET_DIR, f"{category}_{session_id}_{i+1:03d}.wav")
    wavfile.write(file_path, SAMPLE_RATE, audio_array)
    saved_count += 1
    
    print(f"[{category}] Captured sample {saved_count}/{target_count} -> {os.path.basename(file_path)}")

ser.close()
print("\n" + "=" * 60)
print(f"[DONE] Successfully saved {saved_count} samples directly to:")
print(TARGET_DIR)
print("=" * 60)