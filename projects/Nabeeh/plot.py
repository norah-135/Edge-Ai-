import serial
import matplotlib.pyplot as plt
from collections import deque
import numpy as np

SERIAL_PORT = "COM6"  # تأكدي من رقم المنفذ
BAUD = 115200

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

MAX_POINTS = 50
ambient_data = deque(maxlen=MAX_POINTS)
object_data = deque(maxlen=MAX_POINTS)
delta_data = deque(maxlen=MAX_POINTS)

plt.style.use('dark_background')
fig, (ax_graph, ax_bar) = plt.subplots(1, 2, figsize=(10, 5), gridspec_kw={'width_ratios': [4, 1]})

plt.ion()
plt.show()

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line or "," not in line:
            continue
        
        parts = line.split(",")
        if len(parts) == 3:
            amb, obj, delta = float(parts[0]), float(parts[1]), float(parts[2])
            
            ambient_data.append(amb)
            object_data.append(obj)
            delta_data.append(delta)

            # تحديث الرسم البياني الزمني
            ax_graph.clear()
            ax_graph.plot(ambient_data, label="Ambient Temp (°C)", color="cyan", linestyle="--")
            ax_graph.plot(object_data, label="Object Temp (°C)", color="orange", linewidth=2)
            ax_graph.set_title("Thermal Signature Profile", color="white")
            ax_graph.set_ylabel("Temperature (°C)")
            ax_graph.set_ylim(15, 45)
            ax_graph.legend(loc="upper left")
            ax_graph.grid(True, alpha=0.3)

            # تحديث شريط التنبيه الحراري (Gauge)
            ax_bar.clear()
            bar_color = 'red' if delta > 3.0 else ('yellow' if delta > 1.0 else 'green')
            ax_bar.bar(["Delta T"], [delta], color=bar_color, width=0.4)
            ax_bar.set_ylim(-2, 12)
            ax_bar.set_ylabel("ΔT = Object - Ambient (°C)")
            ax_bar.set_title("Biological Heat", color="white")
            ax_bar.grid(True, axis='y', alpha=0.3)

            fig.canvas.draw_idle()
            fig.canvas.flush_events()

except KeyboardInterrupt:
    ser.close()
    print("تم الإيقاف.")