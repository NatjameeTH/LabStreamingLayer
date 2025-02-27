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

        # เก็บข้อมูลจากแต่ละ stream
        stream_data = []

        try:
            # ฟังข้อมูลจาก stream นี้
            while True:
                # รับข้อมูลจาก stream
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample is not None:
                    print(f" Signal - Timestamp: {timestamp:.3f}, Sample: {sample}")
                    stream_data.append([timestamp] + sample)  # เก็บ timestamp และ sample

                # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ CPU ใช้งานหนักเกินไป
                time.sleep(0.05)

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
        print(" No data collected.")

    # พล็อตกราฟหลังจากบันทึกข้อมูลทั้งหมด
    if all_stream_data:
        plt.figure(figsize=(20, 16))
        
        # ใช้การปรับแกน Y ให้แสดงชื่อช่องสัญญาณ
        for idx, stream_data in enumerate(all_stream_data):
            timestamps = stream_data[:, 0]  # Timestamp อยู่ในคอลัมน์แรก
            signal_values = stream_data[:, 1:]  # ข้อมูลสัญญาณเริ่มจากคอลัมน์ที่ 2

            # แปลง signal_values เป็น numpy array
            signal_values = np.array(signal_values)

            # สร้างกราฟสำหรับข้อมูลแต่ละ stream
            for i in range(signal_values.shape[1]):
                # ใช้ label เป็น CH1, CH2, ...
                channel_name = f'CH{i+1}'
                
                # แสดงเพียงแค่ชื่อช่องสัญญาณบนแกน Y (ไม่แสดง amplitude)
                # เพิ่มค่า i เพื่อย้ายกราฟแต่ละช่องให้ไม่ซ้อนกัน
                plt.plot(timestamps, signal_values[:, i] + i, label=channel_name)

        plt.xlabel('Time (s)')
        plt.ylabel('Channels')
        plt.title('EEG Signals')
        
        # ตั้งค่า Y ticks ให้แสดงชื่อช่องสัญญาณ
        plt.yticks(np.arange(signal_values.shape[1]) + 0.5, [f'CH{i+1}' for i in range(signal_values.shape[1])])  
        
        plt.legend()
        plt.show()  # แสดงกราฟ

if __name__ == '__main__':
    main()
