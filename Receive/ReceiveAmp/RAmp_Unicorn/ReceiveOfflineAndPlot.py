# รับสัญญาณ จาก g-tec Unicorn (LSL: LabRecorder)
# Plot กราฟ แบบ Offline ด้วย MatPlotlib

import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

# กำหนดชื่อช่องสัญญาณ
channel_names = [
    'EEG 1', 'EEG 2', 'EEG 3', 'EEG 4', 'EEG 5', 'EEG 6', 'EEG 7', 'EEG 8',
    'Accelerometer X', 'Accelerometer Y', 'Accelerometer Z',
    'Gyroscope X', 'Gyroscope Y', 'Gyroscope Z',
    'Battery Level', 'Counter', 'Validation Indicator'
]

def main():
    print("🔍 Looking for all streams...")

    # ค้นหาสตรีมทั้งหมด 
    all_streams = resolve_streams()

    if not all_streams:
        print(" No streams found!")
        return

    all_stream_data = []  # เก็บข้อมูลจากทุก stream

    # ดึงข้อมูลจากทุก stream
    for stream in all_streams:
        print(f"Found stream: {stream.name()} of type {stream.type()}")

        inlet = StreamInlet(stream)
        signal_info = inlet.info()
        num_channels = signal_info.channel_count()
        print(f" Number of channels: {num_channels}")

        stream_data = []

        try:
            while True:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f" Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample)  # บันทึก timestamp + ค่าข้อมูล

                time.sleep(0.05)  # หน่วงเวลาเล็กน้อย

        # Ctrl+C เพื่อหยุดรับสัญญาณ
        except KeyboardInterrupt:
            print("\n⏹ Program interrupted by user. Saving data...")

            if stream_data:
                all_stream_data.append(np.array(stream_data))
            else:
                all_stream_data.append(np.empty((0, num_channels + 1))) 

            break  

    # บันทึกข้อมูลลงไฟล์
    if all_stream_data:
        np.save("all_stream_data.npy", all_stream_data)
        print("💾 Data saved to 'all_stream_data.npy'.")
    else:
        print(" No data collected.")

    # วาดกราฟแบบไม่ซ้อนกัน
    if all_stream_data:
        plt.figure(figsize=(12, 8))
        cmap = plt.colormaps["tab10"]  # ใช้สีจาก colormap

        for idx, stream_data in enumerate(all_stream_data):
            timestamps = stream_data[:, 0]  
            signal_values = stream_data[:, 1:]  

            signal_values = np.array(signal_values)
            num_channels = signal_values.shape[1]

            for i in range(num_channels):
                offset = (num_channels - i - 1) * 50000  # กำหนด offset ให้เรียงจากบนลงล่าง
                label = channel_names[i] if i < len(channel_names) else f'CH{i+1}'
                plt.plot(timestamps, signal_values[:, i] + offset, label=label, color=cmap(i % 10))

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude ')
        plt.title('EEG Signals By Unicorn')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    main()