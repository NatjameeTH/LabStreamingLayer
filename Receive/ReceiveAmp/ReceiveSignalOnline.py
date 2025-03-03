#รับสัญญาณแบบ Realtime Plot ด้วย MatPlotlib

import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

def main():
    print("🔍 Looking for all streams...")

    # ค้นหาสตรีมทั้งหมด 
    all_streams = resolve_streams()

    if not all_streams:
        print("❌ No streams found!")
        return

    all_stream_data = []  # เก็บข้อมูลจากทุก stream

    for stream in all_streams:
        print(f"✅ Found stream: {stream.name()} of type {stream.type()}")

        inlet = StreamInlet(stream)  # เชื่อมต่อ stream
        signal_info = inlet.info()
        num_channels = signal_info.channel_count()
        print(f"   📊 Number of channels: {num_channels}")

        stream_data = []  # เก็บข้อมูลของ stream นี้
        plt.figure(figsize=(10, 6))  # ตั้งค่าขนาดของกราฟ

        try:
            while True:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f"📡 Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample) 

                time.sleep(0.05)  # หน่วงเวลาเล็กน้อย

                if len(stream_data) > 1:
                    timestamps = np.array([data[0] for data in stream_data])
                    signal_values = np.array([data[1:] for data in stream_data])
                    
                    # กำหนดค่า offset เพื่อลดการทับกันของเส้นสัญญาณ
                    offsets = np.arange(signal_values.shape[1]) * 10

                    plt.clf()
                    for i in range(signal_values.shape[1]):
                        plt.plot(timestamps, signal_values[:, i] + offsets[i], label=f'Channel {i+1}')
                    
                    plt.xlabel('Time (s)')
                    plt.ylabel('Signal Value')
                    plt.title('EEG Signal')
                    plt.legend()
                    plt.pause(0.05)

        except KeyboardInterrupt:
            print("\n⏹ Program interrupted by user. Saving data...")

            if stream_data:
                all_stream_data.append(np.array(stream_data))
            else:
                all_stream_data.append(np.empty((0, num_channels + 1))) 

            break  

    if all_stream_data:
        np.save("all_stream_data.npy", all_stream_data)
        print("💾 Data saved to 'all_stream_data.npy'.")
    else:
        print("❌ No data collected.")

    plt.show()  

if __name__ == '__main__':
    main()
