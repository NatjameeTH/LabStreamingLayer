import pyxdf
import matplotlib.pyplot as plt

# โหลดไฟล์ XDF
filename = "C:\\Users\\BCILA\\Desktop\\LSL_File\\sub-P002\\ses-S001\\eeg\\sub-P002_ses-S001_task-Default_run-001_eeg.xdf"

# อ่านข้อมูลจากไฟล์ XDF
streams, header = pyxdf.load_xdf(filename)

# แสดงข้อมูลจากไฟล์
print("ข้อมูลไฟล์ XDF:")
print(f"Number of streams: {len(streams)}")
print(f"Stream names: {[stream['info']['name'][0] for stream in streams]}")

# เลือกข้อมูลจากสตรีมแรก (กรณีเลือก EEG stream)
eeg_stream = streams[1]  

# ดึงข้อมูลสัญญาณและเวลาจาก EEG stream
eeg_data = eeg_stream['time_series']
eeg_times = eeg_stream['time_stamps']

# ตรวจสอบข้อมูล
if len(eeg_data) == 0:
    print("ไม่มีข้อมูลในสตรีม EEG นี้")
else:
    print(f"Data from EEG stream: {eeg_data[:10]}...")  # แสดงข้อมูลบางส่วน

    # เลือก offset สำหรับการแบ่งช่วง
    offset_value = 10  # ค่า offset ที่จะเพิ่มให้กับแต่ละช่อง

    # Plot ข้อมูล EEG จากหลายช่อง
    plt.figure(figsize=(10, 6))

    # จำนวนช่องที่มีใน EEG
    num_channels = eeg_data.shape[1]

    # Plot แต่ละช่องโดยใช้ offset
    for i in range(num_channels):
        plt.plot(eeg_times, eeg_data[:, i] + i * offset_value, label=f"Channel {i + 1}")

    plt.title("EEG Signals with Offset")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (Shifted)")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
