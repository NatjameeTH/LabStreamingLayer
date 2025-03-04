import numpy as np
import mne
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from typing import List
from datetime import datetime  # เพิ่มการใช้ datetime สำหรับ timestamp

PLOT_DURATION = 5  # จำนวนวินาทีของข้อมูลที่จะแสดง
UPDATE_INTERVAL = 60  # ระยะเวลาที่จะใช้ในการอัปเดตกราฟ ms
PULL_INTERVAL = 500  # ระหว่างการดำเนินการดึงแต่ละครั้ง ms
CHANNEL_OFFSET = 5000  # เพิ่มระยะห่างระหว่างช่องสัญญาณให้มากขึ้น


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
        self.saved = False
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # ใช้ timestamp สำหรับตั้งชื่อไฟล์

        # แสดงชื่อของช่องสัญญาณ EEG
        self.channel_names = [f"EEG {i+1}" for i in range(self.channel_count)]
        print(f"Channels: {self.channel_names}")  # แสดงชื่อช่องสัญญาณ EEG

        bufsize = (int(2 * np.ceil(info.nominal_srate() * PLOT_DURATION)), info.channel_count())
        self.buffer = np.empty(bufsize, dtype=np.float32)
        empty = np.array([])

        # ปรับ Curve ให้สัญญาณแต่ละช่องไม่ทับกัน
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count)]
        for i, curve in enumerate(self.curves):
            plt.addItem(curve)
            curve.setPos(0, (i + 1) * CHANNEL_OFFSET)  # เพิ่มระยะห่างระหว่างช่องสัญญาณ
            curve.setPen(pg.mkPen(color=pg.intColor(i), width=0.5))  # ลดความหนาของเส้น 

    def pull_and_plot(self, plot_time, plt):
        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=self.buffer.shape[0])
        if timestamps and samples:
            timestamps = np.array(timestamps)
            y = np.array(samples)

            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                old_x, old_y = self.curves[ch_ix].getData()
                if ch_ix == 0:
                    old_offset = old_x.searchsorted(plot_time)
                    new_offset = timestamps.searchsorted(plot_time)
                    this_x = np.hstack((old_x[old_offset:], timestamps[new_offset:]))

                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] + ch_ix * CHANNEL_OFFSET))
                self.curves[ch_ix].setData(this_x, this_y, skipFiniteCheck=True)

            if not self.saved:
                self.save_to_mne(timestamps, y)
                self.saved = True

    def save_to_mne(self, timestamps, values):
        ch_names = [f'EEG {i+1}' for i in range(self.channel_count)]
        info = mne.create_info(ch_names, self.srate, ch_types='eeg')
        raw_data = np.transpose(values)

        raw = mne.io.RawArray(raw_data, info)

        # เพิ่ม timestamp ในชื่อไฟล์เพื่อไม่ให้เซฟทับ
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw.save(f"eeg_data_{self.name}_raw_{timestamp_str}.fif", overwrite=True)


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
            # เรียกใช้ฟังก์ชันบันทึก Marker แต่ไม่เซฟ CSV
            # self.save_marker_to_csv(closest_ts, marker_value)

    def save_marker_to_csv(self, timestamp, marker_value):
        # คอมเมนต์ฟังก์ชันนี้เพื่อไม่ให้บันทึก Marker ลง CSV
        pass


def main():
    inlets: List[Inlet] = []
    print("Looking for streams...")
    streams = pylsl.resolve_streams()

    pw = pg.plot(title='LSL Data Plot')
    pw.setBackground('k')  
    pw.setGeometry(100, 100, 1200, 800)
    plt = pw.getPlotItem()

    for info in streams:
        print(f"Adding data inlet: {info.name()} of type {info.type()}")
        if info.type() == 'Markers':
            inlets.append(MarkerInlet(info, plt))  
        else:
            inlets.append(DataInlet(info, plt))  

    def scroll():
        plot_time = pylsl.local_clock()
        pw.setXRange(plot_time - PLOT_DURATION, plot_time)

    def update():
        plot_time = pylsl.local_clock() - PLOT_DURATION
        for inlet in inlets:
            inlet.pull_and_plot(plot_time, plt)

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
