
# Metadata เป็นการดึงข้อมูลจากอุปกรณ์
from pylsl import StreamInlet, resolve_streams

def get_stream_metadata():
    """ค้นหา streams และดึง metadata มาแสดงผล"""
    
    results = resolve_streams()

    if not results:
        print(" No streams found!")
        return

    print(f" Found {len(results)} stream(s).")

    inlet = StreamInlet(results[0])
    info = inlet.info()

    # แสดง XML metadata ทั้งหมด
    print("\n The stream's XML meta-data:")
    xml_data = info.as_xml()
    print(xml_data)  # พิมพ์ XML ทั้งหมด

    #  ดึงข้อมูลผู้ผลิต
    manufacturer = info.desc().child_value("manufacturer") if info.desc() else None
    print(f" Manufacturer: {manufacturer if manufacturer else ' Not found'}")

    # ดึงขนาดหมวก EEG
    cap_size = info.desc().child("cap").child_value("size") if info.desc().child("cap") else None
    print(f"Cap circumference: {cap_size if cap_size else ' Not found'}")

    # 📡 แสดงข้อมูลช่องสัญญาณ EEG
    print("\n📡 Channel labels:")
    channels = info.desc().child("channels") if info.desc() else None

    if channels:
        # ค้นหาช่องทั้งหมดภายใน XML
        channel_labels = []
        ch = channels.child("channel")
        while ch:
            label = ch.child_value("label")
            if label:
                channel_labels.append(label)
            ch = ch.next_sibling()

        if channel_labels:
            print("  " + ", ".join(channel_labels))
        else:
            print("⚠️ No channel labels found.")
    else:
        print("⚠️ No channel metadata found.")

if __name__ == '__main__':
    get_stream_metadata()
