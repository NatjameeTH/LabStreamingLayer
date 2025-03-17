# รับสัญญาณ จาก Brainmaster Discovery24E (LSL: LabRecorder)
# Plot กราฟ แบบ Real-time ด้วย pyqtgraph


import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from typing import List
import mne
import datetime
import os

# ค่าคงที่สำหรับการแสดงผล
PLOT_DURATION = 5  # จำนวนวินาทีของข้อมูลที่จะแสดงในแต่ละครั้ง (5 วินาทีล่าสุด)
UPDATE_INTERVAL = 60  #กราฟจะถูกรีเฟรชหรืออัปเดตทุกๆ 60 ms
PULL_INTERVAL = 500  
CHANNEL_OFFSET = 6000 
FIF_FILE = "Test_raw.fif"

class Inlet:
    def __init__(self, info: pylsl.StreamInfo):
        self.inlet = pylsl.StreamInlet(
            info,
            max_buflen=PLOT_DURATION,
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,
        )
        self.name = info.name()
        self.channel_count = info.channel_count()

#buffer คือตัวเก็บ list ข้อมูล
class DataInlet(Inlet):
    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        self.srate = info.nominal_srate()
        bufsize = (2 * math.ceil(info.nominal_srate() * PLOT_DURATION), info.channel_count())
        self.buffer = np.empty(bufsize, dtype=np.float32)
        empty = np.array([])

        # กำหนดชื่อช่องสัญญาณตาม BrainMaster 24Ch
        self.channel_names = [
            'Fp1', 'F3', 'C3', 'P3', 'O1', 'F7', 'T3', 'T5',
            'Fz', 'Fp2', 'F4', 'C4', 'P4', 'O2', 'F8', 'T4', 
            'T6', 'Cz', 'Pz', 'A2', 'Fpz', 'Oz', 'AUX1', 'AUX2'
        ]
        self.channel_count = len(self.channel_names)  # กำหนดจำนวนช่องสัญญาณ

        print(f"Channels: {self.channel_names}")  # แสดงชื่อช่องสัญญาณที่เรากำหนดเอง

        
        # สร้าง curve สำหรับแต่ละ channel
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count)]
        for i, curve in enumerate((self.curves)): # ไม่ใช้ reversed
            plt.addItem(curve)
            curve.setPos(0, (i + 1) * CHANNEL_OFFSET)  # เพิ่มระยะห่างระหว่างช่องสัญญาณ
            curve.setPen(pg.mkPen(color=pg.intColor(i), width=0.5))  # ลดความหนาของเส้น 
        
        self.data = []  # เก็บข้อมูลทั้งหมด



    def pull_and_plot(self, plot_time, plt):
        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=self.buffer.shape[0])
        
        #  พิมพ์ค่าของ samples และ timestamps ที่ได้รับมา
        #print(f"Raw samples: {samples}")
        #print(f"Raw timestamps: {timestamps}")

        if timestamps and samples:
            timestamps = np.array(timestamps)
            y = np.array(samples)  # แปลงเป็น numpy array เพื่อให้สามารถจัดการได้ง่าย
            
                  
            # ตรวจสอบขนาดของข้อมูล
            print(f"Shape of timestamps: {timestamps.shape}")
            print(f"Shape of y: {y.shape}")

            if y.shape[1] != self.channel_count:
                print(f"Warning: Received {y.shape[1]} channels, expected {self.channel_count}")

            # ขยายข้อมูลเก่าใน buffer และเพิ่มข้อมูลใหม่
            # zip รวมหรือจับคู่ข้อมูลจาก timestamps และ y (ซึ่งอาจจะเป็นลิสต์หรือ iterable อื่น ๆ) 
            self.data.extend(zip(timestamps, y))  # เพิ่มข้อมูลใหม่ใน self.data

            # พิมพ์ข้อมูลที่ถูกเพิ่มเข้าไปใน self.data
            print(f"Extended data (first 5 entries): {list(zip(timestamps, y))[:5]}")

            # อัปเดตข้อมูลใน curves
            for ch_ix in range(self.channel_count):
                old_x, old_y = self.curves[ch_ix].getData()

                # พิมพ์ขนาดของ old_x และ old_y
                print(f"Channel {ch_ix} - old_x shape: {old_x.shape}, old_y shape: {old_y.shape}")

                # สร้าง new_x และ new_y โดยการเชื่อมข้อมูลเก่าและข้อมูลใหม่
                new_x = np.hstack((old_x, timestamps))  # เพิ่ม timestamps ใหม่
                new_y = np.hstack((old_y, y[:, ch_ix]))  # เพิ่มข้อมูลใหม่ของช่องที่ ch_ix

                #  พิมพ์ขนาดของ new_x และ new_y
                print(f"Channel {ch_ix} - new_x shape: {new_x.shape}, new_y shape: {new_y.shape}")

                # อัปเดตข้อมูลใน curve
                self.curves[ch_ix].setData(new_x, new_y)

