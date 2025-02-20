
## Plot เป็น กราฟ sine และ Realtime ด้วย 
## ส่งกราฟไป Lab Recorder
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from pylsl import StreamInfo, StreamOutlet

# ✅ ตั้งค่าพารามิเตอร์ของ Stream
stream_name = "EEG_Stream"
stream_type = "EEG"
channel_count = 4
sampling_rate = 70  # ✅ ลดความเร็วอัปเดต
channel_format = "float32"

# ✅ สร้าง StreamInfo และ StreamOutlet
info = StreamInfo(stream_name, stream_type, channel_count, sampling_rate, channel_format)
outlet = StreamOutlet(info)

# ✅ สร้าง GUI
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle("Real-Time EEG Signal")
plot = win.addPlot(title="EEG Data")
plot.setXRange(0, 500, padding=0)  # ✅ ปรับช่วง X ให้รองรับ buffer ใหม่

# ✅ ตั้งค่ากราฟ
plot.setLabel('left', 'Amplitude')
plot.setLabel('bottom', 'Time', units='s')

# ✅ สร้างเส้นกราฟสำหรับ 4 ช่องสัญญาณ
colors = ['w', 'w', 'w', 'w']  
curves = [plot.plot(pen=pg.mkPen(colors[i], width=2)) for i in range(channel_count)]
data = np.zeros((channel_count, 500))  # ✅ ขยาย buffer เป็น 500 จุด
offsets = np.arange(channel_count) * 5  
time_values = np.linspace(0, 500, 500)  # ✅ อัปเดต time_values ให้ตรงกัน

# ✅ ฟังก์ชัน Moving Average
def moving_average(data, window_size=5):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

# ✅ ฟังก์ชันอัปเดตกราฟ
def update_plot():
    global data

    t = time.time()  

    # ✅ ใช้คลื่นความถี่ต่ำลง
    signal_values = [
        np.sin(2 * np.pi * 10 * t),  
        np.sin(2 * np.pi * 15 * t),  
        np.sin(2 * np.pi * 20 * t), 
        np.sin(2 * np.pi * 25 * t)  
    ]
    
    # ✅ ส่งข้อมูลไปยัง LSL
    outlet.push_sample(signal_values)  

    # ✅ เลื่อนข้อมูลให้ช้าลง
    data = np.roll(data, -1, axis=1)  
    data[:, -1] = signal_values  

    # ✅ อัปเดตเส้นกราฟแบบ Smooth
    for i in range(channel_count):
        smoothed_data = moving_average(data[i, :])
        curves[i].setData(time_values[: len(smoothed_data)], smoothed_data + offsets[i])

# ✅ ตั้งเวลาให้อัปเดตกราฟทุก 1 / sampling_rate วินาที
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(int(100 / sampling_rate))  # ✅ ปรับให้รองรับ buffer ใหม่

# ✅ เริ่ม GUI event loop
app.exec_()

