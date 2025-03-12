#ไฟล์ที่เก็บจาก python LSL
import mne
import matplotlib.pyplot as plt  

#  โหลดไฟล์ FIF
raw = mne.io.read_raw_fif("C:\\Users\\s\\Desktop\\NewLSL\\LabStreamingLayer\\Python_fif\\eeg_data_Unicorn_raw_หลับ20250304_134357.fif", preload=True)

# ทำการกรองสัญญาณ notch และ Bandpass
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')

# เลือกแค่แชนเนล EEG สำหรับการแสดงผล
raw_eeg = raw.pick_types(eeg=True)

# เลือกแค่ 8 แชนเนลแรกที่ต้องการแสดง
channels_to_display = raw_eeg.info['ch_names'][:8]  # เลือก 8 ช่องแรก
raw_eeg = raw_eeg.pick_channels(channels_to_display)

# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=8, scalings=10000, title='EEG หลับ Signals')

# เซฟกราฟเป็นไฟล์ PNG
plt.savefig("EEG_หลับ_py.png")

# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # เพื่อแสดงกราฟ


