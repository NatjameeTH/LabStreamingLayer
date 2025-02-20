
#sendata ที่เป็น array และเป็นคลื่น sine
import sys
import getopt
import time
import math
from pylsl import StreamInfo, StreamOutlet, local_clock

def main(argv):
    srate = 512  # Sampling Rate (Hz)
    name = 'SineWaveSignal'
    type = 'EEG'
    n_channels = 4  # Number of channels
    frequency = 1  # ความถี่ของคลื่นไซน์ (Hz)
    

    help_string = 'SendData.py -s <sampling_rate> -c <channels> -n <stream_name> -t <stream_type> -f <frequency>'
    try:
        opts, args = getopt.getopt(argv, "hs:c:n:t:f:", longopts=["srate=", "channels=", "name=", "type=", "frequency="])
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-s", "--srate"):
            srate = float(arg)
        elif opt in ("-c", "--channels"):
            n_channels = int(arg)
        elif opt in ("-n", "--name"):
            name = str(arg)
        elif opt in ("-t", "--type"):
            type = str(arg)
        elif opt in ("-f", "--frequency"):
            frequency = float(arg)

    info = StreamInfo(name, type, n_channels, srate, 'float32', 'myuid22345')
    outlet = StreamOutlet(info)

    print("Now sending sine wave data...")



    #elapsed_time เวลาที่ผ่านไป (วินาที)
    #required_samples จำนวนตัวอย่างที่ส่ง
    #srate (Sampling Rate)
    start_time = local_clock()
    sent_samples = 0
    try: #เพื่อให้KeyboardInterrupt: ทำงานใน loop นี้
        while True:
            elapsed_time = local_clock() - start_time
            required_samples = int(srate * elapsed_time) - sent_samples
            print(f"Elapsed Time: {elapsed_time:.3f} sec, Required Samples: {required_samples}")

            for i in range(required_samples):
                t = (sent_samples + i) / srate  # คำนวณเวลา t

               
                # สร้างคลื่นไซน์ 4 ช่อง (ทุกช่องจะมีเฟสเหมือนกัน) ไม่เหลือมกัน
                mysample = [math.sin(2 * math.pi * frequency * t) for ch in range(n_channels)]

                print(f"Sent Data: {mysample}")  # แสดงข้อมูลที่ส่งออก
                outlet.push_sample(mysample)

            sent_samples += required_samples
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Saving data...")

if __name__ == '__main__':
    main(sys.argv[1:])



