# รับสัญญาณ จาก OpenViBe Acquisition Server (LSL: LabRecorder)
# โดยใช้ Driver -> Generic Oscillator ใช้สร้างคลื่นสัญญาณแบบจำลอง  


import numpy as np
from pylsl import StreamInlet, resolve_streams
import time

def main():
    print("Looking for 'openvibeSignal' and 'openvibeMarkers' streams...")
    signal_streams = resolve_streams()  # ค้นหา streams ทั้งหมด
    marker_streams = resolve_streams()  # ค้นหา streams ทั้งหมด

    # กรอง streams ตามชื่อ
    signal_stream = next((s for s in signal_streams if s.name() == 'openvibeSignal'), None)
    marker_stream = next((s for s in marker_streams if s.name() == 'openvibeMarkers'), None)

    if not signal_stream:
        print("No signal stream found with name 'openvibeSignal'!")
        return
    if not marker_stream:
        print("No marker stream found with name 'openvibeMarkers'!")
        return

    # สร้าง Inlet สำหรับ signal และ marker
    signal_inlet = StreamInlet(signal_stream)
    marker_inlet = StreamInlet(marker_stream)

    # ตรวจสอบจำนวน channel
    signal_info = signal_inlet.info()
    num_channels = signal_info.channel_count()
    print(f"Number of signal channels: {num_channels}")

    print("Streams connected. Listening for data...")

    # สร้าง list เพื่อเก็บข้อมูล
    signal_data = []
    marker_data = []
    unique_markers = set()  # ใช้เก็บ marker ที่ไม่ซ้ำ

    try:
        while True:
            # รับข้อมูลจาก signal (EEG)
            signal_sample, signal_timestamp = signal_inlet.pull_sample(timeout=1.0)
            if signal_sample is not None:
                print(f"Signal - Timestamp: {signal_timestamp:.3f}, Sample: {signal_sample}")
                signal_data.append([signal_timestamp] + signal_sample)  # เก็บ timestamp และ sample

            # รับข้อมูลจาก marker
            marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=1.0)
            if marker_sample is not None:
                marker_value = marker_sample[0]  # Marker จะเป็น string หรือเลข
                if marker_value not in unique_markers:  # ตรวจสอบว่า marker ยังไม่ซ้ำ
                    unique_markers.add(marker_value)  # บันทึก marker ลงใน set
                    print(f"Marker - Timestamp: {marker_timestamp:.3f}, Sample: {marker_sample}")
                    marker_data.append([marker_timestamp, marker_value])  # เก็บ timestamp และ marker

            # หน่วงเวลา
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Saving data...")

        # แปลงลิสต์เป็น NumPy array
        if signal_data:
            signal_array = np.array(signal_data)
        else:
            signal_array = np.empty((0, num_channels + 1))  # เผื่อกรณีไม่มีข้อมูล

        if marker_data:
            marker_array = np.array(marker_data)
        else:
            marker_array = np.empty((0, 2))  # เผื่อกรณีไม่มีข้อมูล

        # บันทึกข้อมูลลงไฟล์
        np.save("signal_data.npy", signal_array)  # บันทึกข้อมูล signal
        np.save("marker_data.npy", marker_array)  # บันทึกข้อมูล marker

        print("Data saved to 'signal_data.npy' and 'marker_data.npy'.")
        return

if __name__ == '__main__':
    main()
