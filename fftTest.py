import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy import signal
from scipy.signal import argrelextrema

#replace this with our bci data
combined = []
samples_per_second = 12

fftData = np.fft.fft(combined)
#replace samples_per_second with sampling speed of board
freq = np.fft.fftfreq(len(combined))*samples_per_sec

fftData = fftData[0:int(len(fftData)/2)]
freq = freq[0:int(len(fftData)/2)]

magnitudeList = []
for entry in fftData:
    magnitudeList.append(abs(entry))
magnitude = np.array(magnitudeList)

if len(magnitude) == len(freq):
    pairing = dict(zip(magnitude, freq))


maxima = argrelextrema(magnitude, np.greater)
peaksHz = []
for entry in maxima:
    peaksHz.append(freq[entry])
    #print(str(magnitude[entry])+","+str(freq[entry]))

#accessing peaks
print(peaksHz)    
print(peaksHz[0][0])
print(peaksHz[0][1])

#print(str(len(fftData))+" "+str(len(freq)))

#OTHER CODE

"""
time = np.linspace(0, 0.5, 500)
samples_per_sec = 1000

amp_one, freq_one = 1.0, 10
amp_two, freq_two = 0.5, 35

sine_one = amp_one * np.sin(freq_one * 2 * np.pi * time)
sine_two = amp_two * np.sin(freq_two * 2 * np.pi * time)

combined = sine_one + sine_two
"""

"""
dict = {1:'a',2:'b',3:'c'}
array = [1,2,3]
print(array)
for entry in array:
    print(dict[entry])

compNum = [4+2j, 1+2j, 5+3j]
for entry in compNum:
    print(abs(entry))

compNum = [4+2j, 1+2j, 5+3j]
newArray = []
for entry in compNum:
    print(abs(entry))
    newArray.append(abs(entry))
print(newArray)    
"""
