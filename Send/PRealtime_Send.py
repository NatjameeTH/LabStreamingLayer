## Plot เป็น กราฟ sine และ Realtime  
## ส่งกราฟไป Lab Recorder
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from pylsl import StreamInfo, StreamOutlet

# ตั้งค่าพารามิเตอร์ของสตรีม EEG
stream_name = "SendEEG_Stream_Online"
stream_type = "EEG"
channel_count = 24
sampling_rate = 100  
channel_format = "float32"

# สร้าง StreamInfo และ StreamOutlet สำหรับ EEG
info = StreamInfo(stream_name, stream_type, channel_count, sampling_rate, channel_format)
outlet = StreamOutlet(info)

# สร้าง StreamInfo และ StreamOutlet สำหรับ Marker
marker_stream_name = "Marker_Stream_Online"
marker_stream_type = "Markers"
marker_info = StreamInfo(marker_stream_name, marker_stream_type, 1, 0, "float32")  # 1 channel, 0 Hz (irregular rate)
marker_outlet = StreamOutlet(marker_info)

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
colors = ['w', 'w', 'w', 'w', 'w', 'w']  # กำหนดสีพื้นฐาน
curves = [plot.plot(pen=pg.mkPen(colors[i % len(colors)], width=2)) for i in range(channel_count)] #หากมีช่องเพิ่มให้วนซ้ำ
data = np.zeros((channel_count, 500))  # Buffer ขนาด 500 จุด
offsets = np.arange(channel_count) * 5  # ทำให้เส้นกราฟแต่ละช่องไม่ทับกัน
time_values = np.linspace(0, 500, 500)  # กำหนดช่วงเวลาเริ่มต้น

# ฟังก์ชันอัปเดตกราฟ
def update_plot():
    global data, time_values

    t = time.time()  # เวลาปัจจุบัน ณ ขณะนั้น 
    freq = 5  # ความถี่ของคลื่นไซน์ (Hz)
    
    # ใช้คลื่นไซน์ความถี่ 5 Hz เหมือนกันทุกช่อง
    signal_values = np.sin(2 * np.pi * freq * t) * np.ones(channel_count)

    # ส่งข้อมูล EEG ไปยัง LSL
    outlet.push_sample(signal_values)

    # เลื่อนข้อมูลให้ช้าลง
    data = np.roll(data, -1, axis=1)
    data[:, -1] = signal_values

    # อัปเดตเส้นกราฟ
    for i in range(channel_count):
        curves[i].setData(time_values, data[i] + offsets[i])

# ฟังก์ชันส่ง Marker ทุก ๆ 5 วินาที และแสดงเป็นเส้นแนวตั้ง
def send_marker():
    global marker_line
    marker_value = [1.0]  # Marker เป็น 1.0
    marker_outlet.push_sample(marker_value)
    print("Marker sent:", time.time())

    # แสดง marker เป็นเส้นแนวตั้ง
    marker_time = time.time() % 500  
    marker_line.setData([marker_time, marker_time], [-5, channel_count * 5], pen=pg.mkPen('r', width=2))

# สร้างเส้น marker
marker_line = plot.plot()

# ตั้งเวลาให้อัปเดตกราฟทุก 1 / sampling_rate วินาที
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(int(1000 / sampling_rate))  # แปลงเป็น milliseconds

# ตั้งเวลาให้ส่ง Marker ทุก 5 วินาที
timer_marker = QtCore.QTimer()
timer_marker.timeout.connect(send_marker)
timer_marker.start(5000)  # 5000 milliseconds = 5 seconds

# เริ่ม GUI event loop
app.exec_()
