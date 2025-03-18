# รับสัญญาณ จาก Brainmaster Discovery24E  (LSL: LabRecorder)
# Plot กราฟ แบบ Offline ด้วย MatPlotlib

import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

def main():
    print("🔍 Looking for all streams...")

    all_streams = resolve_streams()

    if not all_streams:
        print(" No streams found!")
        return

    all_stream_data = []
    all_channel_names = []

    for stream in all_streams:
        print(f"Found stream: {stream.name()} of type {stream.type()}")

        inlet = StreamInlet(stream)
        signal_info = inlet.info()
        num_channels = signal_info.channel_count()
        print(f" Number of channels: {num_channels}")

        # ดึงชื่อช่องสัญญาณ
        channel_names = []
        ch = signal_info.desc().child("channels").child("channel")
        for i in range(num_channels):
            channel_names.append(ch.child_value("label") or f"CH{i+1}")
            ch = ch.next_sibling()

        all_channel_names.append(channel_names)  # เก็บชื่อช่องไว้สำหรับการพล็อต
        stream_data = []

        try:
            while True:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f" Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample)

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n⏹ Program interrupted by user. Saving data...")

            if stream_data:
                all_stream_data.append(np.array(stream_data))
            else:
                all_stream_data.append(np.empty((0, num_channels + 1)))

            break

    # บันทึกข้อมูล
    if all_stream_data:
        np.save("all_stream_data.npy", all_stream_data)
        print("💾 Data saved to 'all_stream_data.npy'.")
    else:
        print(" No data collected.")

    # วาดกราฟ
    if all_stream_data:
        plt.figure(figsize=(20, 10))
        cmap = plt.colormaps["tab10"]

        # zip เพื่อ รวมข้อมูลสัญญาณ และชื่อช่องสัญญาณ
        for idx, (stream_data, channel_names) in enumerate(zip(all_stream_data, all_channel_names)):
            timestamps = stream_data[:, 0]
            signal_values = stream_data[:, 1:]

            num_channels = signal_values.shape[1]

            #  พล็อตโดยเรียงจากบนลงล่าง
            for i in range(num_channels):
                offset = (num_channels - i - 1) * 30000  # เรียงช่องสัญญาณจากบนลงล่าง
                plt.plot(timestamps, signal_values[:, i] + offset, 
                         label=f'{channel_names[i]}', color=cmap(i % 10))

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('EEG Signals By Brainmaster')
        plt.legend(loc='upper right')
        plt.grid(True)

        # บันทึกกราฟเป็นไฟล์ PNG หลังจาก plot
        plt.savefig('plot.png', dpi=300, bbox_inches='tight')

        # แสดงกราฟ
        plt.show()

if __name__ == '__main__':
    main()