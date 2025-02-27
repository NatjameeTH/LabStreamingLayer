#Plot_Offline ได้ทุก amp
import numpy as np
import matplotlib.pyplot as plt

# โหลดข้อมูลจากไฟล์
signal_data = np.load('signal_data.npy')  # ไฟล์ข้อมูลสัญญาณจาก Amp
marker_data = np.load('marker_data.npy')  # ไฟล์ข้อมูล marker

# แยกข้อมูล timestamp และสัญญาณ
timestamps = signal_data[:, 0]  # คอลัมน์แรกคือ timestamp
signals = signal_data[:, 1:]   # คอลัมน์ที่เหลือคือข้อมูลสัญญาณ 

# แยกข้อมูล marker
marker_timestamps = marker_data[:, 0]
marker_labels = marker_data[:, 1]

# ตรวจสอบจำนวนช่องสัญญาณ
num_channels = signals.shape[1]
print(f"Detected {num_channels} channels.")

# สร้างสีให้แต่ละช่อง
colors = plt.get_cmap('tab10')(np.linspace(0, 1, num_channels))

# ปรับ Offset ให้ตรงกับหมายเลขช่อง (CH 1, CH 2, CH 3, …)
offsets = np.arange(num_channels, 0, -1) * 6  # กำหนดค่าเพื่อเว้นระยะ

# สร้าง Figure
plt.figure(figsize=(12, 8))
plt.title(f'EEG Signal Display ({num_channels} Channels)', fontsize=16)

# Plot ทุกสัญญาณในกราฟเดียวกัน
for i in range(num_channels):
    plt.plot(timestamps, signals[:, i] + offsets[i], label=f'CH {i+1}', color=colors[i])

# เพิ่ม marker เป็นเส้นแนวตั้ง
for marker_time, marker_label in zip(marker_timestamps, marker_labels):
    plt.axvline(x=marker_time, color='green', linestyle='-', alpha=0.7)
    plt.text(marker_time, offsets[0] + 2, f'{marker_label}', color='red', fontsize=8, rotation=90)

# ตั้งค่าแกน Y ให้แสดงหมายเลข Channel
plt.yticks(offsets, [f'CH {i+1}' for i in range(num_channels)])
plt.xlabel('Time (s)')
plt.ylabel('Channel')
plt.legend(loc='upper right', fontsize=8)
plt.grid(True, linestyle='--', alpha=0.5)

plt.show()
