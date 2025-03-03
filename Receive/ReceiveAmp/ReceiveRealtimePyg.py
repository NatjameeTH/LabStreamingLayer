import numpy as np
import mne
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import csv
from typing import List

# ค่าคงที่สำหรับการแสดงผล
PLOT_DURATION = 5  # ระยะเวลาที่จะแสดงผล (วินาที)
UPDATE_INTERVAL = 60  # มิลลิวินาที
PULL_INTERVAL = 500  # มิลลิวินาที
CHANNEL_OFFSET = 210  # ปรับเพื่อไม่ให้กราฟซ้อนทับกัน
CSV_FILE_SIGNAL = "eeg_signal_data_Unicorn.csv"  # กำหนดชื่อไฟล์สำหรับข้อมูลสัญญาณ EEG
CSV_FILE_MARKER = "marker_data.csv"      # กำหนดชื่อไฟล์สำหรับข้อมูล Marker

class Inlet:
    def __init__(self, info: pylsl.StreamInfo):
        self.inlet = pylsl.StreamInlet(
            info,
            max_buflen=PLOT_DURATION,
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,
        )
        self.name = info.name()
        self.channel_count = info.channel_count()

class DataInlet(Inlet):
    def __init__(self, info: pylsl.StreamInfo, plt: pg.PlotItem):
        super().__init__(info)
        self.srate = info.nominal_srate()
        
        # แปลงผลลัพธ์จาก np.ceil ให้เป็น int ก่อนใช้
        bufsize = (int(2 * np.ceil(info.nominal_srate() * PLOT_DURATION)), info.channel_count())

        self.buffer = np.empty(bufsize, dtype=np.float32)
        empty = np.array([])
        
        # สร้าง curve สำหรับทุกช่องสัญญาณ 17 ช่อง
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(17)]
        for i, curve in enumerate(self.curves):
            plt.addItem(curve)
            curve.setPos(0, i * CHANNEL_OFFSET)  # เพิ่มค่า CHANNEL_OFFSET เพื่อให้ช่องไม่ทับกัน
            curve.setPen(pg.mkPen(color='w'))  # สีขาว  
            curve.opts['name'] = f"Channel {i+1}"  # ตั้งชื่อช่องให้แต่ละ curve

    def pull_and_plot(self, plot_time, plt):
        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=self.buffer.shape[0])
        if timestamps and samples:
            timestamps = np.array(timestamps)
            y = np.array(samples)

            # ตรวจสอบว่าได้รับข้อมูลช่องสัญญาณตามที่คาดไว้
            if y.shape[1] != self.channel_count:
                print(f"Warning: Received {y.shape[1]} channels, expected {self.channel_count}")

            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                old_x, old_y = self.curves[ch_ix].getData()

                if ch_ix == 0:
                    old_offset = old_x.searchsorted(plot_time)
                    new_offset = timestamps.searchsorted(plot_time)
                    this_x = np.hstack((old_x[old_offset:], timestamps[new_offset:]))  # กำหนดค่า x ให้กับกราฟ

                # ตรวจสอบช่องที่ไม่ได้รับข้อมูล
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix if ch_ix < y.shape[1] else np.zeros_like(timestamps[new_offset:])))
                self.curves[ch_ix].setData(this_x, this_y)

                self.save_to_csv(timestamps[new_offset:], y[new_offset:, ch_ix], ch_ix)

            # แปลงข้อมูลที่ได้เป็น RawArray สำหรับ MNE
            self.save_to_mne(timestamps, y)

    def save_to_csv(self, timestamps, values, ch_ix):
        with open(CSV_FILE_SIGNAL, mode='a', newline='') as file:
            writer = csv.writer(file)
            for t, v in zip(timestamps, values):
                writer.writerow([t, ch_ix, v])

    def save_to_mne(self, timestamps, values):
        # สร้างข้อมูล MNE RawArray
        ch_names = [f'EEG {i+1}' for i in range(self.channel_count)]  # ตั้งชื่อช่อง EEG
        info = mne.create_info(ch_names, self.srate, ch_types='eeg')
        raw_data = np.transpose(values)  # ต้องการให้ข้อมูลเป็นรูปแบบ (channels, samples)

        # สร้าง RawArray และบันทึกเป็นไฟล์
        raw = mne.io.RawArray(raw_data, info)
        raw.save(f"eeg_data_{self.name}.fif", overwrite=True)

class MarkerInlet(Inlet):
    def __init__(self, info: pylsl.StreamInfo, plt):
        super().__init__(info)
        self.marker_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='green', width=2))
        plt.addItem(self.marker_line)

    def pull_and_plot(self, plot_time, plt):
        strings, timestamps = self.inlet.pull_chunk(timeout=0.0)
        if timestamps:
            closest_ts = min(timestamps, key=lambda ts: abs(ts - plot_time))
            self.marker_line.setPos(closest_ts)
            marker_value = "Event 1"
            self.save_marker_to_csv(closest_ts, marker_value)

    def save_marker_to_csv(self, timestamp, marker_value):
        with open(CSV_FILE_MARKER, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, marker_value])

def main():
    inlets: List[Inlet] = []
    print("Looking for streams...")
    streams = pylsl.resolve_streams()  # ค้นหา streams ทั้งหมดที่มีในระบบ

    pw = pg.plot(title='LSL Data Plot')
    pw.setBackground('k')  # ตั้งพื้นหลังเป็นสีดำ
    plt = pw.getPlotItem()

    for info in streams:
        # ไม่กรองประเภท stream ใดๆ ให้รับทุก stream ที่พบ
        print(f"Adding data inlet: {info.name()} of type {info.type()}")
        if info.type() == 'Markers':
            inlets.append(MarkerInlet(info, plt))  # เพิ่ม MarkerInlet สำหรับ Marker stream
        else:
            inlets.append(DataInlet(info, plt))  # เพิ่ม DataInlet สำหรับ stream อื่นๆ (EEG, Sensor, อื่นๆ)

    # แสดงข้อมูลชื่อ stream และช่องสัญญาณ
    for inlet in inlets:
        if isinstance(inlet, DataInlet):
            print(f"Stream {inlet.name} has {inlet.channel_count} channels.")
            for i, curve in enumerate(inlet.curves):
                print(f"  Channel {i + 1}: {curve.opts.get('name', 'Unnamed channel')}")
        elif isinstance(inlet, MarkerInlet):
            print(f"Marker Stream {inlet.name}")

    def scroll():
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - PLOT_DURATION, plot_time)  # ตั้งค่าให้กราฟเลื่อนตามเวลา

    def update():
        plot_time = pylsl.local_clock() - PLOT_DURATION
        for inlet in inlets:
            inlet.pull_and_plot(plot_time, plt)  # ดึงข้อมูลจากแต่ละ stream

    update_timer = QtCore.QTimer()
    update_timer.timeout.connect(scroll)
    update_timer.start(UPDATE_INTERVAL)

    pull_timer = QtCore.QTimer()
    pull_timer.timeout.connect(update)
    pull_timer.start(PULL_INTERVAL)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()

if __name__ == "__main__":
    main()
