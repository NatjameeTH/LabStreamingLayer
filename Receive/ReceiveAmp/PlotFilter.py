import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# โหลดข้อมูลจากไฟล์ .npy
data = np.load('UnicornSignal.npy')

# ตรวจสอบขนาดของข้อมูล
print(data.shape)

# กำหนดพารามิเตอร์สำหรับ Bandpass filter
low_cutoff = 0.1  # ความถี่ต่ำ (Hz)
high_cutoff = 40  # ความถี่สูง (Hz)
sampling_rate = 1000  # ความถี่การสุ่มตัวอย่าง (Hz)

# สร้าง Bandpass filter
def bandpass_filter(data, low_cutoff, high_cutoff, sampling_rate):
    nyquist = 0.5 * sampling_rate  # Nyquist frequency
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist
    b, a = butter(4, [low, high], btype='band')  # สร้าง filter ประเภท bandpass
    return filtfilt(b, a, data)  # ใช้ filter กับข้อมูล

# กรองข้อมูลในแต่ละช่อง (ถ้าข้อมูลมีหลายช่อง)
filtered_data = []
for i in range(data.shape[0]):
    filtered_channel = bandpass_filter(data[i], low_cutoff, high_cutoff, sampling_rate)
    filtered_data.append(filtered_channel)

# แปลงกลับเป็น NumPy array
filtered_data = np.array(filtered_data)

# พลอตกราฟก่อนและหลังการกรอง
fig, axes = plt.subplots(data.shape[0], 1, figsize=(10, 5 * data.shape[0]), sharex=True)

if data.shape[0] == 1:
    axes = [axes]  # เพื่อให้ axes เป็น list หากมีกราฟแค่กราฟเดียว

# พลอตกราฟทั้งข้อมูลดั้งเดิมและที่กรองแล้ว
for i in range(data.shape[0]):
    axes[i].plot(data[i], label='Original Data', alpha=0.7)
    axes[i].plot(filtered_data[i], label='Filtered Data (Bandpass)', linestyle='--', color='red')
    axes[i].set_title(f'Channel {i+1}')
    axes[i].set_ylabel('Value')
    axes[i].legend()

# แสดงกราฟ
plt.tight_layout()
plt.show()
