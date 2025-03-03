# Online Plot แบบแยกช่อง บอกชื่อ channel "".

import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

def main():
    print("🔍 Looking for all streams...")

    # ค้นหาสตรีมทั้งหมด .
    all_streams = resolve_streams()

    if not all_streams:
        print(" No streams found!")
        return

    # สร้าง list เพื่อเก็บข้อมูลจากสตรีมทั้งหมด
    all_stream_data = []

    # สร้าง Inlet สำหรับแต่ละ stream
    for stream in all_streams:
        print(f"Found stream: {stream.name()} of type {stream.type()}")

        # สร้าง Inlet สำหรับ stream นี้
        inlet = StreamInlet(stream)

        # ตรวจสอบจำนวนช่องสัญญาณของ stream
        signal_info = inlet.info()
        num_channels = signal_info.channel_count()
        print(f" Number of channels: {num_channels}")

        # ดึง metadata ของช่องสัญญาณ
        desc = signal_info.desc()
        ch_list = desc.child("channels").child("channel")

        channel_names = []
        for i in range(num_channels):
            channel_names.append(ch_list.child_value("label"))
            ch_list = ch_list.next_sibling()

        print(" Channel Names:", channel_names)

        # เก็บข้อมูลจากแต่ละ stream
        stream_data = []

        # สร้างกราฟแบบแยก subplot ตามจำนวนช่องสัญญาณ
        fig, axes = plt.subplots(num_channels, 1, figsize=(15, 10 * num_channels), sharex=True)
        if num_channels == 1:
            axes = [axes]  # กรณีมีช่องสัญญาณเดียว ให้ทำเป็น list

        try:
            # ฟังข้อมูลจาก stream นี้
            while True:
                # รับข้อมูลจาก stream
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f" Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample)  # เก็บ timestamp และ sample

                # หน่วงเวลาเล็กน้อย
                time.sleep(0.01)

                # พล็อตกราฟจากข้อมูลที่เก็บ
                if len(stream_data) > 0:
                    # แยก timestamp และ signal sample
                    timestamps = [data[0] for data in stream_data]
                    signal_values = np.array([data[1:] for data in stream_data])

                    # ล้างค่าก่อนพล็อตใหม่
                    for ax in axes:
                        ax.clear()

                    for i in range(signal_values.shape[1]):
                        axes[i].plot(timestamps, signal_values[:, i], label=f'Channel {i+1}')
                        axes[i].set_ylabel(f'Ch {i+1}')
                        axes[i].legend(loc='upper right')

                    axes[-1].set_xlabel('Time (s)')  # ตั้งชื่อแกน X ใน subplot ล่างสุด
                    plt.suptitle('EEG Signal')
                    plt.pause(0.05)  # Pause เพื่อให้กราฟอัพเดตทันที

        except KeyboardInterrupt:
            print("\ Program interrupted by user. Saving data...")

            # บันทึกข้อมูลจาก stream นี้ลงใน list หลัก
            if stream_data:
                all_stream_data.append(np.array(stream_data))
            else:
                all_stream_data.append(np.empty((0, num_channels + 1)))  # กรณีไม่มีข้อมูลจาก stream นี้

            break  # ออกจาก loop หลังจากหยุดรับข้อมูลจาก stream นี้

    # บันทึกข้อมูลทั้งหมดจากทุก stream ลงในไฟล์
    if all_stream_data:
        np.save("UnicornSignal.npy", all_stream_data)  # บันทึกข้อมูลจากทุก stream
        print(" Data saved to 'UnicornSignal.npy'.")
    else:
        print(" No data collected.")

    plt.show()  # แสดงกราฟสุดท้ายหลังจากออกจาก loop

if __name__ == '__main__':
    main()
