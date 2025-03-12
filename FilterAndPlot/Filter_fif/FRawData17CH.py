# 
import mne
import pandas as pd
import matplotlib.pyplot as plt  

#  โหลดไฟล์ FIF
raw = mne.io.read_raw_fif("C:\\Users\\s\\Desktop\\NewLSL\\Test1m_raw.fif", preload=True)

# ทำการกรองสัญญาณ notch และ Bandpass
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')


# ใช้ MNE แสดงกราฟ
raw.plot(duration=10, n_channels=17, scalings=10, title='EEG & Misc Signals')

# เซฟกราฟเป็นไฟล์ PNG
plt.savefig("All_หลับ.png")

# แสดงกราฟ วาดกราฟ 2D ผ่าน raw.plot()
plt.show()  # ใช้ plt.show() เพื่อแสดงกราฟ

