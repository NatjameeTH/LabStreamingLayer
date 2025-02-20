
## save เป็น num.py และ plot กราฟ sine
import pyxdf
import numpy as np
import matplotlib.pyplot as plt
import os

def load_xdf_file(file_path):
    """ โหลดไฟล์ XDF และจัดการข้อผิดพลาด """
    if not os.path.exists(file_path):
        print(f" ไม่พบไฟล์: {file_path}")
        return None, None
    try:
        streams, header = pyxdf.load_xdf(file_path, dejitter_timestamps=True)
        return streams, header
    except Exception as e:
        print(f" ไม่สามารถโหลดไฟล์ XDF ได้: {e}")
        return None, None

def find_eeg_stream(streams):
    """ ค้นหา Stream ที่เป็น EEG """
    for stream in streams:
        if 'type' in stream['info'] and 'EEG' in stream['info']['type']:
            return stream
    return None

def plot_eeg_signal(timestamps, eeg_data, num_channels=4, offset=20, time_window=10):  #time_windowกำหนดช่วงเวลาที่ต้องการ แสดงผลข้อมูล EEG บนกราฟ (หน่วยเวลา)
    """ พล็อตสัญญาณ EEG พร้อมการตั้งค่าขนาดและช่วงเวลา """
    if eeg_data.shape[1] < 2:
        print(" มีข้อมูลไม่เพียงพอสำหรับพล็อต")
        return

    
    plt.figure(figsize=(30, 10))  # ปรับให้ใหญ่ขึ้น
    plt.rcParams.update({'font.size': 14})  # ขยายตัวอักษรในกราฟ

    for i in range(min(num_channels, eeg_data.shape[0])):
        plt.plot(timestamps, eeg_data[i, :] + i * offset, label=f'Channel {i+1}')
    
    plt.xlabel("Time (s)")
    plt.ylabel("EEG Signal (Offset Applied)")
    plt.title("EEG Signal Display")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5)  # กริดชัดขึ้น
    
    # จำกัดช่วงเวลาสำหรับพล็อต
    plt.xlim(timestamps[0], timestamps[0] + time_window)
    plt.show()


#  กำหนดพาธไฟล์ XDF
file_path = ("C:\\Users\\s\\Desktop\\LSL\\sub-19-2\\ses-S002\\eeg\\sub-19-2_ses-S002_task-Default_run-001_eeg.xdf")
#  โหลดไฟล์ XDF
streams, header = load_xdf_file(file_path)
if streams is None:
    exit()

#  เลือก Stream ที่เป็น EEG
eeg_stream = find_eeg_stream(streams)
if eeg_stream is None:
    print(" ไม่พบ Stream EEG ในไฟล์ XDF")
    exit()

#  ดึงข้อมูล EEG และ timestamps
eeg_data = np.array(eeg_stream['time_series']).T  # (channels, samples)
timestamps = np.array(eeg_stream['time_stamps'])  # เวลาของแต่ละตัวอย่าง

#  ตรวจสอบข้อมูล
if eeg_data.size == 0 or timestamps.size == 0:
    print(" ไม่มีข้อมูลใน Stream EEG")
    exit()

#  บันทึกข้อมูล EEG เป็นไฟล์ .npy
np.save("eeg_data.npy", eeg_data)
np.save("timestamps.npy", timestamps)
print(f" บันทึกข้อมูลสำเร็จ! EEG shape: {eeg_data.shape}, Timestamps shape: {timestamps.shape}")

# 📈 แสดงผลสัญญาณ EEG
plot_eeg_signal(timestamps, eeg_data, num_channels=4, offset=20, time_window=10)