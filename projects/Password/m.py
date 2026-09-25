import time
import serial
from pynput import keyboard

# ================= Configuration =================
SERIAL_PORT = 'COM4'  
BAUD_RATE = 115200
TARGET_WORD = "pnu12345"
# =================================================

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[CONNECTED] Serial connection established on {SERIAL_PORT}")
except Exception as e:
    print(f"[ERROR] Could not open serial port {SERIAL_PORT}: {e}")
    exit()

current_input = []
press_times = {}

print("=" * 60)
print("System armed and actively monitoring...")
print(f"Target word: [{TARGET_WORD}]")
print("=" * 60)

def on_press(key):
    if key in [keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r]:
        return

    try:
        k = key.char
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
        press_times.pop(key, None)
        return

    try:
        k = key.char
    except AttributeError:
        k = key
        
    p_time = press_times.pop(k, now)

    if key == keyboard.Key.enter:
        entered_word = "".join([str(item['char']) for item in current_input])
        
        if entered_word == TARGET_WORD:
            features = []
            for i in range(len(TARGET_WORD)):
                features.append(current_input[i]['hold'])
            # 2. وقت الانتقال Flight Times (7 ميزات)
            for i in range(len(TARGET_WORD) - 1):
                features.append(current_input[i+1]['press'] - current_input[i]['release'])
            
            features = features[:15]
            
            data_string = ",".join([f"{f:.5f}" for f in features]) + "\n"
            ser.write(data_string.encode())
            print(f"\n[SENT] Sent {len(features)} keystroke dynamics to Arduino...")

            time.sleep(0.15)
            while ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(f"[ARDUINO RESPONSE]: {response}")
        else:
            print(f"\n[IGNORED] Word mismatched: '{entered_word}'")

        current_input = []
    else:
        if k is not None:
            current_input.append({'char': str(k), 'press': p_time, 'release': now, 'hold': now - p_time})

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()