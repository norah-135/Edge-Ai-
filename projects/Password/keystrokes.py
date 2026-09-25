import os
import time
import csv
from pynput import keyboard

TARGET_WORD = "pnu12345"
SAMPLES_COUNT = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "my_keystrokes.csv")

dataset = []
current_input = []
press_times = {}

print("=" * 60)
print(f"Target Word: [{TARGET_WORD}]")
print("Make sure your keyboard language is set to ENGLISH.")
print(f"Please type the word and press [ENTER] after each attempt.")
print(f"Attempt 1 of {SAMPLES_COUNT}: Type now...")
print("=" * 60)

AR_TO_EN = {
    'ح': 'p', 'ى': 'n', 'ع': 'u',
    '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5',
    '٦': '6', '٧': '7', '٨': '8', '٩': '9', '٠': '0'
}

def normalize_char(k):
    return AR_TO_EN.get(k, k)

def on_press(key):
    if key in [keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r]:
        return

    try:
        k = key.char
        if k is not None:
            k = normalize_char(k)
    except AttributeError:
        k = key

    if k not in press_times:
        press_times[k] = time.time()

def on_release(key):
    global current_input
    now = time.time()

    if key in [keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r]:
        return

    if key == keyboard.Key.backspace:
        if current_input:
            current_input.pop()
            typed_so_far = "".join([item['char'] for item in current_input])
            print(f"Current input: {typed_so_far}   ", end="\r")
        press_times.pop(key, None)
        return

    try:
        k = key.char
        if k is not None:
            k = normalize_char(k)
    except AttributeError:
        k = key
        
    p_time = press_times.pop(k, now)
    
    if key == keyboard.Key.enter:
        entered_word = "".join([str(item['char']) for item in current_input])
        
        if entered_word == TARGET_WORD:
            features = []
            # 8 أوقات ضغط (Hold Times)
            for i in range(len(TARGET_WORD)):
                features.append(current_input[i]['hold'])
            # 7 أوقات انتقال (Flight Times)
            for i in range(len(TARGET_WORD) - 1):
                f_time = current_input[i+1]['press'] - current_input[i]['release']
                features.append(f_time)
            
            # التأكد من حفظ 15 ميزة بالضبط
            features = features[:15]
            dataset.append(features)
            
            print(f"\n[SUCCESS] Recorded attempt {len(dataset)}/{SAMPLES_COUNT} -> '{entered_word}'")
            
            if len(dataset) < SAMPLES_COUNT:
                print(f"--> Next attempt ({len(dataset) + 1}/{SAMPLES_COUNT}): Type now...")
        else:
            print(f"\n[ERROR] Typed: '{entered_word}' | Expected: '{TARGET_WORD}'. Try again.")
            
        current_input = []
        press_times.clear()
        
        if len(dataset) >= SAMPLES_COUNT:
            return False
    else:
        if k is not None:
            current_input.append({'char': str(k), 'press': p_time, 'release': now, 'hold': now - p_time})
            typed_so_far = "".join([item['char'] for item in current_input])
            print(f"Current input: {typed_so_far}   ", end="\r")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

with open(CSV_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(dataset)

print("\n" + "=" * 60)
print(f"[COMPLETED] All {SAMPLES_COUNT} samples saved successfully to:\n{CSV_PATH}")
print("=" * 60)