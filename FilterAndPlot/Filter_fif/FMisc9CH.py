
#ไฟล์ที่เก็บจาก python LSL
import mne
import pandas as pd
import matplotlib.pyplot as plt  


#  โหลดไฟล์ FIF
raw = mne.io.read_raw_fif("C:\\users\\s\\Desktop\\NewLSL\\LabStreamingLayer\\Python_fif\\eeg_data_Unicorn_raw_นั่งนิ่ง20250304_135321.fif", preload=True)

# ทำการกรองสัญญาณ notch และ Bandpass
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')


# เลือกแค่แชนเนล EEG สำหรับการแสดงผล
raw_eeg = raw.pick_types(eeg=True)

# เลือกแค่ 9 แชนเนลถัดไป (จากช่องที่ 9 ถึงช่องที่ 17)
channels_to_display_next = raw_eeg.info['ch_names'][8:17]  # ช่องที่ 9 ถึง 17
raw_eeg_next = raw_eeg.pick_channels(channels_to_display_next)

# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=9, scalings=50, title='Misc นั่งนิ่ง Signals')

# เซฟกราฟเป็นไฟล์ PNG
plt.savefig("Misc_นั่งนิ่ง_py.png")

# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # ใช้ plt.show() เพื่อแสดงกราฟ



