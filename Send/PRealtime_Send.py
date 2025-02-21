
## Plot เป็น กราฟ sine และ Realtime  
## ส่งกราฟไป Lab Recorder
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from pylsl import StreamInfo, StreamOutlet

# ตั้งค่าพารามิเตอร์ของ Stream
stream_name = "SendEEG_Stream"
stream_type = "EEG"
channel_count = 4
sampling_rate = 300  # ลดความเร็วอัปเดตเพื่อให้ดูสมูทขึ้น
channel_format = "float32"

# สร้าง StreamInfo และ StreamOutlet
info = StreamInfo(stream_name, stream_type, channel_count, sampling_rate, channel_format)
outlet = StreamOutlet(info)

# สร้าง GUI สำหรับแสดงสัญญาณแบบ Realtime
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle("Real-Time EEG Signal")
plot = win.addPlot(title="EEG Data")
plot.setXRange(0, 500, padding=0)

# ตั้งค่ากราฟ
plot.setLabel('left', 'Amplitude')
plot.setLabel('bottom', 'Time', units='s')

# สร้างเส้นกราฟ 4 ช่องสัญญาณ
colors = ['w', 'w', 'w', 'w']
curves = [plot.plot(pen=pg.mkPen(colors[i], width=2)) for i in range(channel_count)]
data = np.zeros((channel_count, 500))  # Buffer ขนาด 500 จุด
offsets = np.arange(channel_count) * 5  # ทำให้เส้นกราฟแต่ละช่องไม่ทับกัน
time_values = np.linspace(0, 500, 500)  # กำหนดช่วงเวลาเริ่มต้น

# ฟังก์ชันอัปเดตกราฟ
def update_plot():
    global data, time_values

    t = time.time()
    
    # กำหนดให้ทุกช่องใช้สัญญาณไซน์ที่เหมือนกัน
    freq = 5  # ความถี่ของสัญญาณ (5 Hz)
    signal_values = np.sin(2 * np.pi * freq * t) * np.ones(channel_count)
    
    # ส่งข้อมูลไปยัง LSL
    outlet.push_sample(signal_values)

    # เลื่อนข้อมูลให้ช้าลง
    data = np.roll(data, -1, axis=1)
    data[:, -1] = signal_values

    # อัปเดตเส้นกราฟ
    for i in range(channel_count):
        curves[i].setData(time_values, data[i] + offsets[i])

# ตั้งเวลาให้อัปเดตกราฟทุก 1 / sampling_rate วินาที
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(int(1000 / sampling_rate))  # แปลงเป็น milliseconds

# เริ่ม GUI event loop
app.exec_()
