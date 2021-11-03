import board
import busio
import adafruit_mpu6050
import math
import time
import matplotlib.pyplot as plt
from numpy import linspace, loadtxt, ones, convolve
import numpy as numpy
from scipy.signal  import find_peaks
from peakdetect import peakdetect
from gpiozero import Button
import RPi.GPIO as GPIO
from time import sleep, perf_counter    # perf_counter is more precise than time() for dt calculation\

# Setup
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN,pull_up_down=GPIO.PUD_UP)

# This function is used by us to help reduce some of the noise of our waveform
def interpolatedata(y_array, window_size):
    window = numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(y_array, window, 'same')

def getMag(x_data, y_data, z_data):
    #trans_z = z_data - 9.2
    mag = []
    for i in range(len(x_data)):
        mag.append(  math.sqrt( (x_data[i] ** 2) + (y_data[i] ** 2) + (z_data[i] ** 2) )  )
    return mag

# Used variables
stepcounter = 0;
time_data = []
x_data = []
y_data = []
z_data = []
start_time = time.time()

# Write a loop to poll each sensor and print its axis values
while True:
    if GPIO.input(5) == 0:
        sleep(0.5)
        while True:
            print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" %(mpu.acceleration))
            print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s" % (mpu.gyro))
            print("")
            time_data.append(time.time())
            x_data.append(mpu.acceleration[0])
            y_data.append(mpu.acceleration[1])
            z_data.append(mpu.acceleration[2]-9.2)
            sleep(0.1)
            if GPIO.input(5) == 0:
                break
        break

# Find magnitude of acceleration
mag_value = getMag(x_data, y_data, z_data)
plt.plot(time_data, mag_value, 'm')

# Find the peaks from the x acceleration and add it to stepcounter
# Find peaks
# Peaks of interpolated data
new_mag = interpolatedata(mag_value, 2)
peaks, _ = find_peaks(new_mag, prominence=0.3, distance=1)
peaks_time = []
peaks_value = []
for i in range(len(peaks)):
    peaks_time.append(time_data[peaks[i]])
    peaks_value.append(new_mag[peaks[i]]) # Previously z_data[peaks[i]] if you want to plot x's on raw data
plt.plot(peaks_time, peaks_value, "x")
stepcounter = str(len(peaks))
print("Steps: " + stepcounter)

# PLot
plt.plot(time_data, z_data, "b") # Raw Z
plt.plot(time_data, new_mag, "g") #Interpolated
plt.show()