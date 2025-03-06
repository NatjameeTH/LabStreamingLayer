# Plot graph ที่ได้จาก Unicorn 
import pandas as pd
import mne
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

#  1. โหลดข้อมูลจากไฟล์ CSV
df = pd.read_csv("C:\\Users\\s\\Desktop\\NewLSL\\LabStreamingLayer\\Unicorn_csv\\UnicornRecorder_3(หลับ)20250304_133154.csv")

#  2. สร้าง Info สำหรับ MNE
channel_names = ['EEG 1', 'EEG 2', 'EEG 3', 'EEG 4', 'EEG 5', 'EEG 6', 'EEG 7', 'EEG 8', 
                 'Accelerometer X', 'Accelerometer Y', 'Accelerometer Z', 
                 'Gyroscope X', 'Gyroscope Y', 'Gyroscope Z', 
                 'Battery Level', 'Counter', 'Validation Indicator']

sfreq = 250  # ความถี่ตัวอย่าง (Hz)
info = mne.create_info(ch_names=channel_names, sfreq=sfreq, ch_types=['eeg']*8 + ['misc']*9)  # สร้างข้อมูล meta ของ EEG และ Sensor

#  3. สร้าง RawArray จากข้อมูล
raw = mne.io.RawArray(df.values.T, info)

#  4. ตรวจสอบข้อมูลก่อนการกรอง
raw_data_before_filter = raw.get_data()  # ข้อมูลก่อนกรอง
print("Raw Data (ก่อนกรอง) - ตัวอย่าง 10 ค่าแรก:")
print(raw_data_before_filter[:, :10])  # แสดง 10 ค่าแรกในทุกช่อง

#  5. ทำ Notch Filter (50 Hz) และ Bandpass Filter (0.5-30 Hz)
raw.notch_filter(50, fir_design='firwin')
raw.filter(l_freq=0.5, h_freq=30, fir_design='firwin')


#  6. ตรวจสอบข้อมูลหลังการกรอง
raw_data_after_filter = raw.get_data()  # ข้อมูลหลังกรอง
print("Raw Data (หลังกรอง) - ตัวอย่าง 10 ค่าแรก:")
print(raw_data_after_filter[:, :10])  # แสดง 10 ค่าแรกในทุกช่องหลังการกรอง

#  7. Scaling ±50 µV (ถ้าไม่ต้องการการ Scaling ให้ข้ามขั้นตอนนี้)
data = raw_data_after_filter
# data = (raw_data_after_filter / np.max(np.abs(raw_data_after_filter), axis=1, keepdims=True)) * 50  # เอา Scaling ออกแล้วดูผล

#  8. สร้างแกนเวลา
time_axis = np.arange(data.shape[1]) / sfreq  # สร้างแกนเวลาแบบจริงทั้งหมด

#  9. สร้าง GUI PyQtGraph
app = QtWidgets.QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="EEG & Sensor Signals")
win.resize(1200, 1000)
win.setWindowTitle('EEG & Sensor Visualization')

#  10. Loop ผ่านทุกช่อง (เรียงแนวตั้ง 1 คอลัมน์ 17 แถว)
plots = []
first_plot = None  # สร้างตัวแปรสำหรับกราฟแรก

for i, ch_name in enumerate(channel_names):
    plot = win.addPlot(title=f"{ch_name}")  
    plot.plot(time_axis, data[i], pen='b')  # แสดงข้อมูลทั้งหมดตามเวลา
    plot.setLabel('left', 'µV' if 'EEG' in ch_name else 'Value')  
    plot.setYRange(-50, 50)  # ตั้งขอบเขตแกน Y
    
    # เชื่อมโยงแกน X กับกราฟแรก
    if i == len(channel_names) - 1:  # ถ้าเป็นกราฟสุดท้าย (กราฟล่างสุด)
        plot.getAxis('bottom').setVisible(True)  # แสดงแกน X ในกราฟสุดท้าย
    else:
        plot.getAxis('bottom').setVisible(False)  # ซ่อนแกน X ในกราฟอื่นๆ
    
    # เชื่อมโยงแกน X ทุกกราฟให้เหมือนกัน
    if first_plot is None:
        first_plot = plot
    else:
        plot.setXLink(first_plot)  # ให้ทุกกราฟมีแกน X เดียวกัน

    plots.append(plot)
    win.nextRow()  # ทำให้เรียงแนวตั้ง

#  11. แสดงหน้าต่าง PyQtGraph
QtWidgets.QApplication.instance().exec_()
