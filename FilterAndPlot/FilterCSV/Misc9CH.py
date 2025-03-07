
import mne
import pandas as pd
import matplotlib.pyplot as plt  

# โหลดข้อมูลจากไฟล์ CSV
df = pd.read_csv("C:\\users\\s\\Desktop\\NewLSL\\LabStreamingLayer\\Unicorn_csv\\UnicornRecorder_3(หลับ)20250304_133154.csv")

# สร้าง Info สำหรับ Channel 
channel_names = ['EEG 1', 'EEG 2', 'EEG 3', 'EEG 4', 'EEG 5', 'EEG 6', 'EEG 7', 'EEG 8', 
                 'Accelerometer X', 'Accelerometer Y', 'Accelerometer Z', 
                 'Gyroscope X', 'Gyroscope Y', 'Gyroscope Z', 
                 'Battery Level', 'Counter', 'Validation Indicator']

sfreq = 250  # ความถี่ในการตัวอย่าง
info = mne.create_info(ch_names=channel_names, sfreq=sfreq, ch_types=['eeg']*8 + ['misc']*9) #misc (miscellaneous) Sensor อื่นๆ

# สร้าง RawArray จากข้อมูลใน CSV
raw = mne.io.RawArray(df.values.T, info)

# ทำการกรองสัญญาณ notch และ Bandpass
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')

# เลือกแค่แชนเนล EEG สำหรับการแสดงผล
raw_eeg = raw.pick_types(misc=True)

# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=9, scalings='1', title='Misc หลับ Signals')

# เซฟกราฟเป็นไฟล์ PNG
plt.savefig("Misc_หลับ.png")

# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # ใช้ plt.show() เพื่อแสดงกราฟ



