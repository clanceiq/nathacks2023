## IMPORTS ##
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
import numpy as np
import matplotlib.pyplot as plt
import time
## GRAPHING IMPORTS ##
import argparse
import logging
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


def processData(cur_data):
    """ GET EEG Board Data """
    eeg_channels = board.get_eeg_channels(board_id)
    #print(eeg_channels)
    cur_eeg_data = cur_data[eeg_channels]
    #print(cur_eeg_data.shape)
    #print(cur_eeg_data)
    return cur_eeg_data

def passFiltering(cur_eeg_data):
    for channel in range(cur_eeg_data.shape[0]):
        DataFilter.perform_lowpass(cur_eeg_data[channel], BoardShim.get_sampling_rate(board_id), 50.0, 5, FilterTypes.BUTTERWORTH, 1)
        DataFilter.perform_highpass(cur_eeg_data[channel], BoardShim.get_sampling_rate(board_id), 2.0, 4, FilterTypes.BUTTERWORTH, 0)
    plt.plot(np.arange(cur_eeg_data.shape[1]), cur_eeg_data[0])
    return cur_eeg_data

def waveletTransform(cur_eeg_data):
    length_list = []
    wavelet_coeffs_list = []
    app_coefs_list = []
    detailed_coeffs_first_block_list = []
    for channel in range(cur_eeg_data.shape[0]):
        """ WAVELET TRANSFORM """
        #wavelet_coeffs, lengths = DataFilter.perform_wavelet_transform(cur_eeg_data[channel], "db1", 3)
        wavelet_coeffs, lengths = DataFilter.perform_wavelet_transform(cur_eeg_data[channel], 1, 3)

        app_coefs = wavelet_coeffs[0: lengths[0]] #approximation coefficients
        detailed_coeffs_first_block = wavelet_coeffs[lengths[0]: lengths[1]] # detailed coefficients
        length_list.append(lengths)
        wavelet_coeffs_list.append(wavelet_coeffs)
        app_coefs_list.append(app_coefs)
        detailed_coeffs_first_block_list.append(detailed_coeffs_first_block)
    return (wavelet_coeffs_list, length_list, app_coefs_list, detailed_coeffs_first_block_list)
    ## FIGURE OUT WAY TO PLOT THE WAVELET TRANSFORM TO USE VISUALIZE DATA ##
    ## FIGURE OUT HOW TO EXTRACT A NUMBER/FREQUENCY TO USE ##
    ## WHEN TESTING HEADSET, FIND IF THERE IS A CONSTANT FREQUENCY WHEN STIMULUS OCCURS ##

"""GRAPHING"""
class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot', size=(800, 600))

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
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                p.setTitle('TimeSeries Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)
        for count, channel in enumerate(self.exg_channels):
            # plot timeseries
            DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(data[channel], self.sampling_rate, 3.0, 45.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 48.0, 52.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 58.0, 62.0, 2,
                                        FilterTypes.BUTTERWORTH_ZERO_PHASE, 0)
            self.curves[count].setData(data[channel].tolist())

        self.app.processEvents()


if __name__ == "__main__":
    """ BOARD DECLARATION
    # will either use the connected board or will create a synthetic board #
    """
    params = BrainFlowInputParams()
    params.serial_port = 'COM5' # CHANGE THIS
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
    Graph(board)
    for i in range(5): # WILL MAYBE CHANGE THIS VALUE IF WE DONT WANT A DELAY?? #
        time.sleep(1)
        current_data = board.get_current_board_data(25) # adjust number of samples so that it doesn't overlap each loop
        current_eeg_data = processData(current_data)
        current_eeg_data = passFiltering(current_eeg_data)
        wavelet_coeffs, lengths, app_coeffs, detailed_coeffs_first_block = waveletTransform(current_eeg_data)
        print(app_coeffs)
    data = board.get_board_data()
    print("Ending Stream")
    board.stop_stream()
    board.release_session() # all data is colleted and removed from buffer
    # for data collection we could maybe use a loop ??
    # nothing else will run if we use an actual loop --> set parameters maybe\