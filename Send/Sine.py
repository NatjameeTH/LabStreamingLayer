
import numpy as np
import matplotlib.pyplot as plt

# กำหนดพารามิเตอร์
frequency = 1 # ความถี่ 1 Hz
sampling_rate = 500  # Hz 500 จุดต่อวิ
duration = 1  # ระยะเวลาในวินาที

# สร้างเวลา (second)
# 0 จุดเริ่มต้นของเวลา 
# duration จบที่เวลาเท่าไหร่?

t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# คำนวณ sine wave 
# np.sine เป็น fn ที่คำนวณค่า sine ของมุมในหน่วยเรเดียน.
# 2 π วงกลม
y = np.sin(2 * np.pi * frequency * t)

# สร้างกราฟ
plt.plot(t, y)
plt.title("Sine Wave (1 Hz)")
plt.xlabel("Times(s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()




"""

#Importing required library
import numpy as np
import matplotlib.pyplot as plt


# Creating x axis with range and y axis with Sine
# Function for Plotting Sine Graph
x = np.arange(0, 5*np.pi, 0.1)
y = np.sin(x)

# Plotting Sine Graph
plt.plot(x, y, color='green')
plt.show()

"""

