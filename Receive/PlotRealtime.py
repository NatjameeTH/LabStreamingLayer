import numpy as np
import math
import pylsl
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import csv
from typing import List

# ค่าคงที่สำหรับการแสดงผล
PLOT_DURATION = 5  
UPDATE_INTERVAL = 60  
PULL_INTERVAL = 500  
CHANNEL_OFFSET = 10  
CSV_FILE_SIGNAL = "signal_data.csv"
CSV_FILE_MARKER = "marker_data.csv"

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
        bufsize = (2 * math.ceil(info.nominal_srate() * PLOT_DURATION), info.channel_count())

        self.buffer = np.empty(bufsize, dtype=np.float32)  
        empty = np.array([])
        self.curves = [pg.PlotCurveItem(x=empty, y=empty, autoDownsample=True) for _ in range(self.channel_count)]
        for i, curve in enumerate(reversed(self.curves)):
            plt.addItem(curve)
            curve.setPos(0, i * CHANNEL_OFFSET)

    def pull_and_plot(self, plot_time, plt):
        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=self.buffer.shape[0])
        if timestamps and samples:
            timestamps = np.array(timestamps)
            y = np.array(samples)

            if y.shape[1] != self.channel_count:
                print(f"Warning: Received {y.shape[1]} channels, expected {self.channel_count}")

            old_offset = 0
            new_offset = 0
            for ch_ix in range(self.channel_count):
                old_x, old_y = self.curves[ch_ix].getData()
                if ch_ix == 0:
                    old_offset = old_x.searchsorted(plot_time)
                    new_offset = timestamps.searchsorted(plot_time)
                    this_x = np.hstack((old_x[old_offset:], timestamps[new_offset:]))
                this_y = np.hstack((old_y[old_offset:], y[new_offset:, ch_ix] - ch_ix))
                self.curves[ch_ix].setData(this_x, this_y)

                self.save_to_csv(timestamps[new_offset:], y[new_offset:, ch_ix], ch_ix)

    # Save แบบ Online เป็น csv ไว้ 
    def save_to_csv(self, timestamps, values, ch_ix):
        with open(CSV_FILE_SIGNAL, mode='a', newline='') as file:
            writer = csv.writer(file)
            for t, v in zip(timestamps, values):
                writer.writerow([t, ch_ix, v])

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
            
            # กำหนดค่าของ Marker ที่ต้องการบันทึก (ตัวอย่าง: "Event 1" หรือค่าหมายเลข)
            marker_value = "Event 1"  # สามารถเปลี่ยนเป็นค่าที่เหมาะสมได้
            self.save_marker_to_csv(closest_ts, marker_value)

    # เพิ่มฟังก์ชัน save_marker_to_csv ใน MarkerInlet
    def save_marker_to_csv(self, timestamp, marker_value):
        with open(CSV_FILE_MARKER, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, marker_value])  # บันทึก Timestamp และ Marker Value



def main():
    inlets: List[Inlet] = []
    print("Looking for streams...")
    streams = pylsl.resolve_streams()

    pw = pg.plot(title='LSL Signal Plot')
    plt = pw.getPlotItem()
   

    for info in streams:
        if info.type() == 'Markers':
            print(f"Adding marker inlet: {info.name()}")
            inlets.append(MarkerInlet(info, plt))
        elif info.nominal_srate() > 0:
            print(f"Adding data inlet: {info.name()}")
            inlets.append(DataInlet(info, plt))
        else:
            print(f"Skipping unknown stream: {info.name()}")

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
