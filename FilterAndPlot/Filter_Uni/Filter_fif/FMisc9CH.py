# Filter สัญญาณที่บันทึกเป็นไฟล์ fif (9 ช่อง)
import mne
import pandas as pd
import matplotlib.pyplot as plt  


#  โหลดไฟล์ FIF
raw = mne.io.read_raw_fif("C:\\Users\\s\\Desktop\\NewLSL\\UnicornFIF\\ขยับตัว_raw.fif", preload=True)

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
raw_eeg = raw.pick_types(eeg=True)

# เลือกแค่ 9 แชนเนลถัดไป (จากช่องที่ 9 ถึงช่องที่ 17)
channels_to_display_next = raw_eeg.info['ch_names'][8:17]  # ช่องที่ 9 ถึง 17
raw_eeg_next = raw_eeg.pick_channels(channels_to_display_next)

# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=9, scalings=10, title='Misc ขยับตัว Signals')

# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # ใช้ plt.show() เพื่อแสดงกราฟ



