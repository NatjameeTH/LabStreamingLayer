## Trigger ครั้งเดียว 

import matplotlib.pyplot as plt
import numpy as np

# สมมติว่ามีข้อมูล EEG ที่บันทึกไว้
sampling_rate = 512  # ตัวอย่าง sampling rate
time_points = np.arange(0, 10, 1/sampling_rate)  # 10 วินาที
signal = np.sin(2 * np.pi * 10 * time_points)  # สัญญาณตัวอย่าง (Sine Wave)

# กำหนดตำแหน่งที่ marker เกิดขึ้น
marker_time = 3  # เช่น marker อยู่ที่เวลา 3 วินาที

# สร้างกราฟสัญญาณ
plt.plot(time_points, signal, label='EEG Signal')

# เพิ่ม vertical line สำหรับ marker
plt.axvline(x=marker_time, color='r', linestyle='--', label='Marker Event')

# เพิ่มป้ายกำกับ
plt.title('EEG Signal with Marker')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.legend()

plt.show()

