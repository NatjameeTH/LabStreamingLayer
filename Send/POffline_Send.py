
#Plot sine graph และ Marker
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
    """ ค้นหา Stream ที่เป็น Marker หรือ Event """
    for stream in streams:
        if 'type' in stream['info'] and 'Markers' in stream['info']['type']:
            return stream
    return None

def plot_eeg_signal(timestamps, eeg_data, num_channels=4, offset=20, time_window=10, markers=None):
    """ พล็อตสัญญาณ EEG พร้อมการตั้งค่าขนาดและช่วงเวลา """
    if eeg_data.shape[1] < 2:
        print("มีข้อมูลไม่เพียงพอสำหรับพล็อต")
        return

    plt.figure(figsize=(30, 10))  
    plt.rcParams.update({'font.size': 14})  # ขยายตัวอักษรในกราฟ

    # พล็อต EEG signal
    for i in range(min(num_channels, eeg_data.shape[0])):
        plt.plot(timestamps, eeg_data[i, :] + i * offset, label=f'Channel {i+1}')

    # พล็อต marker event ทุกๆ 5 วินาที
    if markers is not None:
        first_marker = True  # ตัวแปรเพื่อเช็คว่าเจอ marker แรกแล้ว
        for marker in markers:
            # เช็คว่าเวลาเป็นช่วงที่ห่างกัน 5 วินาทีหรือไม่
            if first_marker or (marker % 5 == 0):  # เพิ่มเงื่อนไขว่า marker จะถูกแสดงทุกๆ 5 วินาที
                plt.axvline(x=marker, color='r', linestyle='-', label='Marker Event' if first_marker else "")
                first_marker = False  # ตั้งค่าหลังจากเจอ marker แรกแล้ว

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("EEG Signal with Markers")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.9)  # รูปแบบ grid ที่แสดงหลังกราฟ
    
    # กำหนดช่วงเวลาเริ่มต้นและเวลาแสดงผล (time_window)
    plt.xlim(timestamps[0], timestamps[0] + time_window)  # เริ่มต้นจาก timestamps[0] และแสดง time_window วินาทีแรก
    plt.show()


#  กำหนดพาธไฟล์ XDF ที่ได้จาก LSL LabRecorder
file_path = ("C:\\Users\\s\\Desktop\\LSL_File\\sub-25-2\\ses-S004\\eeg\\sub-25-2_ses-S004_task-Default_run-001_eeg.xdf")

#  โหลดไฟล์ XDF
streams, header = load_xdf_file(file_path)
if streams is None:
    exit()

#  เลือก Stream ที่เป็น EEG
eeg_stream = find_eeg_stream(streams)
if eeg_stream is None:
    print(" ไม่พบ Stream EEG ในไฟล์ XDF")
    exit()

#  เลือก Stream ที่เป็น Marker หรือ Event
marker_stream = find_marker_stream(streams)
if marker_stream is None:
    print(" ไม่พบ Stream Marker ในไฟล์ XDF")
    markers = []  # หากไม่มี marker
else:
    markers = np.array(marker_stream['time_stamps'])  # ดึงเวลา timestamp ของ marker

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
print(f" บันทึกข้อมูลสำเร็จ EEG shape: {eeg_data.shape}, Timestamps shape: {timestamps.shape}")

# 📈 แสดงผลสัญญาณ EEG พร้อม Marker
plot_eeg_signal(timestamps, eeg_data, num_channels=4, offset=2, time_window=10, markers=markers)
