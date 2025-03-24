#Plot sine graph และ Marker
#ข้อมูลที่ Plot มาจากไฟล์ SendData.py 
import pyxdf
import numpy as np
import matplotlib.pyplot as plt
import os

def load_xdf_file(file_path):
    """ โหลดไฟล์ XDF """
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

def find_marker_stream(streams):
    """ ค้นหา Stream ที่เป็น Marker """
    for stream in streams:
        if 'type' in stream['info'] and 'Markers' in stream['info']['type']:
            return stream
    return None

def plot_eeg_signal(timestamps, eeg_data, num_channels=24, time_window=10, markers=None):
    """ พล็อตสัญญาณ EEG พร้อมการตั้งค่าขนาดและช่วงเวลา """
    if eeg_data.shape[1] < 2:
        print("มีข้อมูลไม่เพียงพอสำหรับพล็อต")
        return

    plt.figure(figsize=(35, 14))  # ขยายขนาดกราฟ
    plt.rcParams.update({'font.size': 14})

    channel_labels = [f'CH {i+1}' for i in range(num_channels)]
    offset = 1.5  # ปรับ offset แยกเส้นกราฟแต่ละช่อง

    # พล็อต EEG signal โดยเพิ่ม offset ให้แต่ละช่อง
    for i in range(min(num_channels, eeg_data.shape[0])):
        plt.plot(timestamps, eeg_data[i, :] + i * offset, label=f'CH {i+1}')

    # พล็อต marker event
    if markers is not None:
        for marker in markers:
            plt.axvline(x=marker, color='r', linestyle='--', label='Marker Event' if marker == markers[0] else "")

    plt.xlabel("Time (s)")
    plt.ylabel("Channel")
    plt.title("EEG Signal with Markers")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.9)
    
    # กำหนดช่วงเวลาแสดงผล
    plt.xlim(timestamps[0], timestamps[0] + time_window)
    
    # ปรับแกน Y ให้สอดคล้องกับช่องสัญญาณ
    plt.yticks(np.arange(0, num_channels * offset, offset), labels=channel_labels)

    plt.show()

#  กำหนดพาธไฟล์ XDF ที่บันทึกจาก Lab Recorder
file_path = r'C:\users\s\Desktop\LSL_File\sub-24-3\ses-S001\eeg\sub-24-3_ses-S001_task-Default_run-001_eeg.xdf'

# โหลดไฟล์ XDF
streams, header = load_xdf_file(file_path)
if streams is None:
    exit()

# เลือก Stream ที่เป็น EEG
eeg_stream = find_eeg_stream(streams)
if eeg_stream is None:
    print(" ไม่พบ Stream EEG ในไฟล์ XDF")
    exit()

# เลือก Stream ที่เป็น Marker 
marker_stream = find_marker_stream(streams)
markers = np.array(marker_stream['time_stamps']) if marker_stream else []

# ดึงข้อมูล EEG และ timestamps
eeg_data = np.array(eeg_stream['time_series']).T  # (channels, samples)
timestamps = np.array(eeg_stream['time_stamps'])

# ตรวจสอบข้อมูล
if eeg_data.size == 0 or timestamps.size == 0:
    print(" ไม่มีข้อมูลใน Stream EEG")
    exit()

# บันทึกข้อมูล EEG เป็นไฟล์ .npy เพื่อนำไฟล์ไป plot แบบ Realtime ได้ 
np.save("eeg_data.npy", eeg_data)
np.save("timestamps.npy", timestamps)
print(f" บันทึกข้อมูลสำเร็จ EEG shape: {eeg_data.shape}, Timestamps shape: {timestamps.shape}")

# แสดงผลสัญญาณ EEG พร้อม Marker
plot_eeg_signal(timestamps, eeg_data, num_channels=24, time_window=10, markers=markers)
