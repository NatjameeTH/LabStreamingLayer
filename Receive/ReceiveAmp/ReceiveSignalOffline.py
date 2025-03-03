# #รับสัญญาณแบบ Online Plot ด้วย MatPlotlib
import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

def main():
    print("🔍 Looking for all streams...")

    # ค้นหาสตรีมทั้งหมด (ไม่มี timeout)
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
        plt.figure(figsize=(12, 6))
        cmap = plt.colormaps["tab10"]  # หรือใช้ plt.colormaps.get_cmap("tab10")  # ใช้สีจาก colormap

        for idx, stream_data in enumerate(all_stream_data):
            timestamps = stream_data[:, 0]  
            signal_values = stream_data[:, 1:]  

            signal_values = np.array(signal_values)
            num_channels = signal_values.shape[1]

            for i in range(num_channels):
                offset = i * 10  # เพิ่ม offset ทีละ 10 หน่วยให้แต่ละช่อง
                plt.plot(timestamps, signal_values[:, i] + offset, label=f'CH{i+1}', color=cmap(i % 10))

        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude (with offset)')
        plt.title('EEG Signals')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    main()
