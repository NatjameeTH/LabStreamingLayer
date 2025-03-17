import mne
import pandas as pd
import matplotlib.pyplot as plt  

# โหลดข้อมูลจากไฟล์ CSV
df = pd.read_csv("C:\\Users\\BCILAB_QEEG_Com2\\Desktop\\LabStreamingLayer\\UnicornRecorder_2(ขยับตัว)20250304_132815.csv")

# สร้าง Info สำหรับ Channel 
channel_names = ['EEG 1', 'EEG 2', 'EEG 3', 'EEG 4', 'EEG 5', 'EEG 6', 'EEG 7', 'EEG 8', 
                 'Accelerometer X', 'Accelerometer Y', 'Accelerometer Z', 
                 'Gyroscope X', 'Gyroscope Y', 'Gyroscope Z', 
                 'Battery Level', 'Counter', 'Validation Indicator']

sfreq = 250  # ความถี่ในการตัวอย่าง
info = mne.create_info(ch_names=channel_names, sfreq=sfreq, ch_types=['eeg']*8 + ['misc']*9) #misc (miscellaneous) Sensor อื่นๆ

# สร้าง RawArray จากข้อมูลใน CSV
raw = mne.io.RawArray(df.values.T, info)

"""
# สำหรับ Chek ค่าที่ได้ ก่อน plot #

# ดึงข้อมูลทั้งหมดจาก raw object
data = raw.get_data()

# ดึงชื่อช่องทั้งหมด
channel_names = raw.info['ch_names']

# พิมพ์ค่าของแต่ละช่องสัญญาณ
for i, ch_name in enumerate(channel_names):
    print(f"Channel {ch_name} (index {i+1}):")
    # แสดงข้อมูลของแต่ละช่องสัญญาณ
    print(f"{data[i, :10]} ... {data[i, -10:]}")  # แสดงค่าช่องสัญญาณ 10 ค่าแรกและ 10 ค่าสุดท้าย
    print("\n" + "="*50 + "\n")  # คั่นระหว่างช่อง
    
"""

# ทำการกรองสัญญาณ notch และ Bandpass
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')

# เลือกแค่แชนเนล EEG สำหรับการแสดงผล
raw_eeg = raw.pick_types(eeg=True)  # เลือกแชนเนล EEG

# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=17, scalings='1', title='Misc หลับ Signals')


# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # ใช้ plt.show() เพื่อแสดงกราฟ




