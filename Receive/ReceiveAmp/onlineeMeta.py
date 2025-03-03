import numpy as np
import time
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_streams

def main():
    print("🔍 Looking for all streams...")

    # ค้นหาสตรีมทั้งหมด
    all_streams = resolve_streams()

    if not all_streams:
        print("No streams found!")
        return

    # สร้าง list เพื่อเก็บข้อมูลจากสตรีมทั้งหมด
    all_stream_data = []

    # สร้าง Inlet สำหรับแต่ละ stream
    for stream in all_streams:
        print(f"Found stream: {stream.name()} of type {stream.type()}")

        # สร้าง Inlet สำหรับ stream นี้
        inlet = StreamInlet(stream)

        # ตรวจสอบ metadata ของ stream
        signal_info = inlet.info()
        print("Stream metadata info:")
        print(signal_info)

        # ตรวจสอบข้อมูลใน metadata
        desc = signal_info.desc()
        print("Stream description:")
        print(desc)

        # ตรวจสอบข้อมูลช่องสัญญาณ
        ch_list = desc.child("channels")
        channel_names = []

        if ch_list:
            ch_list = ch_list.child("channel")
            while ch_list:
                channel_name = ch_list.child_value('label')  # ดึงชื่อช่องสัญญาณ
                if channel_name:
                    print(f"Channel label: {channel_name}")
                    channel_names.append(channel_name)
                ch_list = ch_list.next_sibling()

        # ถ้าไม่พบช่องสัญญาณใน metadata
        if not channel_names:
            print("No channels found or labels are missing.")
            channel_names = [f"Ch {i+1}" for i in range(inlet.info().channel_count())]

        print(f"All channel names: {channel_names}")

        # เก็บข้อมูลจากแต่ละ stream
        stream_data = []

        # สร้างกราฟแบบแยก subplot ตามจำนวนช่องสัญญาณ
        num_channels = len(channel_names)
        fig, axes = plt.subplots(num_channels, 1, figsize=(10, 4 * num_channels), sharex=True)
        if num_channels == 1:
            axes = [axes]  # กรณีมีช่องสัญญาณเดียว ให้ทำเป็น list

        try:
            # ฟังข้อมูลจาก stream นี้
            while True:
                # รับข้อมูลจาก stream
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f"Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample)  # เก็บ timestamp และ sample

                # หน่วงเวลาเล็กน้อย
                time.sleep(0.05)

                # พล็อตกราฟจากข้อมูลที่เก็บ
                if len(stream_data) > 0:
                    # แยก timestamp และ signal sample
                    timestamps = [data[0] for data in stream_data]
                    signal_values = np.array([data[1:] for data in stream_data])

                    # ล้างค่าก่อนพล็อตใหม่
                    for ax in axes:
                        ax.clear()

                    for i in range(signal_values.shape[1]):
                        axes[i].plot(timestamps, signal_values[:, i], label=f'{channel_names[i]}')
                        axes[i].set_ylabel(f'{channel_names[i]}')
                        axes[i].legend(loc='upper right')

                    axes[-1].set_xlabel('Time (s)')  # ตั้งชื่อแกน X ใน subplot ล่างสุด
                    plt.suptitle('EEG Signal')

                    # ใช้ plt.draw() และ plt.pause() เพื่อให้กราฟอัพเดต
                    plt.draw()
                    plt.pause(0.05)  # Pause เพื่อให้กราฟอัพเดตทันที

        except KeyboardInterrupt:
            print("\n⏹ Program interrupted by user. Saving data...")

            # บันทึกข้อมูลจาก stream นี้ลงใน list หลัก
            if stream_data:
                all_stream_data.append(np.array(stream_data))
            else:
                all_stream_data.append(np.empty((0, num_channels + 1)))  # กรณีไม่มีข้อมูลจาก stream นี้

            break  # ออกจาก loop หลังจากหยุดรับข้อมูลจาก stream นี้

    # บันทึกข้อมูลทั้งหมดจากทุก stream ลงในไฟล์
    if all_stream_data:
        np.save("all_stream_data.npy", all_stream_data)  # บันทึกข้อมูลจากทุก stream
        print("💾 Data saved to 'all_stream_data.npy'.")
    else:
        print("No data collected.")

    plt.show()  # แสดงกราฟสุดท้ายหลังจากออกจาก loop

if __name__ == '__main__':
    main()