class MarkerInlet(Inlet):
    def __init__(self, info: pylsl.StreamInfo, plt):
        super().__init__(info)
        self.marker_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='green', width=2))
        plt.addItem(self.marker_line)
        self.markers = []

    def pull_and_plot(self, plot_time, plt):
        strings, timestamps = self.inlet.pull_chunk(timeout=0.0)
        if timestamps:
            closest_ts = min(timestamps, key=lambda ts: abs(ts - plot_time))
            self.marker_line.setPos(closest_ts)
            marker_value = "Event 1"
            self.markers.append((closest_ts, marker_value))


def save_to_mne(data_inlets, marker_inlets):
    # ใช้ชื่อช่องสัญญาณจาก data_inlets[0].channel_names
    info = mne.create_info(
        ch_names=data_inlets[0].channel_names,  # ใช้ชื่อที่กำหนดไว้ใน channel_names
        sfreq=data_inlets[0].srate,
        ch_types="eeg"
    )

    # ตรวจสอบข้อมูลก่อนสร้าง RawArray
    all_data = []
    for di in data_inlets:
        if len(di.data) > 0:
            timestamps, values = zip(*di.data)  # แยก timestamps และ values ออกจากกัน
            all_data.append(np.array(values).T)  # Transpose เพื่อให้เป็น (n_channels, n_samples)

    if not all_data:
        print("No valid data to save.")
        return

    # รวมข้อมูลทุกช่องสัญญาณเข้าด้วยกัน
    raw_data = np.hstack(all_data)  # รวมข้อมูลแนวแกนเวลาให้เป็น (n_channels, n_samples)

    # ตรวจสอบว่า raw_data มีขนาดถูกต้อง
    if raw_data.shape[0] != len(info["ch_names"]):
        print(f"Warning: Number of channels ({raw_data.shape[0]}) does not match info ({len(info['ch_names'])})")

    raw = mne.io.RawArray(raw_data, info)

    # แสดงข้อมูลช่องสัญญาณที่บันทึก
    for idx, ch_name in enumerate(info["ch_names"]):
        # แสดงค่าช่องสัญญาณ
        print(f"Channel {ch_name} (index {idx}):")
        print(f"{raw_data[idx, :10]} ... {raw_data[idx, -10:]}")  # แสดงค่าช่องสัญญาณ 10 ค่าแรกและ 10 ค่าสุดท้าย
        print()  # เพื่อให้แต่ละช่องสัญญาณแยกจากกัน

    # จัดการ Marker annotations เหตุการณ์
    annotations = []
    for marker in marker_inlets:
        for ts, val in marker.markers:
            annotations.append((ts, 0, val))

    if annotations:
        onset, duration, description = zip(*annotations)
        raw.set_annotations(mne.Annotations(onset, duration, description))

    # ตรวจสอบว่าไฟล์มีอยู่แล้วหรือไม่
    if os.path.exists(FIF_FILE):
        # ถ้ามีไฟล์อยู่แล้ว เปลี่ยนชื่อไฟล์ใหม่ โดยเพิ่ม timestamp
        new_file_name = FIF_FILE.replace(".fif", f"_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.fif")
        raw.save(new_file_name, overwrite=True)
        print(f"Saved data to {new_file_name}")
    else:
        raw.save(FIF_FILE, overwrite=True)
        print(f"Saved data to {FIF_FILE}")



def main():
    inlets: List[Inlet] = []
    print("Looking for streams...")
    streams = pylsl.resolve_streams()

    pw = pg.plot(title='LSL Signal Plot')
    plt = pw.getPlotItem()
    data_inlets = []
    marker_inlets = []

    for info in streams:
        if info.type() == 'Markers':
            print(f"Adding marker inlet: {info.name()}")
            mi = MarkerInlet(info, plt)
            inlets.append(mi)
            marker_inlets.append(mi)
        elif info.nominal_srate() > 0:
            print(f"Adding data inlet: {info.name()}")
            di = DataInlet(info, plt)
            inlets.append(di)
            data_inlets.append(di)
        else:
            print(f"Skipping unknown stream: {info.name()}")

    def scroll():
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - PLOT_DURATION, plot_time)

    def update():
        plot_time = pylsl.local_clock() - PLOT_DURATION
        for inlet in inlets:
            inlet.pull_and_plot(plot_time, plt)

    def on_app_quit():
        save_to_mne(data_inlets, marker_inlets)


    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(UPDATE_INTERVAL)

    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(PULL_INTERVAL)

    
    # เชื่อมต่อกับฟังก์ชัน save_to_fif ก่อนปิดโปรแกรม
    app = QtGui.QGuiApplication.instance()
    app.aboutToQuit.connect(on_app_quit)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()

    save_to_mne(data_inlets, marker_inlets)

if __name__ == "__main__":
    main()