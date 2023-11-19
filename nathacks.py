## IMPORTS ##
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations, NoiseEstimationLevelTypes, \
    AggOperations, WaveletTypes, WaveletExtensionTypes, ThresholdTypes, WaveletDenoisingTypes
from sklearn.svm import OneClassSVM
import numpy as np
import matplotlib.pyplot as plt
import time
## GRAPHING IMPORTS ##
import argparse
import logging
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import fftTest as FourierFT

#which is plotting? line 30 or lines in 80s?

def processData(cur_data):
    """ GET EEG Board Data """
    eeg_channels = board.get_eeg_channels(board_id)
    #print(eeg_channels)
    cur_eeg_data = cur_data[eeg_channels]
    #print(cur_eeg_data.shape)
    #print(cur_eeg_data)
    return cur_eeg_data


"""GRAPHING AND DATA COLLECTION"""
class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        #self.num_points = self.window_size * self.sampling_rate
        self.num_points = 250 #next thing: how do we limit range

        self.app = QtGui.QApplication([])  #this is the application from PyQt5
        #changed title
        self.win = pg.GraphicsWindow(title='FFT Plot', size=(800, 600))

        self._init_timeseries()

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        QtGui.QApplication.instance().exec_()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            p = self.win.addPlot(row=i, col=0)
            p.showAxis('left', True)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', True)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                #changed title
                p.setTitle('FFT Transform Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    #for changing the y-values
    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        for count, channel in enumerate(self.exg_channels):
            # collect timeseries
            ##filtering
            DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(data[channel], self.sampling_rate, 3.0, 45.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 48.0, 52.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 58.0, 62.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)

            # first of all you can try simple moving median or moving average with different window size
            if count == 0:
                DataFilter.perform_rolling_filter(data[channel], 3, AggOperations.MEAN.value)
            elif count == 1:
                DataFilter.perform_rolling_filter(data[channel], 3, AggOperations.MEDIAN.value)
            # if methods above dont work for your signal you can try wavelet based denoising
            # feel free to try different parameters
            else:
                DataFilter.perform_wavelet_denoising(data[channel], WaveletTypes.BIOR3_9, 3,
                                                    WaveletDenoisingTypes.SURESHRINK, ThresholdTypes.HARD,
                                                    WaveletExtensionTypes.SYMMETRIC, NoiseEstimationLevelTypes.FIRST_LEVEL)


            #DataFilter.perform_lowpass(data[channel], BoardShim.get_sampling_rate(board_id), 50, 5, FilterTypes.BUTTERWORTH, 1)
            #DataFilter.perform_highpass(data[channel], BoardShim.get_sampling_rate(board_id), 2.0, 4, FilterTypes.BUTTERWORTH, 0) 
            #print(fourierFT.getFFTdata(data[channel], BoardShim.get_sampling_rate(board_id)))
            #freq, data[channel], peakLocations = fourierFT.getFFTdata(data[channel], BoardShim.get_sampling_rate(board_id))
            self.curves[count].setData(data[channel].tolist())

        truePair = []
        for channel in self.exg_channels:
            self.curves[channel-1].setData(np.asarray(FourierFT.getFFTdata(data[channel], self.sampling_rate)))
            currentfreq = FourierFT.getFFTfreq(data[channel], self.sampling_rate)
            currentFFT = FourierFT.getFFTdata(data[channel], self.sampling_rate)
            pairing = dict(zip(currentfreq,currentFFT))
       
            #filtering peaks
            peaksHz = FourierFT.findPeaks(FourierFT.getFFTfreq(data[channel], self.sampling_rate), FourierFT.getFFTdata(data[channel], self.sampling_rate))     
            ourPeaksHz = []
            for entry in peaksHz:
                if entry < 50:
                    ourPeaksHz.append(entry)

            ourMagn = []
            for entry in currentfreq:
                if entry in ourPeaksHz:
                    ourMagn.append(pairing[entry])

            truePair.append(dict(zip(ourPeaksHz,ourMagn)))
            print(channel)
            print(dict(zip(ourPeaksHz,ourMagn)))
            """
            print(len(self.curves))
            print("this is data len: " + str(len(data)))
            print(channel)
            print(self.exg_channels)
        
            """
        """
        if train<=20:
            dataTrain.append(truePair)
        else:
            dataTest.append(truePair)

        train += 1
        """
        self.app.processEvents()  ##should be the "update"


if __name__ == "__main__":
    """ BOARD DECLARATION
    # will either use the connected board or will create a synthetic board #
    """
    params = BrainFlowInputParams()
    params.serial_port = 'COM15' # CHANGE THIS
    board_id = BoardIds.GANGLION_BOARD.value
    try:
        assert board_id == BoardIds.GANGLION_BOARD.value
        board = BoardShim(board_id, params)
        board.prepare_session()
        print("Successfully prepared physical board.")
    except Exception as e:
        print(e)
        #If the device cannot be found or is being used elsewhere, creates a synthetic board instead
        print("Device could not be found or is being used by another program, creating synthetic board.")
        board_id = BoardIds.SYNTHETIC_BOARD
        board = BoardShim(board_id, params)
        board.prepare_session()

    """ DATA COLLECTION AND GRAPHING """
    print("Starting Stream")
    board.start_stream()
    #train = 0
    #dataTrain = []
    #dataTest = []
    Graph(board)

    #newDataTrain = [[i] for i in dataTrain]
    #newDataTest = [[i] for i in dataTest]

    #Experimental ML for outliers/triggering responses
    #outliers = OneClassSVM(gamma='auto').fit(newDataTrain)
    #print(outliers.predict(newDataTest))
        
    #data = board.get_board_data() #all the board's data
    print("Ending Stream")
    board.stop_stream()
    board.release_session() # all data is colleted and removed from buffer
    # for data collection we could maybe use a loop ??
    # nothing else will run if we use an actual loop --> set parameters maybe\
