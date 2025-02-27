#plot แบบ Offline 4 CH

import numpy as np
import matplotlib.pyplot as plt

# โหลดข้อมูลจากไฟล์ .npy
signal_data = np.load('signal_data.npy')  # ไฟล์ข้อมูลสัญญาณ
marker_data = np.load('marker_data.npy')  # ไฟล์ข้อมูล marker

# แยกข้อมูล timestamp และสัญญาณ
timestamps = signal_data[:, 0]  # คอลัมน์แรกคือ timestamp
signals = signal_data[:, 1:]   # คอลัมน์ที่เหลือคือข้อมูลสัญญาณ 

# แยกข้อมูล timestamp และ marker จาก marker_data
marker_timestamps = marker_data[:, 0]  # timestamp ของ marker
marker_labels = marker_data[:, 1]     # label ของ marker

# ตรวจสอบจำนวนช่องสัญญาณ
num_channels = signals.shape[1]
print(f"Number of channels: {num_channels}")

# สร้าง subplot สำหรับแต่ละช่องสัญญาณ
fig, axes = plt.subplots(num_channels, 1, figsize=(12, 20), sharex=True)
fig.suptitle('Signal Display', fontsize=18)

# วนลูปสร้างกราฟสำหรับแต่ละช่องสัญญาณ
for i in range(num_channels):
    axes[i].plot(timestamps, signals[:, i], label=f'Oscillator {i + 1}')
    axes[i].set_ylabel(f'Oscillator {i + 1}')
    axes[i].legend(loc='upper right')
    axes[i].grid(True)

    # เพิ่ม marker เป็นเส้นแนวตั้งในแต่ละช่องสัญญาณ
    for marker_time, marker_label in zip(marker_timestamps, marker_labels):
        axes[i].axvline(x=marker_time, color='green', linestyle='-', alpha=0.7)
        axes[i].text(marker_time, axes[i].get_ylim()[1] * 0.9,  # วาง label บนกราฟ
                     f'{marker_label}', color='red', fontsize=8, rotation=90)

# ตั้งค่าแกน X และแสดงกราฟ
axes[-1].set_xlabel('Time (s)')  # ตั้งชื่อแกน X ที่ subplot สุดท้าย
plt.tight_layout(rect=[0, 0, 1, 0.96])  # ปรับขนาด layout
plt.show()
