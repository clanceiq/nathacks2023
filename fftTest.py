import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy import signal
from scipy.signal import argrelextrema

import matplotlib.pyplot as plt

#converts dataArray (transformed from filtering) into a
#"pairing" dictionary with the magnitude and frequency
def getFFTdata(dataArray, samplingRate):
    fftData = np.fft.fft(dataArray)
    freq = np.fft.fftfreq(len(dataArray))*samplingRate
    #gather frequencies given the sampling rate and the amount of data collected

    fftData = fftData[1:int(len(fftData)/2)]
    freq = freq[1:int(len(freq)/2)]
    #fftData = fftData[0:249]
    #freq = freq[0:249]

    #get magnitudes
    magnitude = []
    for entry in fftData:
        magnitude.append(abs(entry))

    #magnitude = magnitude[0].tolist() #convert from a numpy array
    
    return magnitude

def getFFTfreq(dataArray, samplingRate):
    freq = np.fft.fftfreq(len(dataArray))*samplingRate
    freq = freq[1:int(len(freq)/2)]

    
    return freq

def findPeaks(freq, magnitude):
    if len(magnitude) == len(freq):
        pairing = dict(zip(magnitude, freq))
    
    magnitude = np.asarray(magnitude)
    maxima = argrelextrema(magnitude, np.greater)
    peaksHz = []
    #how do we not make this an embedded array?
    for entry in maxima:
        peaksHz.append(freq[entry])
        peaksHz = peaksHz[0].tolist()
    #print(str(magnitude[entry])+","+str(freq[entry]))
    return peaksHz


    
#accessing peaks
"""
print(peaksHz)    
print(peaksHz[0][0])
print(peaksHz[0][1])
"""

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

freq, magnitude = getFFTdata(combined, samples_per_sec)
print(freq)
print(len(freq))
print(magnitude)
print(len(magnitude))
peaks = findPeaks(freq, magnitude)
print(peaks)
"""
#plt.plot(freq, magnitudeList)
#plt.show()


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
